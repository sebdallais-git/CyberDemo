"""Real ServiceNow REST API client using httpx + Basic Auth.

Connects to a free Personal Developer Instance (PDI) from developer.servicenow.com.
Uses the standard incident table (available on all instances).
"""

import logging
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ServiceNowClient:
    """Client for ServiceNow REST API (Table API)."""

    def __init__(self):
        self.base_url = settings.SNOW_INSTANCE_URL.rstrip("/")
        self.auth = (settings.SNOW_USERNAME, settings.SNOW_PASSWORD)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            headers=self.headers,
            timeout=30.0,
        )

    async def create_security_incident(self, data: dict[str, Any]) -> dict:
        """Create a Security Incident Response record."""
        async with self._client() as client:
            resp = await client.post(
                "/api/now/table/incident",
                json=data,
            )
            resp.raise_for_status()
            return resp.json()["result"]

    async def get_incident(self, sys_id: str) -> dict:
        """Get a security incident by sys_id."""
        async with self._client() as client:
            resp = await client.get(
                f"/api/now/table/incident/{sys_id}",
            )
            resp.raise_for_status()
            return resp.json()["result"]

    async def update_incident(self, sys_id: str, data: dict[str, Any]) -> dict:
        """Update fields on a security incident."""
        async with self._client() as client:
            resp = await client.patch(
                f"/api/now/table/incident/{sys_id}",
                json=data,
            )
            resp.raise_for_status()
            return resp.json()["result"]

    async def add_work_note(self, sys_id: str, note: str) -> dict:
        """Add a work note to a security incident."""
        return await self.update_incident(sys_id, {"work_notes": note})

    async def resolve_incident(self, sys_id: str, notes: str) -> dict:
        """Resolve the incident: set to In Progress first, then Resolved."""
        # Move to In Progress (required by ServiceNow state transition rules)
        await self.update_incident(sys_id, {"state": "2"})
        return await self.update_incident(sys_id, {
            "state": "6",
            "close_code": "Solution provided",
            "close_notes": notes,
        })

    async def query_cmdb(self, filter_query: str) -> list[dict]:
        """Query the CMDB Configuration Items table."""
        async with self._client() as client:
            resp = await client.get(
                "/api/now/table/cmdb_ci",
                params={"sysparm_query": filter_query, "sysparm_limit": "20"},
            )
            resp.raise_for_status()
            return resp.json()["result"]

    async def is_available(self) -> bool:
        """Check if ServiceNow instance is reachable."""
        try:
            async with self._client() as client:
                resp = await client.get("/api/now/table/sys_properties?sysparm_limit=1")
                return resp.status_code == 200
        except Exception:
            return False


# Singleton
snow_client = ServiceNowClient()
