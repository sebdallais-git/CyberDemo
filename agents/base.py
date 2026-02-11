"""BaseAgent — shared foundation for all CyberDemo agents.

Provides common setup: output directory management, tool registration,
and the standard run() interface that subclasses implement.
"""

import logging
from pathlib import Path
from abc import ABC, abstractmethod

from app.config import settings

logger = logging.getLogger(__name__)

# Root output directory for all generated artifacts
OUTPUT_DIR = Path(settings.AGENT_OUTPUT_DIR)


class BaseAgent(ABC):
    """Abstract base for all CyberDemo agents.

    Subclasses must implement:
        - system_prompt: str property — the agent's persona/instructions
        - tools: list of tool definitions (Anthropic format)
        - handle_tool(name, input): execute a tool call
        - run(**kwargs): main entry point
    """

    name: str = "base"

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        ...

    @property
    def tools(self) -> list[dict]:
        """Tool definitions (Anthropic format). Override in subclasses that use tools."""
        return []

    async def handle_tool(self, name: str, input: dict) -> str:
        """Execute a tool call. Override in subclasses that use tools."""
        return f"Unknown tool: {name}"

    @abstractmethod
    async def run(self, **kwargs) -> str:
        """Run the agent. Returns the final output text."""
        ...
