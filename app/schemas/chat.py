from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    query: str
    top_k: int | None = Field(
        default=5, ge=1, le=20, description="Number of search results to return"
    )


class ChatResponse(BaseModel):
    reply: str
    context: list[str]


class AnalysisResponse(BaseModel):
    analysis: dict[str, Any]
    raw_results: list[dict[str, Any]]
    query: str
