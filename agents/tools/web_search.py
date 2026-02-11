"""Web search tool — Brave Search API + URL content fetcher.

Used by the Scenarist agent to find recent pharma cyber news
and fetch article content for scenario creation.
"""

import logging

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": (
        "Search the web for recent pharma cybersecurity news using Brave Search. "
        "Returns titles, URLs, and snippets. Use this to find real incidents "
        "as the basis for new scenario creation."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (e.g. 'pharma ransomware attack 2025')",
            },
            "count": {
                "type": "integer",
                "description": "Number of results (1-10, default 5)",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}

FETCH_URL_TOOL = {
    "name": "fetch_url",
    "description": (
        "Fetch the text content of a web page. Strips HTML and returns plain text. "
        "Use this after web_search to read full article content for scenario research."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL to fetch",
            },
        },
        "required": ["url"],
    },
}


async def handle_web_search(input: dict) -> str:
    """Search via Brave Search API."""
    if not settings.BRAVE_API_KEY:
        return "Error: BRAVE_API_KEY not configured. Use curated mode instead."

    query = input["query"]
    count = min(input.get("count", 5), 10)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": count},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": settings.BRAVE_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("web", {}).get("results", [])
    if not results:
        return "No results found."

    lines = []
    for r in results:
        lines.append(f"**{r.get('title', 'No title')}**")
        lines.append(f"URL: {r.get('url', '')}")
        lines.append(f"Snippet: {r.get('description', 'No description')}")
        lines.append("")

    return "\n".join(lines)


async def handle_fetch_url(input: dict) -> str:
    """Fetch and extract text content from a URL."""
    url = input["url"]

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "CyberDemo-Agent/1.0"})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script, style, nav, footer elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Truncate to avoid overwhelming the context
    if len(text) > 15000:
        text = text[:15000] + "\n\n... (truncated)"

    return text
