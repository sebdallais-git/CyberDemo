"""FastAPI application — CyberDemo dashboard.

ServiceNow + Dell Cyber Recovery integration demo for pharma cybersecurity.
"""

import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.models import ScenarioRequest
from app.orchestrator import run_scenario

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="CyberDemo",
    description="ServiceNow + Dell Cyber Recovery pharma demo",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ── Pages ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "dellcr_mode": settings.DELLCR_MODE,
        "snow_instance": settings.SNOW_INSTANCE_URL,
    })


@app.get("/teleprompter", response_class=HTMLResponse)
async def teleprompter(request: Request):
    return templates.TemplateResponse("teleprompter.html", {"request": request})


@app.get("/infrastructure", response_class=HTMLResponse)
async def infrastructure(request: Request):
    return templates.TemplateResponse("infrastructure.html", {"request": request})


@app.get("/infrastructure/ai", response_class=HTMLResponse)
async def infrastructure_ai(request: Request):
    return templates.TemplateResponse("infrastructure_ai.html", {"request": request})


# ── API ──────────────────────────────────────────────────────────────

@app.post("/api/scenario")
async def trigger_scenario(payload: ScenarioRequest):
    """Start a scenario and return SSE stream of step events."""
    return EventSourceResponse(run_scenario(payload.type))


@app.get("/api/status")
async def api_status():
    """Return connectivity status for ServiceNow and Dell CR."""
    from app.servicenow_client import snow_client
    from app.dellcr_client import dellcr_client
    from app.snowflake_client import snowflake_client

    snow_ok = await snow_client.is_available()
    dellcr_ok = await dellcr_client.is_available()
    sf_ok = await snowflake_client.is_available()

    return {
        "servicenow": {
            "available": snow_ok,
            "instance": settings.SNOW_INSTANCE_URL,
        },
        "dell_cr": {
            "available": dellcr_ok,
            "mode": settings.DELLCR_MODE,
            "url": settings.DELLCR_BASE_URL,
        },
        "snowflake": {
            "available": sf_ok,
            "account": settings.SNOWFLAKE_ACCOUNT,
            "database": settings.SNOWFLAKE_DATABASE,
        },
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "dellcr_mode": settings.DELLCR_MODE,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True,
    )
