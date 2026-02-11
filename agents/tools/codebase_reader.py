"""Codebase reader tool — reads source files for the Documentalist agent.

Provides access to all project source files so the Documentalist can
generate accurate architecture docs, API references, and component descriptions.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Directories to scan for source files
SOURCE_DIRS = {
    "app": PROJECT_ROOT / "app",
    "agents": PROJECT_ROOT / "agents",
    "mock_dellcr": PROJECT_ROOT / "mock_dellcr",
    "scripts": PROJECT_ROOT / "scripts",
    "static/js": PROJECT_ROOT / "static" / "js",
    "templates": PROJECT_ROOT / "templates",
}


CODEBASE_LIST_TOOL = {
    "name": "list_source_files",
    "description": (
        "List all source files in the CyberDemo project. "
        "Returns file paths grouped by directory. Use this first to understand "
        "the project structure before reading specific files."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Filter to a specific directory: app, agents, mock_dellcr, scripts, static/js, templates. Leave empty for all.",
                "default": "",
            },
        },
    },
}

CODEBASE_READ_TOOL = {
    "name": "read_source_file",
    "description": (
        "Read a source file from the CyberDemo project. "
        "Provide a relative path from the project root (e.g. 'app/main.py'). "
        "Returns the full file content."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative path from project root (e.g. 'app/main.py', 'agents/base.py')",
            },
        },
        "required": ["path"],
    },
}


async def handle_list_source_files(input: dict) -> str:
    """List source files, optionally filtered by directory."""
    target_dir = input.get("directory", "")
    extensions = {".py", ".js", ".html", ".sql", ".css", ".json", ".md"}

    lines = []
    dirs_to_scan = (
        {target_dir: SOURCE_DIRS[target_dir]} if target_dir in SOURCE_DIRS
        else SOURCE_DIRS
    )

    for name, path in sorted(dirs_to_scan.items()):
        if not path.exists():
            continue
        files = sorted(
            f for f in path.rglob("*")
            if f.is_file() and f.suffix in extensions and "__pycache__" not in str(f)
        )
        if files:
            lines.append(f"\n## {name}/")
            for f in files:
                rel = f.relative_to(PROJECT_ROOT)
                size = f.stat().st_size
                lines.append(f"  {rel} ({size} bytes)")

    return "\n".join(lines) if lines else "No source files found."


async def handle_read_source_file(input: dict) -> str:
    """Read a source file by relative path."""
    rel_path = input["path"]
    full_path = PROJECT_ROOT / rel_path

    if not full_path.exists():
        return f"File not found: {rel_path}"

    if not full_path.is_file():
        return f"Not a file: {rel_path}"

    # Security: ensure the path stays within the project
    try:
        full_path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return f"Access denied: path outside project root"

    content = full_path.read_text(encoding="utf-8")
    if len(content) > 30000:
        content = content[:30000] + "\n\n... (truncated)"

    return content
