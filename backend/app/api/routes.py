import json

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config import settings
from app.core.citation_tools import DEFAULT_CITATION_PROVIDER
from app.core.criteria import RUBRICS, RUBRICS_BY_KEY
from app.core.review_service import review_stream
from app.schemas import CriterionInfo

router = APIRouter(prefix="/api")

ALLOWED_EXTENSIONS = (".pdf", ".json")
CITATION_PROVIDERS = ("tavily", "semantic_scholar")


@router.get("/criteria", response_model=list[CriterionInfo])
def get_criteria():
    return RUBRICS


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


async def _stream_events(file_bytes: bytes, filename: str, selected_keys: list[str], citation_provider: str):
    async for event in review_stream(file_bytes, filename, selected_keys, citation_provider):
        yield _sse(event)


@router.post("/review")
async def post_review(
    file: UploadFile,
    rubrics: str = Form(""),
    citation_provider: str = Form(DEFAULT_CITATION_PROVIDER),
):
    filename = file.filename or ""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only .pdf or .json files are supported.")

    if citation_provider not in CITATION_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown citation_provider '{citation_provider}'. Must be one of: {', '.join(CITATION_PROVIDERS)}.",
        )

    file_bytes = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds the {settings.MAX_UPLOAD_MB}MB upload limit.")

    requested_keys = [k.strip() for k in rubrics.split(",") if k.strip()]
    selected_keys = requested_keys or [r["key"] for r in RUBRICS]

    unknown = [k for k in selected_keys if k not in RUBRICS_BY_KEY]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown rubric(s): {', '.join(unknown)}")

    return StreamingResponse(
        _stream_events(file_bytes, filename, selected_keys, citation_provider),
        media_type="text/event-stream",
    )
