"""Snowflake Streamlit app — SIEM Threat Detection Dashboard.

Runs natively inside Snowflake on app.snowflake.com.
Queries CYBER_SECURITY.SIEM tables live on every page load,
so it always shows the current scenario's data.
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="SIEM Threat Detection", layout="wide")

session = get_active_session()

# ── Queries ──────────────────────────────────────────────────

ANOMALY_DETECTION_SQL = """
WITH anomalies AS (
    SELECT entity_name AS hostname, entity_ip AS ip,
           current_score AS threat_score, anomaly_label, contributing_factors
    FROM ANOMALY_SCORES
    WHERE anomaly_label IN ('CRITICAL_ANOMALY', 'HIGH_ANOMALY')
    ORDER BY current_score DESC
),
malicious_endpoints AS (
    SELECT hostname, COUNT(*) AS detection_count, MAX(risk_score) AS max_risk,
           ARRAY_AGG(DISTINCT detection_name) AS detections
    FROM ENDPOINT_EVENTS WHERE severity IN ('CRITICAL', 'HIGH')
    GROUP BY hostname
),
suspicious_network AS (
    SELECT source_host AS hostname, COUNT(*) AS suspicious_connections,
           COUNT(DISTINCT dest_ip) AS unique_destinations,
           SUM(bytes_sent) AS total_bytes_out
    FROM NETWORK_EVENTS
    WHERE dest_port = 445 OR geo_country != 'CH'
    GROUP BY source_host
    HAVING suspicious_connections > 2
)
SELECT a.hostname, a.ip, a.threat_score, a.anomaly_label,
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

# ── Header ───────────────────────────────────────────────────

st.markdown("## :snowflake: CYBER_SECURITY.SIEM — Threat Detection")

# ── Load data ────────────────────────────────────────────────

detection_df = session.sql(ANOMALY_DETECTION_SQL).to_pandas()
anomaly_df = session.sql("SELECT * FROM ANOMALY_SCORES ORDER BY CURRENT_SCORE DESC").to_pandas()
endpoint_df = session.sql("SELECT * FROM ENDPOINT_EVENTS ORDER BY RISK_SCORE DESC, EVENT_TIME DESC").to_pandas()
network_df = session.sql("SELECT * FROM NETWORK_EVENTS ORDER BY BYTES_SENT DESC LIMIT 30").to_pandas()
databricks_df = session.sql("SELECT * FROM DATABRICKS_API_EVENTS ORDER BY EVENT_TIME ASC").to_pandas()

# ── Summary metrics ──────────────────────────────────────────

max_score = float(detection_df["THREAT_SCORE"].max()) if not detection_df.empty else 0
critical_count = int((anomaly_df["ANOMALY_LABEL"] == "CRITICAL_ANOMALY").sum()) if not anomaly_df.empty else 0
total_endpoints = len(endpoint_df)
total_network = len(network_df)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Max Threat Score", f"{max_score:.2f} / 10")
c2.metric("Anomalous Hosts", len(detection_df))
c3.metric("Critical Anomalies", critical_count)
c4.metric("Endpoint Detections", total_endpoints)
c5.metric("Network Flows", total_network)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────

tab_names = [
    f"Detection Results ({len(detection_df)})",
    f"Anomaly Scores ({len(anomaly_df)})",
    f"Endpoint Events ({len(endpoint_df)})",
    f"Network Events ({len(network_df)})",
    f"Databricks API ({len(databricks_df)})",
]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_names)

with tab1:
    with st.expander("Show SQL"):
        st.code(ANOMALY_DETECTION_SQL, language="sql")
    if detection_df.empty:
        st.info("No anomalies detected.")
    else:
        # Show key columns in a clean table
        display_cols = ["HOSTNAME", "IP", "THREAT_SCORE", "ANOMALY_LABEL",
                        "ENDPOINT_DETECTIONS", "MAX_ENDPOINT_RISK",
                        "SUSPICIOUS_NET_CONNECTIONS", "TOTAL_BYTES_EXFIL"]
        cols_present = [c for c in display_cols if c in detection_df.columns]
        st.dataframe(detection_df[cols_present], use_container_width=True)

with tab2:
    with st.expander("Show SQL"):
        st.code("SELECT * FROM ANOMALY_SCORES ORDER BY CURRENT_SCORE DESC", language="sql")
    if anomaly_df.empty:
        st.info("No anomaly scores.")
    else:
        display_cols = ["ENTITY_NAME", "ENTITY_IP", "ENTITY_TYPE", "CURRENT_SCORE",
                        "BASELINE_SCORE", "ANOMALY_DELTA", "ANOMALY_LABEL", "MODEL_VERSION"]
        cols_present = [c for c in display_cols if c in anomaly_df.columns]
        st.dataframe(anomaly_df[cols_present], use_container_width=True)

with tab3:
    with st.expander("Show SQL"):
        st.code("SELECT * FROM ENDPOINT_EVENTS ORDER BY RISK_SCORE DESC, EVENT_TIME DESC", language="sql")
    if endpoint_df.empty:
        st.info("No endpoint events.")
    else:
        display_cols = ["HOSTNAME", "EVENT_TYPE", "SEVERITY", "DETECTION_NAME",
                        "RISK_SCORE", "PROCESS_NAME", "FILE_PATH"]
        cols_present = [c for c in display_cols if c in endpoint_df.columns]
        st.dataframe(endpoint_df[cols_present], use_container_width=True)

with tab4:
    with st.expander("Show SQL"):
        st.code("SELECT * FROM NETWORK_EVENTS ORDER BY BYTES_SENT DESC LIMIT 30", language="sql")
    if network_df.empty:
        st.info("No network events.")
    else:
        display_cols = ["SOURCE_HOST", "SOURCE_IP", "DEST_IP", "DEST_PORT",
                        "PROTOCOL", "BYTES_SENT", "BYTES_RECEIVED", "GEO_COUNTRY"]
        cols_present = [c for c in display_cols if c in network_df.columns]
        st.dataframe(network_df[cols_present], use_container_width=True)

with tab5:
    with st.expander("Show SQL"):
        st.code("SELECT * FROM DATABRICKS_API_EVENTS ORDER BY EVENT_TIME ASC", language="sql")
    if databricks_df.empty:
        st.info("No Databricks API events (only populated for AI Factory scenario).")
    else:
        display_cols = ["EVENT_TIME", "SERVICE_PRINCIPAL", "API_ENDPOINT", "HTTP_METHOD",
                        "STATUS_CODE", "RESPONSE_BYTES", "SOURCE_IP", "CATALOG_NAME",
                        "TABLES_ACCESSED", "IS_ANOMALOUS"]
        cols_present = [c for c in display_cols if c in databricks_df.columns]
        st.dataframe(databricks_df[cols_present], use_container_width=True)

# ── Footer ───────────────────────────────────────────────────

st.divider()
st.caption("Snowflake AI/ML Anomaly Detection Engine v3.2 — CYBER_SECURITY.SIEM — Live query on page load")
