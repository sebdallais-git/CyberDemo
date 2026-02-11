"""Async Anthropic client wrapper with tool-calling loop and streaming.

Handles the request → tool_use → tool_result → response cycle automatically.
Supports both batch (full response) and streaming (token-by-token SSE) modes.
"""

import json
import logging
from typing import AsyncGenerator

from anthropic import AsyncAnthropic

from app.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> AsyncAnthropic:
    """Create an AsyncAnthropic client from config."""
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def run_agent_loop(
    system: str,
    messages: list[dict],
    tools: list[dict],
    tool_handler: callable,
    model: str | None = None,
    max_turns: int = 20,
) -> str:
    """Run a multi-turn tool-calling loop until Claude produces a final text response.

    Args:
        system: System prompt for the agent persona.
        messages: Initial conversation messages.
        tools: Tool definitions (Anthropic format).
        tool_handler: async callable(name, input) -> str that executes tools.
        model: Override model (defaults to settings.ANTHROPIC_MODEL).
        max_turns: Safety limit on tool-calling rounds.

    Returns:
        Final text response from Claude.
    """
    client = _get_client()
    model = model or settings.ANTHROPIC_MODEL

    for turn in range(max_turns):
        response = await client.messages.create(
            model=model,
            max_tokens=8192,
            system=system,
            messages=messages,
            tools=tools or [],
        )

        # Collect all content blocks
        text_parts = []
        tool_uses = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        # If no tool calls, we're done — return the text
        if not tool_uses:
            return "\n".join(text_parts)

        # Append assistant message with all content blocks
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool call and build tool_result messages
        tool_results = []
        for tool_use in tool_uses:
            logger.info(f"Tool call: {tool_use.name}({json.dumps(tool_use.input)[:200]})")
            try:
                result = await tool_handler(tool_use.name, tool_use.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(result),
                })
            except Exception as e:
                logger.error(f"Tool error: {tool_use.name} — {e}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": f"Error: {e}",
                    "is_error": True,
                })

        messages.append({"role": "user", "content": tool_results})

    return "\n".join(text_parts) if text_parts else "(max tool turns reached)"


async def stream_agent(
    system: str,
    messages: list[dict],
    model: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a simple (no-tools) Claude response token by token.

    Used by the Director agent for real-time cue generation.
    Yields text chunks as they arrive.
    """
    client = _get_client()
    model = model or settings.ANTHROPIC_MODEL

    async with client.messages.stream(
        model=model,
        max_tokens=2048,
        system=system,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text
