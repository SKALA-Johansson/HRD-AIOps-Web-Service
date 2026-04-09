from pydantic import BaseModel, Field


class EmbedDocumentsRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1)
    metadatas: list[dict] | None = None
    collection: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(default=5, ge=1, le=20)
    collection: str | None = None


class SearchHit(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict
