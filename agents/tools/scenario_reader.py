"""Scenario reader tool — loads existing scenarios as structural reference.

Allows agents (especially Scenarist) to read existing scenario files
to understand the expected format and structure.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Directories containing scenario reference material
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
MOCK_DIR = PROJECT_ROOT / "mock_dellcr"
APP_DIR = PROJECT_ROOT / "app"
STATIC_DIR = PROJECT_ROOT / "static" / "js"


SCENARIO_READER_TOOL = {
    "name": "read_scenario",
    "description": (
        "Read an existing scenario file for structural reference. "
        "Available files:\n"
        "- 'snowflake_ransomware.sql' — Snowflake SIEM data for ransomware scenario\n"
        "- 'snowflake_ai_factory.sql' — Snowflake SIEM data for AI factory scenario\n"
        "- 'snowflake_data_exfil.sql' — Snowflake SIEM data for data exfil scenario\n"
        "- 'snowflake_schema.sql' — Snowflake table definitions\n"
        "- 'orchestrator.py' — Orchestrator with scenario details and step definitions\n"
        "- 'app.js' — Frontend with attack sequences and UI state\n"
        "- 'models.py' — Pydantic models (ScenarioType, SSEEvent, etc.)\n"
        "Use these as templates when generating new scenarios."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Name of the file to read (e.g. 'snowflake_ransomware.sql')",
            },
        },
        "required": ["filename"],
    },
}

# Map of readable files to their paths
_FILE_MAP = {
    "snowflake_ransomware.sql": SCRIPTS_DIR / "snowflake_ransomware.sql",
    "snowflake_ai_factory.sql": SCRIPTS_DIR / "snowflake_ai_factory.sql",
    "snowflake_data_exfil.sql": SCRIPTS_DIR / "snowflake_data_exfil.sql",
    "snowflake_schema.sql": SCRIPTS_DIR / "snowflake_schema.sql",
    "orchestrator.py": APP_DIR / "orchestrator.py",
    "app.js": STATIC_DIR / "app.js",
    "models.py": APP_DIR / "models.py",
}


async def handle_read_scenario(input: dict) -> str:
    """Read a scenario reference file and return its contents."""
    filename = input["filename"]
    path = _FILE_MAP.get(filename)

    if not path:
        available = ", ".join(sorted(_FILE_MAP.keys()))
        return f"Unknown file: {filename}. Available: {available}"

    if not path.exists():
        return f"File not found: {path}"

    content = path.read_text(encoding="utf-8")
    # Truncate very large files to stay within tool result limits
    if len(content) > 30000:
        content = content[:30000] + "\n\n... (truncated)"
    return content
