"""Unified Snowflake setup: create schema and load scenario data.

Usage (run from project root):
    python scripts/setup_snowflake.py                     # Schema + ransomware data
    python scripts/setup_snowflake.py --schema-only        # Just create tables
    python scripts/setup_snowflake.py --scenario ai_factory
    python scripts/setup_snowflake.py --scenario data_exfil
"""

import argparse
import sys
from pathlib import Path

# Add project root so we can import app.config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import snowflake.connector
from app.config import settings

SCRIPTS_DIR = Path(__file__).resolve().parent

SCENARIO_FILES = {
    "ransomware": "snowflake_ransomware.sql",
    "ai_factory": "snowflake_ai_factory.sql",
    "data_exfil": "snowflake_data_exfil.sql",
}


def run_sql_file(conn, sql_path: Path, skip_use: bool = False):
    """Execute all statements in a SQL file, printing progress."""
    print(f"\n── Executing {sql_path.name} ──")
    sql_text = sql_path.read_text()
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]

    cur = conn.cursor()
    ok, errors = 0, 0
    for stmt in statements:
        # Skip pure comment blocks
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
        meaningful = [l for l in lines if l.strip()]
        if not meaningful:
            continue

        # Optionally skip USE statements (when loading data, already connected)
        first_keyword = meaningful[0].strip().split()[0].upper()
        if skip_use and first_keyword == "USE":
            continue

        try:
            cur.execute(stmt)
            # Show first meaningful SQL line as progress
            desc = meaningful[0].strip()[:80]
            print(f"  OK: {desc}")
            ok += 1
        except Exception as e:
            desc = meaningful[0].strip()[:60] if meaningful else "unknown"
            print(f"  ERROR [{desc}]: {e}")
            errors += 1

    print(f"  Result: {ok} OK, {errors} errors")
    return errors == 0


def main():
    parser = argparse.ArgumentParser(description="Setup Snowflake CYBER_SECURITY schema and load scenario data")
    parser.add_argument("--schema-only", action="store_true", help="Only create schema/tables, don't load data")
    parser.add_argument("--scenario", choices=list(SCENARIO_FILES.keys()), default="ransomware",
                        help="Which scenario data to load (default: ransomware)")
    args = parser.parse_args()

    print(f"Connecting to Snowflake account: {settings.SNOWFLAKE_ACCOUNT}")
    conn = snowflake.connector.connect(
        account=settings.SNOWFLAKE_ACCOUNT,
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
    )

    # Always run schema DDL first
    schema_ok = run_sql_file(conn, SCRIPTS_DIR / "snowflake_schema.sql")
    if not schema_ok:
        print("\nSchema creation had errors — check output above")

    if args.schema_only:
        conn.close()
        print("\nDone (schema only)")
        return

    # Re-connect with database/schema/warehouse now that they exist
    conn.close()
    conn = snowflake.connector.connect(
        account=settings.SNOWFLAKE_ACCOUNT,
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
    )

    # Truncate tables before loading
    cur = conn.cursor()
    for table in ("ANOMALY_SCORES", "ENDPOINT_EVENTS", "NETWORK_EVENTS"):
        cur.execute(f"TRUNCATE TABLE IF EXISTS {table}")
        print(f"  Truncated {table}")

    # Load scenario data
    sql_file = SCRIPTS_DIR / SCENARIO_FILES[args.scenario]
    data_ok = run_sql_file(conn, sql_file, skip_use=True)

    conn.close()
    status = "OK" if data_ok else "completed with errors"
    print(f"\nDone: schema + {args.scenario} data ({status})")


if __name__ == "__main__":
    main()
