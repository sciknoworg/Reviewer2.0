import asyncio
from typing import AsyncIterator

from app.core.agents import run_supervisor_synthesis, run_worker_agent
from app.core.citation_tools import DEFAULT_CITATION_PROVIDER, CitationProvider
from app.core.ingestion import ingest_paper, section_paper
from app.core.paper_tools import get_section_text
from app.schemas import CriterionResult


def _overall_recommendation(avg_score: float) -> str:
    if avg_score >= 8.5:
        return "Strong Accept"
    if avg_score >= 7.5:
        return "Accept"
    if avg_score >= 6.5:
        return "Weak Accept"
    if avg_score >= 5.5:
        return "Borderline"
    if avg_score >= 4.5:
        return "Weak Reject"
    return "Reject"


async def _run_and_tag(key: str, sections_data: dict, bibliography: list[dict], citation_provider: CitationProvider):
    try:
        result = await run_worker_agent(key, sections_data, bibliography, citation_provider)
        return key, result, None
    except Exception as e:
        return key, None, str(e)


async def review_stream(
    file_bytes: bytes,
    filename: str,
    selected_keys: list[str],
    citation_provider: CitationProvider = DEFAULT_CITATION_PROVIDER,
) -> AsyncIterator[dict]:
    """
    Run the full multi-agent review pipeline, yielding progress events as they
    happen so the caller can stream them (e.g. over SSE) instead of blocking
    until the whole review is done.
    """
    try:
        yield {"stage": "extracting"}
        markdown, bibliography = ingest_paper(file_bytes, filename)
        sections_data = section_paper(markdown)

        yield {"stage": "queued", "rubrics": selected_keys}

        tasks = [_run_and_tag(key, sections_data, bibliography, citation_provider) for key in selected_keys]

        results: dict[str, CriterionResult] = {}
        for coro in asyncio.as_completed(tasks):
            key, result, error = await coro
            if error:
                yield {"stage": "agent_error", "key": key, "message": error}
                continue
            results[key] = result
            yield {"stage": "agent_done", "key": key, "result": result.model_dump()}

        if not results:
            yield {"stage": "error", "message": "All rubric agents failed to produce a review."}
            return

        valid_scores = [r.score for r in results.values() if r.score > 0]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        recommendation = _overall_recommendation(avg_score) if valid_scores else "Unable to determine"

        yield {"stage": "synthesizing"}
        meta_summary = await run_supervisor_synthesis(results)

        # The title is the heading text of the paper's very first section (by
        # construction of both ingestion paths), not that section's body --
        # unlike every other section lookup, so it's read directly rather
        # than through get_section_text.
        sections_list = sections_data["sections"]
        title = sections_list[0]["title"].strip("* ") if sections_list else "Untitled"
        abstract = get_section_text("abstract", sections_data)

        yield {
            "stage": "complete",
            "result": {
                "title": title,
                "abstract": abstract,
                "reviews": {key: result.model_dump() for key, result in results.items()},
                "overall_score": round(avg_score, 2),
                "recommendation": recommendation,
                "meta_summary": meta_summary,
            },
        }
    except Exception as e:
        yield {"stage": "error", "message": str(e)}
