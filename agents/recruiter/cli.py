"""CLI entry point for the Recruiter agent.

Usage:
    python -m agents.recruiter --company snowflake --mode report
    python -m agents.recruiter --company crowdstrike --mode conversation
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agents.recruiter.agent import RecruiterAgent


def main():
    parser = argparse.ArgumentParser(description="Recruiter — SaaS/cloud talent scout simulator")
    parser.add_argument("--company", type=str, default="snowflake",
                        help="Company: snowflake, crowdstrike, palo_alto, dell, aws, google_cloud")
    parser.add_argument("--mode", choices=["report", "conversation"], default="report",
                        help="report: formal assessment | conversation: simulated interview")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    agent = RecruiterAgent()
    result = asyncio.run(agent.run(company=args.company, mode=args.mode))

    print("\n" + "=" * 60)
    print(f"RECRUITER — {args.company.upper()}")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
