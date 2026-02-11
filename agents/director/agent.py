"""DirectorAgent — hybrid playbook + LLM live stage director.

Subscribes to the internal event bus and produces presenter cues.
Uses pre-written playbook cues for known scenarios (0ms latency).
Falls back to Claude LLM for edge cases or unknown scenarios.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from agents.base import BaseAgent
from agents.claude_client import run_agent_loop
from agents.director.playbook import get_cue
from agents.prompts.director import DIRECTOR_SYSTEM_PROMPT
from app.events import subscribe, unsubscribe

logger = logging.getLogger(__name__)


class DirectorAgent(BaseAgent):
    name = "director"

    @property
    def system_prompt(self) -> str:
        return DIRECTOR_SYSTEM_PROMPT

    async def run(self, **kwargs) -> str:
        # Director doesn't use the standard run() — it uses stream_cues()
        return "Director agent uses stream_cues() for live operation."

    async def stream_cues(self, scenario: str) -> AsyncGenerator[dict, None]:
        """Subscribe to orchestrator events and yield presenter cues.

        Each yielded dict has: cue, talking_points, next_cues, timing.
        """
        queue = subscribe()
        # Track conversation history for LLM fallback context
        llm_messages = []

        try:
            while True:
                try:
                    # Wait for next orchestrator event (timeout prevents zombie connections)
                    event = await asyncio.wait_for(queue.get(), timeout=300)
                except asyncio.TimeoutError:
                    logger.info("Director: no events for 5 min, closing stream")
                    break

                step_name = event.get("name", "")
                status = event.get("status", "")
                message = event.get("message", "")

                # Skip empty events
                if not step_name:
                    continue

                # Try playbook first (instant)
                cue = get_cue(scenario, step_name, status)
                if cue:
                    logger.info(f"Director: playbook cue for {step_name}/{status}")
                    yield cue
                    continue

                # Fall back to LLM for unknown combinations
                logger.info(f"Director: LLM fallback for {step_name}/{status}")
                llm_messages.append({
                    "role": "user",
                    "content": (
                        f"Scenario: {scenario}\n"
                        f"Step: {step_name} (status: {status})\n"
                        f"Message: {message}\n\n"
                        f"Generate a direction cue for the presenter."
                    ),
                })

                try:
                    response = await run_agent_loop(
                        system=self.system_prompt,
                        messages=llm_messages.copy(),
                        tools=[],
                        tool_handler=self.handle_tool,
                    )

                    # Parse JSON response from LLM
                    cue_data = json.loads(response)
                    llm_messages.append({"role": "assistant", "content": response})
                    yield cue_data

                except (json.JSONDecodeError, Exception) as e:
                    logger.error(f"Director LLM error: {e}")
                    # Graceful fallback — generic cue
                    yield {
                        "cue": f"{step_name} — {status}",
                        "talking_points": [message],
                        "next_cues": ["Continue with the demo"],
                        "timing": "go",
                    }

        finally:
            unsubscribe(queue)
