"""Dell Cyber Recovery REST API v7 client.

Works against both the real Dell CR API (via SSH tunnel to HOL VM)
and the local mock server — both expose the same endpoints on localhost:14778.
"""

import logging
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class DellCRClient:
    """Client for Dell Cyber Recovery REST API v7."""

    def __init__(self):
        self.base_url = settings.DELLCR_BASE_URL.rstrip("/")
        self.username = settings.DELLCR_USERNAME
        self.password = settings.DELLCR_PASSWORD
        self.access_token: Optional[str] = None

    def _client(self) -> httpx.AsyncClient:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.access_token:
            headers["X-CR-AUTH-TOKEN"] = self.access_token
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30.0,
        )

    async def login(self) -> dict:
        """Authenticate and store access token."""
        async with self._client() as client:
            resp = await client.post("/cr/v7/login", json={
                "username": self.username,
                "password": self.password,
            })
            resp.raise_for_status()
            data = resp.json()
            self.access_token = data.get("accessToken")
            logger.info("Dell CR login successful")
            return data

    async def get_system_status(self) -> dict:
        """Get overall system status including vault state."""
        async with self._client() as client:
            resp = await client.get("/cr/v7/system")
            resp.raise_for_status()
            return resp.json()

    async def list_vaults(self) -> list[dict]:
        """List all vault copies."""
        async with self._client() as client:
            resp = await client.get("/cr/v7/vaults")
            resp.raise_for_status()
            return resp.json().get("vaults", [])

    async def trigger_policy(self, policy_id: str) -> dict:
        """Trigger a replication policy — opens air gap, syncs, closes."""
        async with self._client() as client:
            resp = await client.post(f"/cr/v7/policies/{policy_id}/run")
            resp.raise_for_status()
            return resp.json()

    async def list_sandboxes(self) -> list[dict]:
        """List available sandboxes for analysis."""
        async with self._client() as client:
            resp = await client.get("/cr/v7/sandboxes")
            resp.raise_for_status()
            return resp.json().get("sandboxes", [])

    async def run_cybersense(self, sandbox_id: str) -> dict:
        """Run CyberSense ML analysis on a sandbox copy."""
        async with self._client() as client:
            resp = await client.post(f"/cr/v7/sandboxes/{sandbox_id}/analyze")
            resp.raise_for_status()
            return resp.json()

    async def get_alerts(self) -> list[dict]:
        """Get CyberSense alerts."""
        async with self._client() as client:
            resp = await client.get("/cr/v7/alerts")
            resp.raise_for_status()
            return resp.json().get("alerts", [])

    async def initiate_recovery(self, pit_id: str) -> dict:
        """Initiate recovery from a specific point-in-time copy."""
        async with self._client() as client:
            resp = await client.post("/cr/v7/recovery", json={"pit_id": pit_id})
            resp.raise_for_status()
            return resp.json()

    async def get_activities(self) -> list[dict]:
        """Get recent activity log."""
        async with self._client() as client:
            resp = await client.get("/cr/v7/activities")
            resp.raise_for_status()
            return resp.json().get("activities", [])

    async def is_available(self) -> bool:
        """Check if Dell CR API is reachable."""
        try:
            async with self._client() as client:
                resp = await client.get("/cr/v7/system")
                return resp.status_code in (200, 401)  # 401 = reachable but needs auth
        except Exception:
            return False


# Singleton
dellcr_client = DellCRClient()
