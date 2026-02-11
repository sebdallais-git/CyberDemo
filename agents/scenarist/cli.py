"""CLI entry point for the Scenarist agent.

Two-phase interactive workflow:
1. Analyze & propose (shows proposal, asks for approval)
2. Generate artifacts (only if user approves)

Usage:
    python -m agents.scenarist --mode search --topic "pharma supply chain attack"
    python -m agents.scenarist --mode curated --text "Article about MedTech breach..."
    python -m agents.scenarist --mode curated --urls https://example.com/article1
    python -m agents.scenarist --auto  # skip approval step (for automation)
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agents.scenarist.agent import ScenaristAgent


def main():
    parser = argparse.ArgumentParser(description="Scenarist — CyberDemo scenario generator")
    parser.add_argument("--mode", choices=["search", "curated"], default="search",
                        help="search: web search | curated: from text/URLs")
    parser.add_argument("--topic", type=str, default="pharma cybersecurity attack 2025",
                        help="Search topic (search mode)")
    parser.add_argument("--text", type=str, default="",
                        help="Source text (curated mode)")
    parser.add_argument("--urls", nargs="*", default=[],
                        help="URLs to fetch (curated mode)")
    parser.add_argument("--name", type=str, default="",
                        help="Override scenario folder name")
    parser.add_argument("--auto", action="store_true",
                        help="Skip approval step — auto-generate after analysis")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    agent = ScenaristAgent()

    # Phase 1: Analyze and propose
    print("\n" + "=" * 60)
    print("PHASE 1: ANALYSIS & PROPOSAL")
    print("=" * 60 + "\n")

    proposal = asyncio.run(agent.analyze(
        mode=args.mode,
        topic=args.topic,
        curated_text=args.text,
        urls=args.urls,
    ))

    print(proposal)

    # Ask for approval (unless --auto)
    if not args.auto:
        print("\n" + "-" * 60)
        response = input("Approve this proposal? [y/N/edit] > ").strip().lower()
        if response == "edit":
            print("Enter modifications (end with empty line):")
            edits = []
            while True:
                line = input()
                if not line:
                    break
                edits.append(line)
            proposal += "\n\nUser modifications:\n" + "\n".join(edits)
        elif response != "y":
            print("Cancelled.")
            return

    # Phase 2: Generate
    print("\n" + "=" * 60)
    print("PHASE 2: GENERATING ARTIFACTS")
    print("=" * 60 + "\n")

    result = asyncio.run(agent.generate(
        proposal=proposal,
        scenario_name=args.name,
    ))

    print(result)
    print("\n" + "=" * 60)
    print("DONE — Check agents/output/scenarios/")
    print("=" * 60)


if __name__ == "__main__":
    main()
