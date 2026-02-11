"""File writer tool — saves agent output to agents/output/.

Provides the tool definition and handler for Claude tool calling.
"""

from pathlib import Path

from agents.base import OUTPUT_DIR


# Tool definition (Anthropic format)
FILE_WRITER_TOOL = {
    "name": "write_file",
    "description": (
        "Write content to a file in the output directory. "
        "Use this to save generated artifacts (SQL, JSON, Markdown, HTML). "
        "The path is relative to the output directory."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path within the output directory (e.g. 'scenarios/supply_chain/snowflake.sql')",
            },
            "content": {
                "type": "string",
                "description": "File content to write",
            },
        },
        "required": ["path", "content"],
    },
}


async def handle_write_file(input: dict) -> str:
    """Write content to a file in the output directory."""
    rel_path = input["path"]
    content = input["content"]

    target = OUTPUT_DIR / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"Written {len(content)} bytes to {rel_path}"
