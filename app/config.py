"""Application settings from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ServiceNow PDI
    SNOW_INSTANCE_URL: str = "https://devXXXXX.service-now.com"
    SNOW_USERNAME: str = "admin"
    SNOW_PASSWORD: str = ""

    # Dell Cyber Recovery
    DELLCR_MODE: str = "mock"  # "mock" or "live"
    DELLCR_BASE_URL: str = "http://localhost:14778"
    DELLCR_USERNAME: str = "crso"
    DELLCR_PASSWORD: str = ""

    # Snowflake
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_DATABASE: str = "CYBER_SECURITY"
    SNOWFLAKE_SCHEMA: str = "SIEM"
    SNOWFLAKE_WAREHOUSE: str = "CYBER_WH"

    # Databricks
    DATABRICKS_HOST: str = ""  # e.g. "dbc-9a9a2925-5ad0.cloud.databricks.com"
    DATABRICKS_TOKEN: str = ""

    # App
    APP_PORT: int = 8889

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
