"""Pydantic validation models for Scenarist-generated scenario packages.

Validates that generated artifacts have the correct structure
before saving to disk.
"""

from pydantic import BaseModel, Field


class AttackFeedEvent(BaseModel):
    severity: str  # HIGH, CRITICAL, BUSINESS
    system: str
    message: str


class OrchestratorDetails(BaseModel):
    short_description: str
    description: str
    priority: str = "1"
    category: str


class CyberSenseMock(BaseModel):
    corrupted_files: list[str] = Field(default_factory=list)
    attack_classification: dict = Field(default_factory=dict)
    recovery_recommendation: dict = Field(default_factory=dict)


class ScenarioPackage(BaseModel):
    """Complete scenario package produced by the Scenarist agent."""
    name: str  # e.g. "supply_chain"
    title: str  # e.g. "Pharma Supply Chain Attack"
    orchestrator_details: OrchestratorDetails
    attack_feed: list[AttackFeedEvent] = Field(min_length=6, max_length=6)
    cybersense_mock: CyberSenseMock
    # SQL and HTML are validated as non-empty strings
    snowflake_sql: str = Field(min_length=100)
    teleprompter_html: str = Field(min_length=100)
    business_impact_md: str = Field(min_length=100)
