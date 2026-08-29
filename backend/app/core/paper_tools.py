from typing import Annotated

from langchain_core.tools import tool

from app.config import settings
from app.core.tools import call_openai

_MATCH_FUNCTION = [{
    "name": "matched_section",
    "description": "Identify which header index corresponds to a requested section.",
    "parameters": {
        "type": "object",
        "properties": {
            "index": {
                "type": "integer",
                "description": "1-based index of the best-matching header, or 0 if none match.",
            }
        },
        "required": ["index"],
    },
}]


def get_section_text(section_name: str, sections_data: dict) -> str:
    """Return the paper section whose header best matches section_name, or a not-found message."""
    headers = sections_data["headers"]
    sections = sections_data["sections"]

    if not sections:
        return "This paper has no detected sections."

    prompt = f"""
You are given a numbered list of section headers from an academic paper:
{headers}

Identify which header best corresponds to the "{section_name}" section.
Return the answer in this format: {{ "index": header-index }} (or 0 if none match).
"""
    result = call_openai(
        messages=[{"role": "user", "content": prompt}],
        llm=settings.HEADER_EXTRACTOR_MODEL,
        function=_MATCH_FUNCTION,
        temperature=0,
    )
    index = result.get("index", 0)
    if not index or index < 1 or index > len(sections):
        return f"No section matching '{section_name}' was found."
    return sections[index - 1]["body"]


def build_paper_tools(sections_data: dict) -> list:
    """
    Build the paper-inspection tools for one request, closing over that
    request's parsed sections so concurrent requests never share state.
    """

    @tool
    def list_headers() -> str:
        """List the section headers available in this paper, in order."""
        return sections_data["headers"] or "This paper has no detected section headers."

    @tool
    def get_section(section_name: Annotated[str, "Section to retrieve, e.g. 'methodology' or 'related work'"]) -> str:
        """Return the full text of the paper section that best matches the given name."""
        return get_section_text(section_name, sections_data)

    return [list_headers, get_section]
