"""Pydantic models for CyberDemo."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    RANSOMWARE = "ransomware"
    SUPPLY_CHAIN = "supply_chain"
    DATA_EXFIL = "data_exfil"


class ScenarioRequest(BaseModel):
    type: ScenarioType


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class SSEEvent(BaseModel):
    """Server-Sent Event payload for the 7-step timeline."""
    step: int  # 1-7
    name: str  # e.g. "DETECT", "INCIDENT"
    status: StepStatus
    message: str
    data: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class VaultState(str, Enum):
    LOCKED = "LOCKED"
    SYNCING = "SYNCING"
    ANALYZING = "ANALYZING"
    CLEAN = "CLEAN"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"


class CyberSenseResult(BaseModel):
    confidence: float = 99.99
    corrupted_files: list[str] = Field(default_factory=list)
    attack_vector: str = "partial_encryption"
    ransomware_family: str = "LockBit 4.0"
    last_clean_pit: str = ""
    affected_servers: list[str] = Field(default_factory=list)
    total_files_scanned: int = 0
    total_corrupted: int = 0


class IncidentSummary(BaseModel):
    sys_id: str = ""
    number: str = ""
    short_description: str = ""
    state: str = ""
    priority: str = ""
    url: str = ""
