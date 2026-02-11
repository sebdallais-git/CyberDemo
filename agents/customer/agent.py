"""CustomerAgent — evaluates scenarios from CxO perspectives.

Supports evaluating from a single persona or all four personas at once.
"""

import logging

from agents.base import BaseAgent
from agents.claude_client import run_agent_loop
from agents.customer.personas import get_persona, get_all_personas
from agents.prompts.customer import CUSTOMER_SYSTEM_PROMPT
from agents.tools.file_writer import FILE_WRITER_TOOL, handle_write_file
from agents.tools.scenario_reader import SCENARIO_READER_TOOL, handle_read_scenario

logger = logging.getLogger(__name__)


class CustomerAgent(BaseAgent):
    name = "customer"

    @property
    def system_prompt(self) -> str:
        return CUSTOMER_SYSTEM_PROMPT

    @property
    def tools(self) -> list[dict]:
        return [SCENARIO_READER_TOOL, FILE_WRITER_TOOL]

    async def handle_tool(self, name: str, input: dict) -> str:
        handlers = {
            "read_scenario": handle_read_scenario,
            "write_file": handle_write_file,
        }
        handler = handlers.get(name)
        if not handler:
            return f"Unknown tool: {name}"
        return await handler(input)

    async def run(self, *, scenario: str = "ransomware", persona: str = "all") -> str:
        """Evaluate a scenario from CxO perspectives.

        Args:
            scenario: Scenario name (ransomware, ai_factory, data_exfil)
            persona: Specific persona (cio, cfo, rd_head, mfg_head) or "all"
        """
        # Build persona context
        if persona == "all":
            personas = get_all_personas()
            persona_block = "\n".join(
                f"### {p['short']} ({p['title']})\n"
                f"Concerns: {', '.join(p['concerns'][:3])}\n"
                f"Lens: {p['evaluation_lens']}\n"
                for p in personas.values()
            )
            output_note = f"Save the complete report to 'evaluations/{scenario}_all_personas.md'"
        else:
            p = get_persona(persona)
            if not p:
                return f"Unknown persona: {persona}. Available: cio, cfo, rd_head, mfg_head"
            persona_block = (
                f"### {p['short']} ({p['title']})\n"
                f"Concerns: {', '.join(p['concerns'])}\n"
                f"Lens: {p['evaluation_lens']}\n"
            )
            output_note = f"Save the report to 'evaluations/{scenario}_{persona}.md'"

        user_msg = (
            f"Evaluate the '{scenario}' scenario from the following CxO perspectives:\n\n"
            f"{persona_block}\n\n"
            f"Steps:\n"
            f"1. Read the scenario files: snowflake_{scenario}.sql, orchestrator.py, app.js\n"
            f"2. Analyze the scenario from each persona's perspective\n"
            f"3. Score each dimension (1-10) with justification\n"
            f"4. Identify strengths, gaps, and specific improvements\n"
            f"5. {output_note}\n"
        )

        messages = [{"role": "user", "content": user_msg}]

        result = await run_agent_loop(
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_handler=self.handle_tool,
        )

        logger.info(f"Customer evaluation completed for {scenario}")
        return result
