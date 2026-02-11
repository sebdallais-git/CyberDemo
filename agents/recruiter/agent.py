"""RecruiterAgent — simulates talent scouts evaluating Seb as a candidate.

Modes:
- report: Formal fit assessment with scores and recommendation
- conversation: Simulated recruiter interview dialogue
"""

import logging

from agents.base import BaseAgent
from agents.claude_client import run_agent_loop
from agents.prompts.recruiter import RECRUITER_SYSTEM_PROMPT
from agents.recruiter.companies import get_company
from agents.tools.file_writer import FILE_WRITER_TOOL, handle_write_file
from agents.tools.scenario_reader import SCENARIO_READER_TOOL, handle_read_scenario

logger = logging.getLogger(__name__)


class RecruiterAgent(BaseAgent):
    name = "recruiter"

    @property
    def system_prompt(self) -> str:
        return RECRUITER_SYSTEM_PROMPT

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

    async def run(self, *, company: str = "snowflake", mode: str = "report") -> str:
        """Generate a recruiter assessment.

        Args:
            company: Company key (snowflake, crowdstrike, palo_alto, dell, aws, google_cloud)
            mode: "report" (formal assessment) or "conversation" (simulated interview)
        """
        comp = get_company(company)
        if not comp:
            return f"Unknown company: {company}. Available: snowflake, crowdstrike, palo_alto, dell, aws, google_cloud"

        # Build company context
        company_context = (
            f"## Your Company: {comp['name']}\n"
            f"Industry: {comp['industry']}\n"
            f"Culture: {comp['culture']}\n"
            f"Target Role: {comp['target_role']}\n\n"
            f"What {comp['name']} Values:\n"
            + "\n".join(f"- {v}" for v in comp['what_they_value'])
            + "\n\nAssessment Dimensions:\n"
            + "\n".join(f"- **{dim}**: {desc}" for dim, desc in comp['assessment_dimensions'])
        )

        if mode == "report":
            user_msg = (
                f"You are a senior recruiter at {comp['name']}.\n\n"
                f"{company_context}\n\n"
                f"Generate a formal candidate fit report for Sebastien DALLAIS.\n\n"
                f"Steps:\n"
                f"1. Read the demo scenario files (orchestrator.py, app.js, "
                f"snowflake_ransomware.sql) to understand what Seb built\n"
                f"2. Assess each dimension with a score (1-10) and specific evidence\n"
                f"3. Write the full report\n"
                f"4. Save to 'recruiter_reports/{company}_fit_report.md'\n"
            )
        else:
            user_msg = (
                f"You are a senior recruiter at {comp['name']}.\n\n"
                f"{company_context}\n\n"
                f"Simulate a recruiter conversation with Seb. Ask 5-7 probing questions "
                f"about the demo, his selling approach, and fit for the target role. "
                f"After each question, provide the 'ideal answer' that would impress "
                f"this recruiter, based on what the demo reveals.\n\n"
                f"Steps:\n"
                f"1. Read the demo files to understand what Seb built\n"
                f"2. Generate the interview dialogue\n"
                f"3. Save to 'recruiter_reports/{company}_conversation.md'\n"
            )

        messages = [{"role": "user", "content": user_msg}]

        result = await run_agent_loop(
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_handler=self.handle_tool,
        )

        logger.info(f"Recruiter report for {comp['name']} completed")
        return result
