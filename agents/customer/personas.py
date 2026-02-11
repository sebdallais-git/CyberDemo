"""CxO persona definitions for the Customer evaluator agent.

Each persona has specific concerns, evaluation criteria, and the lens
through which they assess cybersecurity demos.
"""

PERSONAS = {
    "cio": {
        "title": "Chief Information Officer",
        "short": "CIO",
        "concerns": [
            "Recovery time objective (RTO) and recovery point objective (RPO)",
            "Audit trail completeness for regulatory compliance",
            "Vendor integration and ecosystem compatibility",
            "IT staffing requirements during and after incident",
            "Cloud vs. on-prem security architecture",
            "Board reporting capabilities",
        ],
        "evaluation_lens": (
            "Evaluate from the CIO perspective: focus on technology architecture, "
            "recovery capabilities, integration with existing IT stack, operational "
            "overhead, and how well the demo proves the solution can deliver on "
            "RTO/RPO commitments. Consider whether the demo addresses board-level "
            "reporting needs and compliance audit readiness."
        ),
    },
    "cfo": {
        "title": "Chief Financial Officer",
        "short": "CFO",
        "concerns": [
            "Total cost of ownership (TCO) and ROI",
            "Risk quantification in dollar terms",
            "Cyber insurance premium impact",
            "Regulatory fine exposure (FDA, GDPR, HIPAA)",
            "Stock price and market cap impact of breach",
            "Ransomware payment vs. recovery cost comparison",
        ],
        "evaluation_lens": (
            "Evaluate from the CFO perspective: focus on financial impact, TCO, "
            "ROI justification, risk quantification, and insurance implications. "
            "Does the demo make a compelling business case with real numbers? "
            "Can the CFO use this to justify the investment to the board? "
            "Is the 'cost of doing nothing' clearly articulated?"
        ),
    },
    "rd_head": {
        "title": "Head of R&D",
        "short": "R&D Head",
        "concerns": [
            "Intellectual property protection (formulations, synthesis routes)",
            "Data integrity of research datasets and ML models",
            "AI/ML pipeline security and recoverability",
            "Competitive advantage preservation",
            "Clinical trial data protection (21 CFR Part 11)",
            "Time-to-market impact of data loss",
        ],
        "evaluation_lens": (
            "Evaluate from the R&D Head perspective: focus on IP protection, "
            "research data integrity, AI/ML pipeline security, and the impact "
            "of data loss on competitive advantage and time-to-market. "
            "Does the demo show how R&D-specific assets (formulations, models, "
            "trial data) are protected and recoverable?"
        ),
    },
    "mfg_head": {
        "title": "Head of Manufacturing",
        "short": "MFG Head",
        "concerns": [
            "Production line uptime and continuity",
            "GxP compliance maintenance during incident",
            "Batch record integrity and recoverability",
            "SCADA/ICS system availability",
            "Supply chain continuity",
            "FDA inspection readiness post-incident",
        ],
        "evaluation_lens": (
            "Evaluate from the Manufacturing Head perspective: focus on production "
            "uptime, GxP compliance, batch record integrity, and SCADA system "
            "availability. Does the demo prove that manufacturing can resume quickly? "
            "Are batch records recoverable for FDA inspection? "
            "Is the OT network adequately protected?"
        ),
    },
}


def get_persona(name: str) -> dict | None:
    """Get persona definition by key (cio, cfo, rd_head, mfg_head)."""
    return PERSONAS.get(name)


def get_all_personas() -> dict:
    """Get all persona definitions."""
    return PERSONAS
