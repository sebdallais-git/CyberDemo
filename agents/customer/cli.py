"""CLI entry point for the Customer evaluator agent.

Usage:
    python -m agents.customer --scenario ransomware
    python -m agents.customer --scenario ransomware --persona cfo
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agents.customer.agent import CustomerAgent


def main():
    parser = argparse.ArgumentParser(description="Customer — CxO scenario evaluator")
    parser.add_argument("--scenario", type=str, default="ransomware",
                        help="Scenario to evaluate (ransomware, ai_factory, data_exfil)")
    parser.add_argument("--persona", type=str, default="all",
                        help="Persona: cio, cfo, rd_head, mfg_head, or all")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )

    agent = CustomerAgent()
    result = asyncio.run(agent.run(scenario=args.scenario, persona=args.persona))

    print("\n" + "=" * 60)
    print("CUSTOMER EVALUATION")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
