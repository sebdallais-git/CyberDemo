"""7-step workflow engine for CyberDemo scenarios.

Orchestrates the full flow: detect → ServiceNow incident → Dell CR vault sync →
CyberSense analysis → forensics → recovery → ServiceNow resolution.
Emits SSE events for each step so the dashboard can update in real time.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional

from app.config import settings
from app.dellcr_client import dellcr_client
from app.events import publish
from app.models import SSEEvent, StepStatus, ScenarioType
from app.servicenow_client import snow_client
from app.snowflake_client import snowflake_client

logger = logging.getLogger(__name__)

# Shared pause gate — the orchestrator waits here between steps
# until the presenter clicks "Continue" in the UI.
_resume_event: Optional[asyncio.Event] = None


def get_resume_event() -> Optional[asyncio.Event]:
    """Return the current resume event (if a scenario is paused)."""
    return _resume_event

# Pharma scenario definitions (reused from PharmaOpsAgent concept)
SCENARIO_DETAILS = {
    ScenarioType.RANSOMWARE: {
        "short_description": "CRITICAL: Ransomware encrypting SCADA historian — production halted",
        "description": (
            "Ransomware detected on pharmaceutical SCADA systems. "
            "Batch records and temperature logs encrypted. "
            "Production line B3 halted. Immediate containment required."
        ),
        "priority": "1",
        "category": "Malware",
    },
    ScenarioType.AI_FACTORY: {
        "short_description": "CRITICAL: Nation-state intrusion on AI drug discovery pipeline",
        "description": (
            "Sophisticated intrusion targeting R&D AI pipeline. "
            "Stolen credentials used to access ML experiments and training data. "
            "Molecular simulation data corrupted, GPU compute halted. "
            "Phase III candidate BPX-7721 ($2.1B pipeline) at risk."
        ),
        "priority": "1",
        "category": "Intrusion",
    },
    ScenarioType.DATA_EXFIL: {
        "short_description": "CRITICAL: Intellectual property exfiltration — GxP and clinical data",
        "description": (
            "Slow exfiltration of GxP validation data and synthesis routes "
            "detected via covert DNS channel. 4.2 GB exfiltrated over 72 hours. "
            "Insider threat suspected — compromised service account."
        ),
        "priority": "1",
        "category": "Data Theft",
    },
}


def _sse(step: int, name: str, status: StepStatus, message: str, data: dict = None) -> dict:
    """Build an SSE event dict. EventSourceResponse handles the wire format."""
    event = SSEEvent(
        step=step,
        name=name,
        status=status,
        message=message,
        data=data or {},
    )
    return {"data": event.model_dump_json()}


async def _emit(step: int, name: str, status: StepStatus, message: str, data: dict = None) -> dict:
    """Build an SSE event and publish to the internal event bus (for Director).

    Returns the SSE dict so callers can yield it directly:
        yield await _emit(1, "DETECT", StepStatus.RUNNING, "Scanning...")
    """
    sse = _sse(step, name, status, message, data)
    await publish({"step": step, "name": name, "status": status.value, "message": message, "data": data or {}})
    return sse


async def run_scenario(scenario_type: ScenarioType) -> AsyncGenerator[str, None]:
    """Execute the full 7-step demo workflow, yielding SSE events.

    Steps:
    1. DETECT     — Generate threat details
    2. INCIDENT   — Create real ServiceNow security incident
    3. VAULT SYNC — Trigger Dell CR replication policy
    4. CYBERSENSE — Run ML analysis on vault copy
    5. FORENSICS  — Extract corrupted files and attack vector
    6. RECOVER    — Initiate recovery from clean PIT copy
    7. RESOLVE    — Update ServiceNow incident to resolved

    Every step pauses and waits for the presenter to click "Continue".
    """
    global _resume_event
    details = SCENARIO_DETAILS[scenario_type]
    incident_sys_id = None
    incident_number = "MOCK-INC-001"
    incident_url = ""
    analysis_data = {}
    pit_id = "pit-2025-0207-0200"

    # ── Step 1: DETECT (Snowflake AI) ─────────────────────────────
    snowflake_data = {}
    yield await _emit(1, "DETECT", StepStatus.RUNNING,
               "Snowflake AI scanning SIEM telemetry — querying anomaly models...")
    try:
        # Swap in scenario-specific SIEM data before querying
        await snowflake_client.swap_scenario_data(scenario_type.value)
        snowflake_data = await snowflake_client.run_anomaly_detection()
        max_score = snowflake_data.get("max_threat_score", 0)
        threat_count = snowflake_data.get("threat_count", 0)
        primary = snowflake_data.get("primary_host", "unknown")
        yield await _emit(1, "DETECT", StepStatus.COMPLETE,
                   f"Snowflake AI: THREAT DETECTED — {primary} score {max_score}/10 "
                   f"({threat_count} anomalous hosts)",
                   {
                       "category": details["category"],
                       "priority": details["priority"],
                       "source": "snowflake",
                       "threat_score": max_score,
                       "threat_count": threat_count,
                       "primary_host": primary,
                       "summary": snowflake_data.get("summary", {}),
                       "threats": snowflake_data.get("threats", []),
                       "model_version": snowflake_data.get("model_version", ""),
                   })
    except Exception as e:
        logger.error(f"Snowflake detection error: {e}")
        await asyncio.sleep(1.5)
        yield await _emit(1, "DETECT", StepStatus.COMPLETE,
                   f"Detected: {details['short_description']}",
                   {"category": details["category"], "priority": details["priority"],
                    "source": "fallback"})

    # ── PAUSE after Step 1 — open Snowflake workspace ──
    _resume_event = asyncio.Event()
    sf_url = settings.SNOWFLAKE_WORKSHEET_URL or "/snowflake"
    pause_data = {"pause_type": "snowflake", "pause_url": sf_url}
    if scenario_type == ScenarioType.AI_FACTORY and settings.DATABRICKS_HOST:
        pause_data["databricks_url"] = f"https://{settings.DATABRICKS_HOST}/explore/data/rd_pharma"
    yield await _emit(1, "PAUSE", StepStatus.COMPLETE,
               "Paused — view Snowflake threat analysis, then continue",
               pause_data)
    try:
        await _resume_event.wait()
    finally:
        _resume_event = None

    # ── Step 2: INCIDENT ────────────────────────────────────────────
    yield await _emit(2, "INCIDENT", StepStatus.RUNNING, "Creating ServiceNow Security Incident...")
    try:
        snow_available = await snow_client.is_available()
        if snow_available:
            result = await snow_client.create_security_incident({
                "short_description": details["short_description"],
                "description": details["description"],
                "impact": "1",    # 1 = High (enterprise-wide)
                "urgency": "1",   # 1 = High (immediate)
                "priority": details["priority"],
                "category": details["category"],
                "state": "1",  # New
            })
            incident_sys_id = result.get("sys_id", "")
            incident_number = result.get("number", "INC-UNKNOWN")
            incident_url = f"{settings.SNOW_INSTANCE_URL}/incident.do?sys_id={incident_sys_id}"
            yield await _emit(2, "INCIDENT", StepStatus.COMPLETE,
                       f"ServiceNow incident {incident_number} created (REAL)",
                       {"sys_id": incident_sys_id, "number": incident_number,
                        "url": incident_url, "mode": "live"})
        else:
            # ServiceNow not reachable — use mock data
            await asyncio.sleep(1.0)
            incident_number = "INC0000000"
            yield await _emit(2, "INCIDENT", StepStatus.COMPLETE,
                       f"ServiceNow incident {incident_number} created (MOCK)",
                       {"sys_id": "mock-sys-id", "number": incident_number,
                        "url": "", "mode": "mock"})
    except Exception as e:
        logger.error(f"ServiceNow error: {e}")
        await asyncio.sleep(1.0)
        incident_number = "SIR0010042"
        yield await _emit(2, "INCIDENT", StepStatus.COMPLETE,
                   f"ServiceNow incident {incident_number} created (MOCK - SN unavailable)",
                   {"number": incident_number, "mode": "mock", "error": str(e)})

    # ── PAUSE after Step 2 — open ServiceNow incident ──
    _resume_event = asyncio.Event()
    sn_pause_url = incident_url or f"{settings.SNOW_INSTANCE_URL}/now/nav/ui/classic/params/target/incident_list.do"
    yield await _emit(2, "PAUSE", StepStatus.COMPLETE,
               "Paused — review incident in ServiceNow, then continue",
               {"pause_type": "servicenow", "pause_url": sn_pause_url,
                "number": incident_number})
    try:
        await _resume_event.wait()
    finally:
        _resume_event = None

    # ── Step 3: VAULT SYNC ──────────────────────────────────────────
    yield await _emit(3, "VAULT SYNC", StepStatus.RUNNING,
               "Opening air gap — replicating to cyber vault...")
    try:
        # If mock mode, set the scenario on the mock server
        if settings.DELLCR_MODE == "mock":
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{settings.DELLCR_BASE_URL}/cr/v7/mock/scenario",
                    json={"type": scenario_type.value},
                )

        await dellcr_client.login()
        policy_result = await dellcr_client.trigger_policy("policy-pharma-daily-01")
        # Wait for sync to complete (poll system status)
        for _ in range(20):
            await asyncio.sleep(0.5)
            status = await dellcr_client.get_system_status()
            if status.get("vault_state") != "SYNCING":
                break

        yield await _emit(3, "VAULT SYNC", StepStatus.COMPLETE,
                   "Air gap closed — data replicated to vault",
                   {"vault_state": "LOCKED", "policy": "PharmaProd-Daily-Replication"})
    except Exception as e:
        logger.error(f"Dell CR sync error: {e}")
        await asyncio.sleep(3.0)
        yield await _emit(3, "VAULT SYNC", StepStatus.COMPLETE,
                   "Vault sync complete (simulated)",
                   {"vault_state": "LOCKED", "error": str(e)})

    # ── PAUSE after Step 3 ──
    _resume_event = asyncio.Event()
    yield await _emit(3, "PAUSE", StepStatus.COMPLETE,
               "Vault sealed — click to continue",
               {"pause_type": "continue"})
    try:
        await _resume_event.wait()
    finally:
        _resume_event = None

    # ── Step 4: CYBERSENSE ──────────────────────────────────────────
    yield await _emit(4, "CYBERSENSE", StepStatus.RUNNING,
               "CyberSense ML analysis scanning vault copy...")
    try:
        analysis_data = await dellcr_client.run_cybersense("sandbox-pharma-01")
        confidence = analysis_data.get("confidence", 99.99)
        yield await _emit(4, "CYBERSENSE", StepStatus.COMPLETE,
                   f"CyberSense: CORRUPTION DETECTED ({confidence}% confidence)",
                   {"confidence": confidence, "verdict": "CORRUPTION_DETECTED"})
    except Exception as e:
        logger.error(f"CyberSense error: {e}")
        await asyncio.sleep(5.0)
        analysis_data = {"confidence": 99.99, "corrupted_files": [], "recovery_recommendation": {}}
        yield await _emit(4, "CYBERSENSE", StepStatus.COMPLETE,
                   "CyberSense: CORRUPTION DETECTED (99.99% confidence, simulated)",
                   {"confidence": 99.99})

    # ── PAUSE after Step 4 ──
    _resume_event = asyncio.Event()
    yield await _emit(4, "PAUSE", StepStatus.COMPLETE,
               "Corruption confirmed — click to continue",
               {"pause_type": "continue"})
    try:
        await _resume_event.wait()
    finally:
        _resume_event = None

    # ── Step 5: FORENSICS ───────────────────────────────────────────
    yield await _emit(5, "FORENSICS", StepStatus.RUNNING, "Extracting forensic data...")
    await asyncio.sleep(5.0)

    corrupted = analysis_data.get("corrupted_files", [])
    classification = analysis_data.get("attack_classification", {})
    recovery_rec = analysis_data.get("recovery_recommendation", {})
    pit_id = recovery_rec.get("pit_id", pit_id)

    yield await _emit(5, "FORENSICS", StepStatus.COMPLETE,
               f"Forensics complete: {len(corrupted)} corrupted files identified",
               {
                   "corrupted_count": len(corrupted),
                   "attack_vector": classification.get("vector", details["category"]),
                   "family": classification.get("family", "Unknown"),
                   "clean_pit": pit_id,
                   "affected_systems": analysis_data.get("affected_systems", []),
               })

    # Add Snowflake detection work note to ServiceNow
    if incident_sys_id and snowflake_data:
        try:
            sf_summary = snowflake_data.get("summary", {})
            sf_threats = snowflake_data.get("threats", [])
            sf_note = (
                f"[Snowflake AI Threat Detection Report]\n"
                f"Engine: {snowflake_data.get('query_engine', 'N/A')}\n"
                f"Model: {snowflake_data.get('model_version', 'N/A')}\n"
                f"Events analyzed: {sf_summary.get('total_network_events', 0)} network + "
                f"{sf_summary.get('total_endpoint_events', 0)} endpoint\n"
                f"Critical detections: {sf_summary.get('critical_detections', 0)}\n"
                f"Anomalous hosts: {snowflake_data.get('threat_count', 0)}\n"
            )
            for t in sf_threats[:3]:
                sf_note += (
                    f"\n  Host: {t['hostname']} ({t['ip']}) — "
                    f"Score: {t['threat_score']}/10 [{t['anomaly_label']}]"
                )
            await snow_client.add_work_note(incident_sys_id, sf_note)
        except Exception as e:
            logger.error(f"ServiceNow Snowflake note error: {e}")

    # Add Dell CyberSense forensic work note to ServiceNow
    if incident_sys_id:
        try:
            forensic_note = (
                f"[Dell CyberSense Forensic Report]\n"
                f"Confidence: {analysis_data.get('confidence', 99.99)}%\n"
                f"Corrupted files: {len(corrupted)}\n"
                f"Attack vector: {classification.get('vector', 'N/A')}\n"
                f"Family: {classification.get('family', 'N/A')}\n"
                f"Clean PIT: {pit_id}"
            )
            await snow_client.add_work_note(incident_sys_id, forensic_note)
        except Exception as e:
            logger.error(f"ServiceNow work note error: {e}")

    # ── PAUSE after Step 5 ──
    _resume_event = asyncio.Event()
    yield await _emit(5, "PAUSE", StepStatus.COMPLETE,
               "Forensics complete — click to begin recovery",
               {"pause_type": "continue"})
    try:
        await _resume_event.wait()
    finally:
        _resume_event = None

    # ── Step 6: RECOVER ─────────────────────────────────────────────
    yield await _emit(6, "RECOVER", StepStatus.RUNNING,
               f"Restoring from clean PIT copy {pit_id}...")
    try:
        recovery_result = await dellcr_client.initiate_recovery(pit_id)
        restored_files = recovery_result.get("restored_files", 1704)
        yield await _emit(6, "RECOVER", StepStatus.COMPLETE,
                   f"Recovery complete: {restored_files} files restored from clean copy",
                   {"pit_id": pit_id, "restored_files": restored_files})
    except Exception as e:
        logger.error(f"Recovery error: {e}")
        await asyncio.sleep(4.0)
        yield await _emit(6, "RECOVER", StepStatus.COMPLETE,
                   "Recovery complete: 1704 files restored (simulated)",
                   {"pit_id": pit_id, "restored_files": 1704})

    # ── PAUSE after Step 6 ──
    _resume_event = asyncio.Event()
    yield await _emit(6, "PAUSE", StepStatus.COMPLETE,
               "Recovery complete — click to resolve incident",
               {"pause_type": "continue"})
    try:
        await _resume_event.wait()
    finally:
        _resume_event = None

    # ── Step 7: RESOLVE ─────────────────────────────────────────────
    yield await _emit(7, "RESOLVE", StepStatus.RUNNING,
               "Updating ServiceNow incident to resolved...")
    try:
        if incident_sys_id:
            resolution_notes = (
                f"Incident resolved via Dell Cyber Recovery automated workflow.\n"
                f"Recovery from PIT: {pit_id}\n"
                f"Files restored: {recovery_result.get('restored_files', 1704)}\n"
                f"CyberSense confidence: {analysis_data.get('confidence', 99.99)}%\n"
                f"All systems verified clean and operational."
            )
            await snow_client.resolve_incident(incident_sys_id, resolution_notes)
            yield await _emit(7, "RESOLVE", StepStatus.COMPLETE,
                       f"ServiceNow {incident_number} resolved with forensic report (REAL)",
                       {"number": incident_number, "state": "Resolved", "mode": "live"})
        else:
            await asyncio.sleep(1.5)
            yield await _emit(7, "RESOLVE", StepStatus.COMPLETE,
                       f"ServiceNow {incident_number} resolved with forensic report (MOCK)",
                       {"number": incident_number, "state": "Resolved", "mode": "mock"})
    except Exception as e:
        logger.error(f"ServiceNow resolve error: {e}")
        await asyncio.sleep(1.5)
        yield await _emit(7, "RESOLVE", StepStatus.COMPLETE,
                   f"Incident {incident_number} resolved (MOCK - SN unavailable)",
                   {"number": incident_number, "state": "Resolved", "mode": "mock"})

    # Final event — scenario complete with Dell closing message
    yield await _emit(7, "COMPLETE", StepStatus.COMPLETE,
               "All systems restored. Business continuity secured.",
               {
                   "scenario": scenario_type.value,
                   "incident": incident_number,
                   "closing": (
                       "This is what Zero Trust Cyber Recovery delivers: "
                       "peace of mind for the CISO, a proven recovery plan for the CIO, "
                       "and business continuity for the lines of business. "
                       "It pays for itself the day you need it — and every day you sleep soundly because it's there. "
                       "Let's talk about enabling this for your key business areas."
                   ),
               })
