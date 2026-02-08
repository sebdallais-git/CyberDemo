"""Vault state machine for mock Dell Cyber Recovery.

States: LOCKED → SYNCING → ANALYZING → CLEAN/CORRUPTED → RECOVERING → RECOVERED
Timing is accelerated for demo (real CR takes minutes, mock takes seconds).
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class VaultState(str, Enum):
    LOCKED = "LOCKED"
    SYNCING = "SYNCING"
    ANALYZING = "ANALYZING"
    CLEAN = "CLEAN"
    CORRUPTED = "CORRUPTED"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"


class VaultStateMachine:
    """Manages vault lifecycle with configurable timing for demo speed."""

    def __init__(self):
        self.state = VaultState.LOCKED
        self.sync_duration = 7.0    # seconds (real: minutes) — gives presenter time on infra page
        self.analyze_duration = 8.0  # CyberSense scan — runs while presenter does kill chain
        self.recovery_duration = 10.0  # slow bar fill for dramatic effect on dashboard
        self.last_transition: Optional[str] = None
        self._progress: float = 0.0  # 0.0 to 1.0 for current operation

    @property
    def progress(self) -> float:
        return self._progress

    async def trigger_sync(self) -> dict:
        """Open air gap, sync data, close air gap."""
        if self.state not in (VaultState.LOCKED, VaultState.RECOVERED):
            return {"error": f"Cannot sync from state {self.state}"}

        self.state = VaultState.SYNCING
        self._progress = 0.0
        logger.info("Vault: Air gap OPEN — syncing data")

        # Simulate sync progress
        steps = 10
        for i in range(steps):
            await asyncio.sleep(self.sync_duration / steps)
            self._progress = (i + 1) / steps

        self.state = VaultState.LOCKED
        self._progress = 1.0
        self.last_transition = datetime.utcnow().isoformat()
        logger.info("Vault: Sync complete — air gap CLOSED")
        return {"status": "sync_complete", "vault_state": self.state}

    async def run_analysis(self) -> dict:
        """Run CyberSense analysis (returns to ANALYZING then result state)."""
        self.state = VaultState.ANALYZING
        self._progress = 0.0
        logger.info("Vault: CyberSense analysis running")

        steps = 10
        for i in range(steps):
            await asyncio.sleep(self.analyze_duration / steps)
            self._progress = (i + 1) / steps

        # Always find corruption for demo purposes
        self.state = VaultState.CORRUPTED
        self._progress = 1.0
        self.last_transition = datetime.utcnow().isoformat()
        logger.info("Vault: Analysis complete — CORRUPTION DETECTED")
        return {"status": "analysis_complete", "result": "corrupted"}

    async def initiate_recovery(self) -> dict:
        """Recover from clean PIT copy."""
        if self.state != VaultState.CORRUPTED:
            return {"error": f"Cannot recover from state {self.state}"}

        self.state = VaultState.RECOVERING
        self._progress = 0.0
        logger.info("Vault: Recovery in progress from clean PIT copy")

        steps = 10
        for i in range(steps):
            await asyncio.sleep(self.recovery_duration / steps)
            self._progress = (i + 1) / steps

        self.state = VaultState.RECOVERED
        self._progress = 1.0
        self.last_transition = datetime.utcnow().isoformat()
        logger.info("Vault: Recovery COMPLETE")
        return {"status": "recovery_complete", "vault_state": self.state}

    def reset(self):
        """Reset vault to initial state."""
        self.state = VaultState.LOCKED
        self._progress = 0.0
        self.last_transition = None


# Singleton
vault = VaultStateMachine()
