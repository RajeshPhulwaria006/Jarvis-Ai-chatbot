
"""Web search tool for Jarvis using DuckDuckGo and LangChain."""

import json
import logging

from ddgs import DDGS
from langchain_core.tools import tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MAX_RESULTS = 5
MAX_QUERY_LENGTH = 400
MAX_SNIPPET_LENGTH = 1200

# make schema validation for web search tool
class WebSearchInput(BaseModel):
    query: str = Field(
        ...,
        description=(
            "The actual search terms or question to search "
            "on the web. Example: LangChain Python tools docs"
        ),
    )


@tool("web_search", args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """Search the web for current information.

    Use for recent events, documentation, factual questions,
    unfamiliar topics, and information that may have changed.
    Returns search-result titles, snippets, and source URLs.
    """
    query = query.strip()

    if not query:
        return json.dumps({
            "status": "error",
            "message": "Search query cannot be empty."
        })

    if len(query) > MAX_QUERY_LENGTH:
        return json.dumps({
            "status": "error",
            "message": f"Query must be at most {MAX_QUERY_LENGTH} characters."
        })

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_RESULTS))

        if not results:
            return json.dumps({
                "status": "no_results",
                "query": query,
                "results": []
            }, ensure_ascii=False)

        cleaned_results = []

        for item in results:
            title = item.get("title", "").strip()
            url = item.get("href", "").strip()
            snippet = item.get("body", "").strip()

            # Only accept results with an actual HTTP(S) URL.
            if not url.startswith(("https://", "http://")):
                continue

            cleaned_results.append({
                "title": title,
                "url": url,
                "snippet": snippet[:MAX_SNIPPET_LENGTH]
            })

        if not cleaned_results:
            return json.dumps({
                "status": "no_valid_results",
                "query": query,
                "results": []
            }, ensure_ascii=False)

        return json.dumps({
            "status": "success",
            "query": query,
            "count": len(cleaned_results),
            "results": cleaned_results
        }, ensure_ascii=False)

    except Exception:
        logger.exception("Web search failed")
        return json.dumps({
            "status": "error",
            "message": (
                "Web search failed. No verified search results "
                "are available. Try again later."
            )
        }, ensure_ascii=False)
