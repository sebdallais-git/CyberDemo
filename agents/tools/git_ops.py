"""Git operations tool — allows agents to stage, commit, and check status.

Used by the Documentalist agent to commit generated docs to the repo.
"""

import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


GIT_STATUS_TOOL = {
    "name": "git_status",
    "description": "Show the current git status — staged, unstaged, and untracked files.",
    "input_schema": {
        "type": "object",
        "properties": {},
    },
}

GIT_ADD_TOOL = {
    "name": "git_add",
    "description": (
        "Stage files for commit. Provide specific file paths relative to the project root. "
        "Use '.' to stage all changes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File paths to stage (e.g. ['agents/output/docs/architecture.md']). Use ['.'] for all.",
            },
        },
        "required": ["paths"],
    },
}

GIT_COMMIT_TOOL = {
    "name": "git_commit",
    "description": "Create a git commit with the staged changes.",
    "input_schema": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Commit message (concise, descriptive)",
            },
        },
        "required": ["message"],
    },
}


async def _run_git(args: list[str]) -> str:
    """Run a git command and return stdout."""
    proc = await asyncio.create_subprocess_exec(
        "git", *args,
        cwd=str(PROJECT_ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    output = stdout.decode().strip()
    if proc.returncode != 0:
        err = stderr.decode().strip()
        return f"Error (exit {proc.returncode}): {err}"
    return output or "(no output)"


async def handle_git_status(input: dict) -> str:
    """Show git status."""
    return await _run_git(["status", "--short"])


async def handle_git_add(input: dict) -> str:
    """Stage files for commit."""
    paths = input["paths"]
    return await _run_git(["add"] + paths)


async def handle_git_commit(input: dict) -> str:
    """Create a git commit."""
    message = input["message"]
    return await _run_git(["commit", "-m", message])
