from typing import Annotated, Literal

import httpx
from langchain_core.tools import tool

from app.config import settings
from app.core.tools import call_openai

SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
TAVILY_SEARCH_URL = "https://api.tavily.com/search"
MAX_REFERENCES = 25

CitationProvider = Literal["tavily", "semantic_scholar"]
DEFAULT_CITATION_PROVIDER: CitationProvider = "tavily"

_PARSE_FUNCTION = [{
    "name": "parsed_references",
    "description": "Return a list of parsed bibliography entries.",
    "parameters": {
        "type": "object",
        "properties": {
            "references": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "authors": {"type": "array", "items": {"type": "string"}},
                        "year": {"type": "string"},
                    },
                    "required": ["title"],
                },
            }
        },
        "required": ["references"],
    },
}]


def _fallback_extract_references(sections_data: dict) -> list[dict]:
    """Parse a References/Bibliography section's raw text via a one-shot LLM call.

    Only used when no GROBID-parsed bibliography is available (JSON uploads).
    """
    ref_body = None
    for section in sections_data["sections"]:
        if section["title"].strip().lower() in ("references", "bibliography"):
            ref_body = section["body"]
            break

    if not ref_body:
        return []

    prompt = f"""
Parse the following References section text from an academic paper into a
list of individual reference entries (title, authors, year).

{ref_body}
"""
    result = call_openai(
        messages=[{"role": "user", "content": prompt}],
        llm=settings.HEADER_EXTRACTOR_MODEL,
        function=_PARSE_FUNCTION,
        temperature=0,
    )
    return result.get("references", [])


def _semantic_scholar_lookup(title: str) -> str:
    headers = {}
    if settings.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY

    try:
        response = httpx.get(
            SEMANTIC_SCHOLAR_SEARCH_URL,
            params={"query": title, "fields": "title,year,venue,citationCount", "limit": 1},
            headers=headers,
            timeout=15.0,
        )
    except httpx.HTTPError as e:
        return f"Lookup failed: {e}"

    if response.status_code != 200:
        return f"Lookup failed with status {response.status_code}."

    data = response.json().get("data", [])
    if not data:
        return f"No matching paper found for '{title}'."

    paper = data[0]
    return (
        f"Found: \"{paper.get('title')}\" ({paper.get('year')}), "
        f"venue: {paper.get('venue') or 'unknown'}, citations: {paper.get('citationCount', 0)}"
    )


def _tavily_lookup(title: str) -> str:
    if not settings.TAVILY_API_KEY:
        return "Lookup failed: no Tavily API key configured."

    try:
        response = httpx.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": f'"{title}" academic paper',
                "max_results": 3,
            },
            timeout=15.0,
        )
    except httpx.HTTPError as e:
        return f"Lookup failed: {e}"

    if response.status_code != 200:
        return f"Lookup failed with status {response.status_code}."

    results = response.json().get("results", [])
    if not results:
        return f"No matching paper found for '{title}'."

    top = results[0]
    snippet = (top.get("content") or "").strip()
    if len(snippet) > 300:
        snippet = snippet[:300] + "..."
    return f"Found: \"{top.get('title')}\" - {top.get('url')}\n{snippet}"


def build_citation_tools(
    sections_data: dict,
    bibliography: list[dict],
    provider: CitationProvider = DEFAULT_CITATION_PROVIDER,
) -> list:
    """Build the reference-checking tools for one request.

    `provider` picks which backend `citation_lookup` uses to verify a
    reference (Tavily web search by default, or Semantic Scholar's API) --
    the tool's name and description stay the same either way, so the agent's
    instructions don't need to know which one is active.
    """
    references = bibliography or _fallback_extract_references(sections_data)
    references = references[:MAX_REFERENCES]

    @tool
    def list_references() -> str:
        """List the paper's parsed bibliography entries (title, authors, year)."""
        if not references:
            return "No references could be extracted from this paper."
        lines = []
        for i, r in enumerate(references, 1):
            authors = ", ".join(r.get("authors") or [])
            lines.append(f"{i}. {r.get('title', '')} ({r.get('year') or 'n.d.'}) - {authors}")
        return "\n".join(lines)

    @tool
    def citation_lookup(title: Annotated[str, "Title of the paper to look up"]) -> str:
        """Look up a referenced paper by title to verify it exists and check its basic metadata."""
        if provider == "semantic_scholar":
            return _semantic_scholar_lookup(title)
        return _tavily_lookup(title)

    return [list_references, citation_lookup]
