from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.core.citation_tools import DEFAULT_CITATION_PROVIDER, CitationProvider, build_citation_tools
from app.core.criteria import RUBRICS_BY_KEY
from app.core.paper_tools import build_paper_tools
from app.schemas import CriterionResult

_AGENT_SYSTEM_PREFIX = """
You are an expert academic peer reviewer. You have tools to inspect the paper
under review -- use them to gather the evidence you need before forming your
judgment; do not assume section content you have not actually retrieved.

{instructions}

When you are done:
1. Write a detailed analysis (3-5 paragraphs).
2. Assign a score from 1-10 (1 = very poor on this dimension, 10 = excellent).
3. List 2-3 key bullet points summarizing your assessment.
"""


def _make_llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.REVIEWER_MODEL, api_key=settings.OPENAI_KEY, temperature=0.3)


def build_worker_agent(
    rubric_key: str,
    sections_data: dict,
    bibliography: list[dict],
    citation_provider: CitationProvider = DEFAULT_CITATION_PROVIDER,
):
    """
    Build one rubric's tool-using worker agent for a single request. Agents
    are built fresh per request (not cached) because their tools close over
    that request's parsed paper data.
    """
    rubric = RUBRICS_BY_KEY[rubric_key]

    tools = build_paper_tools(sections_data)
    if rubric["needs_citation_tools"]:
        tools = tools + build_citation_tools(sections_data, bibliography, citation_provider)

    return create_react_agent(
        _make_llm(),
        tools=tools,
        prompt=_AGENT_SYSTEM_PREFIX.format(instructions=rubric["agent_instructions"]),
        response_format=CriterionResult,
    )


async def run_worker_agent(
    rubric_key: str,
    sections_data: dict,
    bibliography: list[dict],
    citation_provider: CitationProvider = DEFAULT_CITATION_PROVIDER,
) -> CriterionResult:
    agent = build_worker_agent(rubric_key, sections_data, bibliography, citation_provider)
    output = await agent.ainvoke({"messages": [("user", "Please conduct your review now.")]})
    return output["structured_response"]


_SYNTHESIS_PROMPT = """
You are the supervising editor for a set of independent peer reviews of the
same paper, each covering a different rubric. Read their findings below and
write a short (2-3 sentence) synthesis highlighting the most important
cross-cutting strengths and/or concerns. Do not restate every rubric's score;
focus on what matters most across the reviews as a whole.

{reviews_block}
"""


async def run_supervisor_synthesis(results: dict[str, CriterionResult]) -> str:
    reviews_block = "\n\n".join(
        f"## {key} (score: {result.score}/10)\n{result.text}"
        for key, result in results.items()
    )
    response = await _make_llm().ainvoke(_SYNTHESIS_PROMPT.format(reviews_block=reviews_block))
    return response.content
