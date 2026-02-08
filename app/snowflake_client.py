"""Snowflake client for querying CYBER_SECURITY SIEM data.

Runs anomaly detection queries against network events, endpoint events,
and ML anomaly scores to detect threats in real time.
"""

import logging
from pathlib import Path
from typing import Any

import snowflake.connector

from app.config import settings

# Directory containing per-scenario SQL data files
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

# Map scenario name → SQL file with INSERT statements
SCENARIO_SQL_FILES = {
    "ransomware": "snowflake_ransomware.sql",
    "ai_factory": "snowflake_ai_factory.sql",
    "data_exfil": "snowflake_data_exfil.sql",
}

logger = logging.getLogger(__name__)

# Anomaly detection query — finds hosts with critical/high anomaly scores
# and correlates with endpoint detections and suspicious network activity
ANOMALY_DETECTION_SQL = """
WITH anomalies AS (
    SELECT
        entity_name AS hostname,
        entity_ip AS ip,
        current_score AS threat_score,
        anomaly_label,
        contributing_factors
    FROM ANOMALY_SCORES
    WHERE anomaly_label IN ('CRITICAL_ANOMALY', 'HIGH_ANOMALY')
    ORDER BY current_score DESC
),
malicious_endpoints AS (
    SELECT
        hostname,
        COUNT(*) AS detection_count,
        MAX(risk_score) AS max_risk,
        ARRAY_AGG(DISTINCT detection_name) AS detections
    FROM ENDPOINT_EVENTS
    WHERE severity IN ('CRITICAL', 'HIGH')
    GROUP BY hostname
),
suspicious_network AS (
    SELECT
        source_host AS hostname,
        COUNT(*) AS suspicious_connections,
        COUNT(DISTINCT dest_ip) AS unique_destinations,
        SUM(bytes_sent) AS total_bytes_out
    FROM NETWORK_EVENTS
    WHERE dest_port = 445 OR geo_country != 'CH'
    GROUP BY source_host
    HAVING suspicious_connections > 10
)
SELECT
    a.hostname,
    a.ip,
    a.threat_score,
    a.anomaly_label,
    a.contributing_factors,
    COALESCE(e.detection_count, 0) AS endpoint_detections,
    COALESCE(e.max_risk, 0) AS max_endpoint_risk,
    e.detections AS endpoint_detection_names,
    COALESCE(n.suspicious_connections, 0) AS suspicious_net_connections,
    COALESCE(n.total_bytes_out, 0) AS total_bytes_exfil
FROM anomalies a
LEFT JOIN malicious_endpoints e ON a.hostname = e.hostname
LEFT JOIN suspicious_network n ON a.hostname = n.hostname
ORDER BY a.threat_score DESC
"""

# Quick count of critical events in the last window
EVENT_SUMMARY_SQL = """
SELECT
    (SELECT COUNT(*) FROM NETWORK_EVENTS) AS total_network_events,
    (SELECT COUNT(*) FROM ENDPOINT_EVENTS) AS total_endpoint_events,
    (SELECT COUNT(*) FROM ENDPOINT_EVENTS WHERE severity = 'CRITICAL') AS critical_detections,
    (SELECT COUNT(*) FROM NETWORK_EVENTS WHERE geo_country != 'CH') AS outbound_foreign,
    (SELECT COUNT(DISTINCT source_host) FROM NETWORK_EVENTS WHERE dest_port = 445) AS smb_sources
"""


