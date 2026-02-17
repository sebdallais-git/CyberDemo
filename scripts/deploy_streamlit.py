"""Deploy the SIEM Threat Detection Streamlit app to Snowflake.

Creates a stage, uploads the app file, and creates the Streamlit app.
After deployment, prints the app URL.

Usage:
    python scripts/deploy_streamlit.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import snowflake.connector
from app.config import settings

SCRIPTS_DIR = Path(__file__).resolve().parent
APP_FILE = SCRIPTS_DIR / "streamlit_siem.py"


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

    # Create internal stage for the Streamlit app files
    print("Creating stage STREAMLIT_STAGE...")
    cur.execute("CREATE STAGE IF NOT EXISTS STREAMLIT_STAGE")

    # Upload the app file
    print(f"Uploading {APP_FILE.name} to @STREAMLIT_STAGE...")
    cur.execute(
        f"PUT 'file://{APP_FILE}' @STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
    )

    # Create (or replace) the Streamlit app
    print("Creating Streamlit app SIEM_THREAT_DASHBOARD...")
    cur.execute("""
        CREATE OR REPLACE STREAMLIT SIEM_THREAT_DASHBOARD
            ROOT_LOCATION = '@CYBER_SECURITY.SIEM.STREAMLIT_STAGE'
            MAIN_FILE = 'streamlit_siem.py'
            QUERY_WAREHOUSE = 'CYBER_WH'
            TITLE = 'SIEM Threat Detection'
    """)

    # Get the app URL
    # Snowflake Streamlit apps are at:
    # https://app.snowflake.com/<locator>/#/streamlit-apps/<DB>.<SCHEMA>.<APP_NAME>
    cur.execute("SELECT CURRENT_ORGANIZATION_NAME(), CURRENT_ACCOUNT_NAME()")
    row = cur.fetchone()
    org_name = row[0]
    acct_name = row[1]

    app_url = (
        f"https://app.snowflake.com/{org_name}-{acct_name}/"
        f"#/streamlit-apps/CYBER_SECURITY.SIEM.SIEM_THREAT_DASHBOARD"
    )

    conn.close()

    print(f"\nDeployment complete!")
    print(f"App URL: {app_url}")
    print(f"\nSet this in your .env to use it during demos:")
    print(f"  SNOWFLAKE_WORKSHEET_URL={app_url}")


if __name__ == "__main__":
    main()
