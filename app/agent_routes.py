"""FastAPI router for all agent endpoints.

Isolated from the core demo — remove the router include and the demo works unchanged.
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

from app.config import settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

agent_router = APIRouter(prefix="/api/agents", tags=["agents"])
page_router = APIRouter(tags=["agent-pages"])


# ── Director SSE endpoint ───────────────────────────────────────

@agent_router.get("/director/stream")
async def director_stream(scenario: str = "ransomware"):
    """Stream presenter cues from the Director agent via SSE."""
    from agents.director.agent import DirectorAgent

    director = DirectorAgent()

    async def event_generator():
        async for cue in director.stream_cues(scenario):
            yield {"data": json.dumps(cue)}

    return EventSourceResponse(event_generator())


# ── Scenarist API (two-phase: analyze → approve → generate) ──────

@agent_router.post("/scenarist/analyze")
async def scenarist_analyze(request: Request):
    """Phase 1: Research and propose — returns a proposal for user review."""
    from agents.scenarist.agent import ScenaristAgent

    body = await request.json()
    mode = body.get("mode", "search")
    topic = body.get("topic", "pharma cybersecurity attack")
    curated_text = body.get("curated_text", "")
    urls = body.get("urls", [])

    agent = ScenaristAgent()

    async def analyze_and_stream():
        yield {"data": json.dumps({"status": "running", "message": "Analyzing sources..."})}
        try:
            proposal = await agent.analyze(
                mode=mode, topic=topic, curated_text=curated_text, urls=urls,
            )
            yield {"data": json.dumps({"status": "proposal", "message": "Proposal ready", "result": proposal})}
        except Exception as e:
            logger.error(f"Scenarist analyze error: {e}")
            yield {"data": json.dumps({"status": "error", "message": str(e)})}

    return EventSourceResponse(analyze_and_stream())


@agent_router.post("/scenarist/generate")
async def scenarist_generate(request: Request):
    """Phase 2: Generate artifacts from an approved proposal."""
    from agents.scenarist.agent import ScenaristAgent

    body = await request.json()
    proposal = body.get("proposal", "")
    scenario_name = body.get("scenario_name", "")

    if not proposal:
        return {"status": "error", "message": "No proposal provided"}

    agent = ScenaristAgent()

    async def generate_and_stream():
        yield {"data": json.dumps({"status": "running", "message": "Generating scenario artifacts..."})}
        try:
            result = await agent.generate(proposal=proposal, scenario_name=scenario_name)
            yield {"data": json.dumps({"status": "complete", "message": "Scenario generated", "result": result})}
        except Exception as e:
            logger.error(f"Scenarist generate error: {e}")
            yield {"data": json.dumps({"status": "error", "message": str(e)})}

    return EventSourceResponse(generate_and_stream())


# ── Documentalist API ────────────────────────────────────────────

@agent_router.post("/documentalist/run")
async def documentalist_run(request: Request):
    """Run the Documentalist agent."""
    from agents.documentalist.agent import DocumentalistAgent

    body = await request.json()
    mode = body.get("mode", "code")
    scenario = body.get("scenario", "ransomware")

    agent = DocumentalistAgent()

    async def run_and_stream():
        yield {"data": json.dumps({"status": "running", "message": "Documentalist starting..."})}
        try:
            result = await agent.run(mode=mode, scenario=scenario)
            yield {"data": json.dumps({"status": "complete", "message": "Documentation generated", "result": result})}
        except Exception as e:
            logger.error(f"Documentalist error: {e}")
            yield {"data": json.dumps({"status": "error", "message": str(e)})}

    return EventSourceResponse(run_and_stream())


# ── Customer API ─────────────────────────────────────────────────

@agent_router.post("/customer/run")
async def customer_run(request: Request):
    """Run the Customer evaluator agent."""
    from agents.customer.agent import CustomerAgent

    body = await request.json()
    scenario = body.get("scenario", "ransomware")
    persona = body.get("persona", "all")

    agent = CustomerAgent()

    async def run_and_stream():
        yield {"data": json.dumps({"status": "running", "message": "Customer evaluation starting..."})}
        try:
            result = await agent.run(scenario=scenario, persona=persona)
            yield {"data": json.dumps({"status": "complete", "message": "Evaluation complete", "result": result})}
        except Exception as e:
            logger.error(f"Customer error: {e}")
            yield {"data": json.dumps({"status": "error", "message": str(e)})}

    return EventSourceResponse(run_and_stream())


# ── Recruiter API ────────────────────────────────────────────────

@agent_router.post("/recruiter/run")
async def recruiter_run(request: Request):
    """Run the Recruiter agent."""
    from agents.recruiter.agent import RecruiterAgent

    body = await request.json()
    company = body.get("company", "snowflake")
    mode = body.get("mode", "report")

    agent = RecruiterAgent()

    async def run_and_stream():
        yield {"data": json.dumps({"status": "running", "message": f"Recruiter ({company}) starting..."})}
        try:
            result = await agent.run(company=company, mode=mode)
            yield {"data": json.dumps({"status": "complete", "message": "Report generated", "result": result})}
        except Exception as e:
            logger.error(f"Recruiter error: {e}")
            yield {"data": json.dumps({"status": "error", "message": str(e)})}

    return EventSourceResponse(run_and_stream())


# ── Agent Pages ──────────────────────────────────────────────────

@page_router.get("/agents", response_class=HTMLResponse)
async def agents_hub(request: Request):
    return templates.TemplateResponse("agents/hub.html", {"request": request})


@page_router.get("/agents/scenarist", response_class=HTMLResponse)
async def agents_scenarist(request: Request):
    return templates.TemplateResponse("agents/scenarist.html", {"request": request})


@page_router.get("/agents/documentalist", response_class=HTMLResponse)
async def agents_documentalist(request: Request):
    return templates.TemplateResponse("agents/documentalist.html", {"request": request})


@page_router.get("/agents/customer", response_class=HTMLResponse)
async def agents_customer(request: Request):
    return templates.TemplateResponse("agents/customer.html", {"request": request})


@page_router.get("/agents/recruiter", response_class=HTMLResponse)
async def agents_recruiter(request: Request):
    return templates.TemplateResponse("agents/recruiter.html", {"request": request})
