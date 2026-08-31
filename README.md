<p align="center">
<img width="150" src="frontend/assets/logo.png" alt="Reviewer2.0">
</p>

<div align="center">

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)]()
![Agentic AI](https://img.shields.io/badge/AI-Agentic_App-0A84FF?logo=ai&logoColor=white)
# Reviewer2.0: Ultimate Automated Nitpicker!

</div>

Reviewer2.0 reviews an academic paper (PDF or pre-parsed JSON) with a panel of independent AI reviewer agents — one per rubric, choosable per review — each reading the sections it needs (and, for citations, checking them against the real literature) before scoring it 1–10 with written justification and bullet notes. A supervisor agent then synthesizes the panel's findings into an overall recommendation. Reviews can be exported as Markdown or JSON.

## Rubrics

Originality, Soundness, Impact, Presentation, Positioning w.r.t Related Work, Reference & Citation Quality, Reproducibility & Artifacts, and Ethical Considerations & Broader Impact. Pick any subset per review.

## Architecture

- **`backend/`** — a FastAPI service. Each rubric is a [LangGraph](https://github.com/langchain-ai/langgraph) tool-using agent (`create_react_agent`) that decides for itself which paper sections to inspect; the reference-checker agent additionally verifies citations against the real literature via a user-selected lookup provider — Tavily web search (default) or Semantic Scholar. Selected agents run in parallel, then a supervisor LLM step synthesizes their findings. Results stream back over Server-Sent Events (`GET /api/criteria`, `POST /api/review`) so the frontend can show live per-agent progress instead of one long wait. PDF uploads are converted to structured text (and a parsed bibliography) via [GROBID](https://github.com/kermitt2/grobid); pre-parsed JSON uploads (`{"markdown": "..."}`) skip that step.
- **`frontend/`** — a static HTML/CSS/vanilla-JS app served by nginx. It lets you pick which rubrics to run, streams the live review panel's progress, and renders the results (with score gauges per rubric) — Markdown/JSON export is built client-side.
- **`grobid`** — the GROBID PDF-to-TEI-XML service, run as its own container.

## Running it

```bash
cp .env.example .env   # fill in OPENAI_KEY, REVIEWER_MODEL, HEADER_EXTRACTOR_MODEL
docker compose up --build
```

Then open `http://localhost:8080`. The backend API is at `http://localhost:8000`, GROBID at `http://localhost:8070`.

Note: the GROBID image is large and its first request after startup is slow while it loads its models — this is expected.

