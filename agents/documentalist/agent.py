"""DocumentalistAgent — generates code docs and scenario runbooks.

Modes:
- code: Reads all source files, generates architecture overview and API reference
- scenario: Reads a scenario, generates presenter runbook and audience briefs
"""

import logging

from agents.base import BaseAgent
from agents.claude_client import run_agent_loop
from agents.prompts.documentalist import DOCUMENTALIST_SYSTEM_PROMPT
from agents.tools.codebase_reader import (
    CODEBASE_LIST_TOOL, CODEBASE_READ_TOOL,
    handle_list_source_files, handle_read_source_file,
)
from agents.tools.file_writer import FILE_WRITER_TOOL, handle_write_file
from agents.tools.git_ops import (
    GIT_STATUS_TOOL, GIT_ADD_TOOL, GIT_COMMIT_TOOL,
    handle_git_status, handle_git_add, handle_git_commit,
)
from agents.tools.scenario_reader import SCENARIO_READER_TOOL, handle_read_scenario

logger = logging.getLogger(__name__)


class DocumentalistAgent(BaseAgent):
    name = "documentalist"

    @property
    def system_prompt(self) -> str:
        return DOCUMENTALIST_SYSTEM_PROMPT

    @property
    def tools(self) -> list[dict]:
        return [
            CODEBASE_LIST_TOOL,
            CODEBASE_READ_TOOL,
            SCENARIO_READER_TOOL,
            FILE_WRITER_TOOL,
            GIT_STATUS_TOOL,
            GIT_ADD_TOOL,
            GIT_COMMIT_TOOL,
        ]

    async def handle_tool(self, name: str, input: dict) -> str:
        handlers = {
            "list_source_files": handle_list_source_files,
            "read_source_file": handle_read_source_file,
            "read_scenario": handle_read_scenario,
            "write_file": handle_write_file,
            "git_status": handle_git_status,
            "git_add": handle_git_add,
            "git_commit": handle_git_commit,
        }
        handler = handlers.get(name)
        if not handler:
            return f"Unknown tool: {name}"
        return await handler(input)

    async def run(self, *, mode: str = "code", scenario: str = "ransomware") -> str:
        """Generate documentation.

        Args:
            mode: "code" (architecture docs) or "scenario" (presenter runbook + briefs)
            scenario: Scenario name (only used in scenario mode)
        """
        if mode == "code":
            user_msg = (
                "Generate complete code documentation for the CyberDemo project.\n\n"
                "Steps:\n"
                "1. List all source files to understand the project structure\n"
                "2. Read each key source file (app/main.py, app/orchestrator.py, "
                "app/config.py, app/models.py, etc.)\n"
                "3. Generate:\n"
                "   - Architecture overview (architecture.md)\n"
                "   - API reference (api_reference.md)\n"
                "   - Component descriptions (components.md)\n"
                "4. Save all docs using write_file to 'docs/code/'\n"
                "5. Stage and commit the docs to git\n"
            )
        else:
            user_msg = (
                f"Generate scenario documentation for the '{scenario}' scenario.\n\n"
                f"Steps:\n"
                f"1. Read the scenario data: snowflake_{scenario}.sql, orchestrator.py, app.js\n"
                f"2. Generate:\n"
                f"   - Presenter runbook (runbook_{scenario}.md) — step-by-step demo guide\n"
                f"   - CIO brief (brief_cio_{scenario}.md)\n"
                f"   - CFO brief (brief_cfo_{scenario}.md)\n"
                f"   - R&D Head brief (brief_rd_{scenario}.md)\n"
                f"   - MFG Head brief (brief_mfg_{scenario}.md)\n"
                f"3. Save all docs using write_file to 'docs/scenarios/{scenario}/'\n"
                f"4. Stage and commit the docs to git\n"
            )

        messages = [{"role": "user", "content": user_msg}]

        result = await run_agent_loop(
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_handler=self.handle_tool,
        )

        logger.info(f"Documentalist completed — output in agents/output/docs/")
        return result
