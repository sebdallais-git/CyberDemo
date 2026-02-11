"""CLI entry point for the Documentalist agent.

Usage:
    python -m agents.documentalist --mode code
    python -m agents.documentalist --mode scenario --scenario ransomware
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agents.documentalist.agent import DocumentalistAgent


def main():
    parser = argparse.ArgumentParser(description="Documentalist — CyberDemo docs generator")
    parser.add_argument("--mode", choices=["code", "scenario"], default="code",
                        help="code: architecture docs | scenario: presenter runbook + briefs")
    parser.add_argument("--scenario", type=str, default="ransomware",
                        help="Scenario name (scenario mode only)")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    agent = DocumentalistAgent()
    result = asyncio.run(agent.run(mode=args.mode, scenario=args.scenario))

    print("\n" + "=" * 60)
    print("DOCUMENTALIST OUTPUT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
