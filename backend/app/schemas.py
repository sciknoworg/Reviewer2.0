from pydantic import BaseModel


class CriterionInfo(BaseModel):
    key: str
    synonyms: list[str]
    desc: str


class CriterionResult(BaseModel):
    text: str
    score: int
    bullets: list[str]


class ReviewResponse(BaseModel):
    title: str
    abstract: str
    reviews: dict[str, CriterionResult]
    overall_score: float
    recommendation: str
    meta_summary: str
