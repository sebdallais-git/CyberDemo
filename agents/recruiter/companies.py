"""Company persona definitions for the Recruiter agent.

Each company has a profile, target role, and assessment dimensions
that the recruiter persona uses to evaluate Seb as a candidate.
"""

COMPANIES = {
    "snowflake": {
        "name": "Snowflake",
        "industry": "Cloud Data Platform",
        "culture": "Engineering-driven, high-growth, data-obsessed",
        "target_role": "Strategic Account Executive — Life Sciences",
        "what_they_value": [
            "Deep understanding of data architecture and analytics",
            "Ability to sell platform value, not just features",
            "Executive-level storytelling with technical credibility",
            "Land-and-expand strategy execution",
            "Competitive intelligence (vs Databricks, BigQuery)",
        ],
        "assessment_dimensions": [
            ("Data Platform Knowledge", "Understanding of cloud data warehousing, SIEM analytics, ML integration"),
            ("Enterprise Selling", "Complex deal management, multi-stakeholder navigation"),
            ("Technical Storytelling", "Ability to make data architecture compelling to CxOs"),
            ("Pharma Domain Expertise", "Knowledge of pharma-specific use cases and regulations"),
            ("Competitive Positioning", "How well they position against alternatives"),
        ],
    },
    "crowdstrike": {
        "name": "CrowdStrike",
        "industry": "Cybersecurity (Endpoint + Cloud)",
        "culture": "Mission-driven, aggressive growth, security-first",
        "target_role": "Regional Sales Director — Healthcare/Pharma",
        "what_they_value": [
            "Cybersecurity domain expertise",
            "Ability to create urgency around threat landscape",
            "Experience selling to CISOs and security teams",
            "Understanding of compliance frameworks (HIPAA, FDA)",
            "Competitive positioning vs. legacy security vendors",
        ],
        "assessment_dimensions": [
            ("Security Acumen", "Understanding of threat landscape, attack vectors, incident response"),
            ("Urgency Creation", "Ability to make security investment feel urgent"),
            ("CISO Engagement", "Credibility with security leadership"),
            ("Compliance Knowledge", "FDA, HIPAA, GxP regulatory framework understanding"),
            ("Competitive Strategy", "Positioning against Palo Alto, SentinelOne, Microsoft"),
        ],
    },
    "palo_alto": {
        "name": "Palo Alto Networks",
        "industry": "Cybersecurity (Network + Cloud + AI)",
        "culture": "Platform-first, AI-driven, acquisition-heavy",
        "target_role": "Major Account Manager — Life Sciences",
        "what_they_value": [
            "Platform consolidation narrative (vs. point solutions)",
            "AI/ML security use cases",
            "Complex enterprise deal management",
            "OT/IoT security understanding",
            "Channel and partner ecosystem navigation",
        ],
        "assessment_dimensions": [
            ("Platform Selling", "Ability to sell platform consolidation vs. best-of-breed"),
            ("AI Security Vision", "Understanding of AI-driven security and XSIAM"),
            ("OT Security", "Knowledge of SCADA/ICS protection in pharma"),
            ("Deal Complexity", "Managing multi-product, multi-stakeholder deals"),
            ("Partner Ecosystem", "Experience with VAR/SI partner-led selling"),
        ],
    },
    "dell": {
        "name": "Dell Technologies",
        "industry": "Infrastructure + Data Protection + AI",
        "culture": "Relationship-driven, long sales cycles, trusted advisor",
        "target_role": "Global Account Manager — Pharma",
        "what_they_value": [
            "Deep customer relationships at CxO level",
            "Full-stack infrastructure knowledge (compute, storage, protection)",
            "Ability to orchestrate complex solutions across BUs",
            "Long-term strategic account planning",
            "Partner ecosystem (VMware, ServiceNow, Snowflake)",
        ],
        "assessment_dimensions": [
            ("Customer Intimacy", "Depth of CxO relationships and strategic trust"),
            ("Solution Architecture", "Understanding of compute + storage + protection stack"),
            ("Cross-BU Orchestration", "Ability to coordinate Dell ISG, DPS, CSG"),
            ("Strategic Planning", "3-year account plans, whitespace mapping"),
            ("Ecosystem Selling", "Leveraging partner ecosystem for customer value"),
        ],
    },
    "aws": {
        "name": "Amazon Web Services",
        "industry": "Cloud Infrastructure + AI/ML",
        "culture": "Customer-obsessed, builder mentality, LP-driven",
        "target_role": "Enterprise Account Manager — Life Sciences",
        "what_they_value": [
            "Working backwards from customer needs",
            "Builder mentality — creating solutions, not just selling",
            "Deep understanding of cloud migration and modernization",
            "AI/ML platform knowledge (SageMaker, Bedrock)",
            "Leadership Principles alignment",
        ],
        "assessment_dimensions": [
            ("Customer Obsession", "Working backwards from customer needs"),
            ("Cloud Architecture", "Understanding of cloud migration, hybrid, multi-cloud"),
            ("AI/ML Platform", "Knowledge of ML platforms and generative AI"),
            ("Builder Mentality", "Creating demos, prototypes, solution architectures"),
            ("LP Alignment", "Bias for action, ownership, earning trust"),
        ],
    },
    "google_cloud": {
        "name": "Google Cloud",
        "industry": "Cloud + AI + Data Analytics",
        "culture": "Data-driven, AI-first, open-source friendly",
        "target_role": "Strategic Account Executive — Healthcare & Life Sciences",
        "what_they_value": [
            "AI/ML thought leadership",
            "Data analytics and BigQuery expertise",
            "Open-source and multi-cloud positioning",
            "Healthcare/pharma regulatory compliance knowledge",
            "Enterprise deal execution at scale",
        ],
        "assessment_dimensions": [
            ("AI Thought Leadership", "Ability to articulate AI vision and use cases"),
            ("Data Analytics", "Understanding of modern data architecture and analytics"),
            ("Healthcare Expertise", "Pharma-specific regulatory and compliance knowledge"),
            ("Open Platform Vision", "Multi-cloud, open-source, interoperability messaging"),
            ("Enterprise Execution", "Complex deal management and closing ability"),
        ],
    },
}


def get_company(name: str) -> dict | None:
    """Get company definition by key."""
    return COMPANIES.get(name)


def get_all_companies() -> dict:
    """Get all company definitions."""
    return COMPANIES