class SnowflakeClient:
    """Client for Snowflake CYBER_SECURITY database queries."""

    def _connect(self):
        return snowflake.connector.connect(
            account=settings.SNOWFLAKE_ACCOUNT,
            user=settings.SNOWFLAKE_USER,
            password=settings.SNOWFLAKE_PASSWORD,
            database=settings.SNOWFLAKE_DATABASE,
            schema=settings.SNOWFLAKE_SCHEMA,
            warehouse=settings.SNOWFLAKE_WAREHOUSE,
        )

    async def is_available(self) -> bool:
        """Check if Snowflake is reachable."""
        try:
            conn = self._connect()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    async def swap_scenario_data(self, scenario: str) -> bool:
        """Replace SIEM table contents with scenario-specific data.

        TRUNCATEs all 3 tables then runs the scenario's SQL INSERT file.
        Called at the start of Step 1 (DETECT) so queries return relevant hosts.
        """
        sql_file_name = SCENARIO_SQL_FILES.get(scenario)
        if not sql_file_name:
            logger.warning(f"No Snowflake data file for scenario '{scenario}', skipping swap")
            return False

        sql_path = SCRIPTS_DIR / sql_file_name
        if not sql_path.exists():
            logger.warning(f"SQL file not found: {sql_path}")
            return False

        try:
            conn = self._connect()
            cur = conn.cursor()

            # Wipe existing data so each scenario starts clean
            for table in ("ANOMALY_SCORES", "ENDPOINT_EVENTS", "NETWORK_EVENTS"):
                cur.execute(f"TRUNCATE TABLE IF EXISTS {table}")

            # Execute the scenario's INSERT statements
            sql_text = sql_path.read_text()
            statements = [s.strip() for s in sql_text.split(";") if s.strip()]
            executed = 0
            for stmt in statements:
                # Skip pure comments and USE statements (already connected to DB/schema)
                lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
                meaningful = [l for l in lines if l.strip()]
                if not meaningful:
                    continue
                first_keyword = meaningful[0].strip().split()[0].upper()
                if first_keyword in ("USE",):
                    continue
                cur.execute(stmt)
                executed += 1

            conn.close()
            logger.info(f"Snowflake data swapped to '{scenario}' ({executed} statements)")
            return True

        except Exception as e:
            logger.error(f"Snowflake data swap error: {e}")
            return False

    async def run_anomaly_detection(self) -> dict:
        """Run the anomaly detection query and return structured results.

        This is the "AI detection" step — queries ML anomaly scores
        correlated with endpoint and network events.
        """
        try:
            conn = self._connect()
            cur = conn.cursor(snowflake.connector.DictCursor)

            # Get event summary first
            cur.execute(EVENT_SUMMARY_SQL)
            summary_row = cur.fetchone()
            summary = {
                "total_network_events": summary_row["TOTAL_NETWORK_EVENTS"],
                "total_endpoint_events": summary_row["TOTAL_ENDPOINT_EVENTS"],
                "critical_detections": summary_row["CRITICAL_DETECTIONS"],
                "outbound_foreign": summary_row["OUTBOUND_FOREIGN"],
                "smb_sources": summary_row["SMB_SOURCES"],
            }

            # Run anomaly detection
            cur.execute(ANOMALY_DETECTION_SQL)
            rows = cur.fetchall()

            threats = []
            for row in rows:
                # Parse contributing_factors from Snowflake VARIANT (comes as JSON string)
                factors = row["CONTRIBUTING_FACTORS"]
                if isinstance(factors, str):
                    import json
                    factors = json.loads(factors)

                threats.append({
                    "hostname": row["HOSTNAME"],
                    "ip": row["IP"],
                    "threat_score": float(row["THREAT_SCORE"]),
                    "anomaly_label": row["ANOMALY_LABEL"],
                    "contributing_factors": factors,
                    "endpoint_detections": row["ENDPOINT_DETECTIONS"],
                    "max_endpoint_risk": float(row["MAX_ENDPOINT_RISK"]),
                    "suspicious_net_connections": row["SUSPICIOUS_NET_CONNECTIONS"],
                    "total_bytes_exfil": row["TOTAL_BYTES_EXFIL"],
                })

            conn.close()

            # Determine overall verdict
            max_score = max((t["threat_score"] for t in threats), default=0)
            primary_threat = threats[0] if threats else None

            return {
                "status": "THREAT_DETECTED" if max_score > 8.0 else "ANOMALY_DETECTED" if threats else "CLEAR",
                "summary": summary,
                "threat_count": len(threats),
                "max_threat_score": max_score,
                "primary_host": primary_threat["hostname"] if primary_threat else None,
                "primary_factors": primary_threat["contributing_factors"] if primary_threat else {},
                "threats": threats,
                "query_engine": "Snowflake AI/ML Anomaly Detection",
                "model_version": "sf-anomaly-v3.2",
            }

        except Exception as e:
            logger.error(f"Snowflake anomaly detection error: {e}")
            raise


# Singleton
snowflake_client = SnowflakeClient()
