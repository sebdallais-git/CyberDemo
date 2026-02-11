"""ScenaristAgent — generates complete scenario packages from news or curated input.

Two-phase workflow:
1. ANALYZE: Read existing scenarios + research external sources → produce a proposal
2. GENERATE: Only after user approval, generate the full artifact set

Modes:
- search: Uses Brave Search API to find recent pharma cyber incidents
- curated: Uses provided URLs or pasted text as source material
"""

import json
import logging

from agents.base import BaseAgent
from agents.claude_client import run_agent_loop
from agents.prompts.scenarist import SCENARIST_SYSTEM_PROMPT, REFERENCE_SCENARIO_NOTE
from agents.tools.file_writer import FILE_WRITER_TOOL, handle_write_file
from agents.tools.scenario_reader import SCENARIO_READER_TOOL, handle_read_scenario
from agents.tools.web_search import (
    WEB_SEARCH_TOOL, FETCH_URL_TOOL,
    handle_web_search, handle_fetch_url,
)

logger = logging.getLogger(__name__)


class ScenaristAgent(BaseAgent):
    name = "scenarist"

    @property
    def system_prompt(self) -> str:
        return SCENARIST_SYSTEM_PROMPT

    @property
    def tools(self) -> list[dict]:
        return [
            WEB_SEARCH_TOOL,
            FETCH_URL_TOOL,
            SCENARIO_READER_TOOL,
            FILE_WRITER_TOOL,
        ]

    async def handle_tool(self, name: str, input: dict) -> str:
        handlers = {
            "web_search": handle_web_search,
            "fetch_url": handle_fetch_url,
            "read_scenario": handle_read_scenario,
            "write_file": handle_write_file,
        }
        handler = handlers.get(name)
        if not handler:
            return f"Unknown tool: {name}"
        return await handler(input)

    async def analyze(self, *, mode: str = "search", topic: str = "", curated_text: str = "",
                      urls: list[str] | None = None) -> str:
        """Phase 1: Research and propose — DO NOT generate files yet.

        Reads existing scenarios, researches external sources, then returns
        a structured proposal for the user to review before generation.
        """
        if mode == "search":
            user_msg = (
                f"ANALYSIS PHASE — Do NOT write any files yet.\n\n"
                f"Search topic: {topic}\n\n"
                f"Steps:\n"
                f"1. Read the existing scenarios (snowflake_ransomware.sql, app.js, orchestrator.py) "
                f"to understand current structure and what already exists\n"
                f"2. Search the web for recent news on this topic\n"
                f"3. If you find good articles, fetch their content for details\n"
                f"4. Based on your research, propose a NEW scenario. Respond with:\n\n"
                f"## Proposal\n"
                f"- **Scenario Name**: (slug, e.g. supply_chain)\n"
                f"- **Title**: (human-readable)\n"
                f"- **Based On**: (real incident/news source with URL)\n"
                f"- **Attack Vector**: (how the attack starts)\n"
                f"- **Impact**: (what gets damaged, business cost)\n"
                f"- **Why It's Compelling**: (why this story works for CxOs)\n"
                f"- **Key Differences from Existing Scenarios**: (what's new vs ransomware/ai_factory/data_exfil)\n"
                f"- **Proposed Artifacts**: Brief outline of what each file will contain\n\n"
                f"DO NOT use write_file. Only read and research."
            )
        else:
            sources = ""
            if curated_text:
                sources += f"Source material:\n{curated_text}\n\n"
            if urls:
                sources += f"URLs to research:\n" + "\n".join(urls) + "\n\n"

            user_msg = (
                f"ANALYSIS PHASE — Do NOT write any files yet.\n\n"
                f"{sources}"
                f"Steps:\n"
                f"1. Read the existing scenarios to understand current structure\n"
                f"2. If URLs are provided, fetch their content\n"
                f"3. Analyze the source material and propose a scenario. Respond with:\n\n"
                f"## Proposal\n"
                f"- **Scenario Name**: (slug)\n"
                f"- **Title**: (human-readable)\n"
                f"- **Based On**: (source material summary)\n"
                f"- **Attack Vector**: (how the attack starts)\n"
                f"- **Impact**: (what gets damaged, business cost)\n"
                f"- **Why It's Compelling**: (why this story works for CxOs)\n"
                f"- **Key Differences from Existing Scenarios**: (what's new)\n"
                f"- **Proposed Artifacts**: Brief outline of what each file will contain\n\n"
                f"DO NOT use write_file. Only read and research."
            )

        # Remove write_file from available tools during analysis
        analysis_tools = [t for t in self.tools if t["name"] != "write_file"]

        messages = [{"role": "user", "content": user_msg}]

        result = await run_agent_loop(
            system=self.system_prompt,
            messages=messages,
            tools=analysis_tools,
            tool_handler=self.handle_tool,
        )

        logger.info("Scenarist analysis phase complete — proposal ready for review")
        return result

    async def generate(self, *, proposal: str, scenario_name: str = "") -> str:
        """Phase 2: Generate all artifacts based on the approved proposal.

        Called only after the user has reviewed and approved the proposal.
        """
        user_msg = (
            f"GENERATION PHASE — The user has approved the following proposal:\n\n"
            f"{proposal}\n\n"
            f"Now generate ALL 6 artifacts:\n"
            f"1. snowflake.sql — Snowflake SIEM data (4 hosts, 10 endpoint events, 20 network events)\n"
            f"2. orchestrator_details.json — ServiceNow incident details\n"
            f"3. attack_feed.json — 6 events for the dashboard feed\n"
            f"4. cybersense_mock.json — CyberSense analysis mock data\n"
            f"5. teleprompter.html — Presenter direction script\n"
            f"6. business_impact.md — CxO business impact narrative\n\n"
            f"Read the existing ransomware scenario files first for structural reference, "
            f"then generate and save each artifact using write_file.\n\n"
            f"{REFERENCE_SCENARIO_NOTE}"
        )

        if scenario_name:
            user_msg += f"\nSave to 'scenarios/{scenario_name}/'."

        messages = [{"role": "user", "content": user_msg}]

        result = await run_agent_loop(
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_handler=self.handle_tool,
        )

        logger.info(f"Scenarist generation complete — output in agents/output/scenarios/")
        return result

    async def run(self, *, mode: str = "search", topic: str = "", curated_text: str = "",
                  urls: list[str] | None = None, scenario_name: str = "") -> str:
        """Full two-phase run (for API/web use — analyze then auto-generate).

        For interactive CLI use, call analyze() and generate() separately.
        """
        # Phase 1: Analyze and propose
        proposal = await self.analyze(
            mode=mode, topic=topic, curated_text=curated_text, urls=urls,
        )

        # Phase 2: Generate (in API mode, auto-approve)
        result = await self.generate(proposal=proposal, scenario_name=scenario_name)
        return result
