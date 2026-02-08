"""Load AI Factory host data into Snowflake CYBER_SECURITY.SIEM tables.

Uses the same credentials from .env that the app uses.
Run from project root:  python3 scripts/load_snowflake_ai_factory.py
"""

import sys
from pathlib import Path

# Add project root so we can import app.config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import snowflake.connector
from app.config import settings


def main():
    print(f"Connecting to Snowflake account: {settings.SNOWFLAKE_ACCOUNT}")
    conn = snowflake.connector.connect(
        account=settings.SNOWFLAKE_ACCOUNT,
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
    )
    cur = conn.cursor()

    # Read and execute the SQL file, splitting on semicolons
    sql_file = Path(__file__).resolve().parent / "snowflake_ai_factory.sql"
    sql_text = sql_file.read_text()

    # Split into individual statements, skip empty/comment-only ones
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]

    success = 0
    errors = 0
    for stmt in statements:
        # Skip pure comment blocks
        lines = [l for l in stmt.splitlines() if not l.strip().startswith("--")]
        if not any(l.strip() for l in lines):
            continue
        try:
            cur.execute(stmt)
            rows = cur.fetchone()
            desc = stmt.strip().splitlines()[0][:80]
            # For non-comment first lines, find the actual SQL keyword
            for line in stmt.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("--"):
                    desc = stripped[:80]
                    break
            print(f"  OK: {desc}")
            success += 1
        except Exception as e:
            # Extract first meaningful SQL line for error context
            desc = "unknown"
            for line in stmt.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("--"):
                    desc = stripped[:60]
                    break
            print(f"  ERROR on [{desc}]: {e}")
            errors += 1

    conn.close()
    print(f"\nDone: {success} statements OK, {errors} errors")


if __name__ == "__main__":
    main()
