"""Faithful Dell Cyber Recovery REST API v7 mock server.

Runs on port 14778 — same endpoints, auth flow, and response shapes
as the real Dell CR API. Used as fallback when no SSH tunnel is available.
"""

import asyncio
import logging
import secrets
import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from typing import Optional

from mock_dellcr.cybersense import generate_analysis
from mock_dellcr.data import VAULT_CONFIG, PIT_COPIES
from mock_dellcr.vault import vault

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dell CR Mock API v7", version="7.0.0")

# Simple token store (single-user mock)
_valid_token: Optional[str] = None
# Store the scenario type for analysis context
_current_scenario: str = "ransomware"
# Track the running sync task to prevent duplicates piling up
_sync_task: Optional[asyncio.Task] = None


def _require_auth(token: Optional[str]):
    """Validate the auth token."""
    if not token or token != _valid_token:
        raise HTTPException(status_code=401, detail="Invalid or missing auth token")


# --- Auth ---

@app.post("/cr/v7/login")
async def login(request: Request):
    global _valid_token
    body = await request.json()
    username = body.get("username", "")
    password = body.get("password", "")

    # Accept any non-empty credentials in mock mode
    if not username:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    _valid_token = secrets.token_hex(32)
    logger.info(f"Mock CR login: user={username}")
    return {"accessToken": _valid_token, "expiresIn": 3600}


# --- System ---

@app.get("/cr/v7/system")
async def get_system(x_cr_auth_token: Optional[str] = Header(None)):
    _require_auth(x_cr_auth_token)
    return {
        "version": "19.18.0.0",
        "vault_state": vault.state.value,
        "vault_progress": vault.progress,
        "last_transition": vault.last_transition,
        "uptime_hours": 847,
    }


# --- Vaults ---

@app.get("/cr/v7/vaults")
async def list_vaults(x_cr_auth_token: Optional[str] = Header(None)):
    _require_auth(x_cr_auth_token)
    return {
        "vaults": [{
            "id": VAULT_CONFIG["id"],
            "name": VAULT_CONFIG["name"],
            "capacity_tb": VAULT_CONFIG["capacity_tb"],
            "used_tb": VAULT_CONFIG["used_tb"],
            "state": vault.state.value,
            "pit_copies": PIT_COPIES,
        }],
    }


# --- Policies ---

@app.post("/cr/v7/policies/{policy_id}/run")
async def trigger_policy(
    policy_id: str,
    x_cr_auth_token: Optional[str] = Header(None),
):
    global _sync_task
    _require_auth(x_cr_auth_token)
    # Run sync in background so the response returns immediately.
    # Skip if a sync is already running to prevent task pile-up.
    if _sync_task is None or _sync_task.done():
        _sync_task = asyncio.create_task(vault.trigger_sync())
    return {
        "policy_id": policy_id,
        "status": "STARTED",
        "message": "Replication policy triggered — air gap opening",
    }


# --- Sandboxes ---

@app.get("/cr/v7/sandboxes")
async def list_sandboxes(x_cr_auth_token: Optional[str] = Header(None)):
    _require_auth(x_cr_auth_token)
    return {
        "sandboxes": [{
            "id": "sandbox-pharma-01",
            "name": "PharmaProd-Analysis",
            "state": "READY",
            "vault_id": VAULT_CONFIG["id"],
        }],
    }


@app.post("/cr/v7/sandboxes/{sandbox_id}/analyze")
async def run_analysis(
    sandbox_id: str,
    x_cr_auth_token: Optional[str] = Header(None),
):
    _require_auth(x_cr_auth_token)
    # Run analysis (blocking — takes ~5s for demo)
    await vault.run_analysis()
    return generate_analysis(_current_scenario)


# --- Alerts ---

@app.get("/cr/v7/alerts")
async def get_alerts(x_cr_auth_token: Optional[str] = Header(None)):
    _require_auth(x_cr_auth_token)
    return {
        "alerts": [{
            "id": "alert-001",
            "severity": "CRITICAL",
            "type": "CORRUPTION_DETECTED",
            "message": "CyberSense detected file corruption in vault copy",
            "timestamp": vault.last_transition or "2025-02-07T14:30:00Z",
        }] if vault.state.value in ("CORRUPTED", "RECOVERING", "RECOVERED") else [],
    }


# --- Recovery ---

@app.post("/cr/v7/recovery")
async def initiate_recovery(
    request: Request,
    x_cr_auth_token: Optional[str] = Header(None),
):
    _require_auth(x_cr_auth_token)
    body = await request.json()
    pit_id = body.get("pit_id", "")

    result = await vault.initiate_recovery()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "status": "RECOVERY_COMPLETE",
        "pit_id": pit_id,
        "restored_files": 1704,
        "restored_size_gb": 248.7,
        "duration_seconds": vault.recovery_duration,
    }


# --- Activities ---

@app.get("/cr/v7/activities")
async def get_activities(x_cr_auth_token: Optional[str] = Header(None)):
    _require_auth(x_cr_auth_token)
    return {
        "activities": [
            {"action": "POLICY_RUN", "status": "COMPLETE", "timestamp": "2025-02-07T02:00:00Z"},
            {"action": "CYBERSENSE_SCAN", "status": "COMPLETE", "timestamp": "2025-02-07T02:15:00Z"},
            {"action": "VAULT_LOCK", "status": "COMPLETE", "timestamp": "2025-02-07T02:16:00Z"},
        ],
    }


# --- Utility: set scenario context ---

@app.post("/cr/v7/mock/scenario")
async def set_scenario(request: Request):
    """Mock-only endpoint to set the active scenario for analysis results."""
    global _current_scenario
    body = await request.json()
    _current_scenario = body.get("type", "ransomware")
    vault.reset()
    return {"scenario": _current_scenario, "vault_state": vault.state.value}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=14778, log_level="info")
