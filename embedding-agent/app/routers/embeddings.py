from fastapi import APIRouter, HTTPException
from app.schemas.embedding import EmbedDocumentsRequest, SearchRequest
from app.schemas.response import ApiResponse
from app.services.embedding_service import upsert_documents, search_similar

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


@router.post("/documents")
async def upload_documents(request: EmbedDocumentsRequest):
    try:
        result = upsert_documents(
            texts=request.texts,
            metadatas=request.metadatas,
            collection=request.collection,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 임베딩 저장 실패: {e}")

    return ApiResponse.ok(
        data=result,
        code="EMBED-200",
        message=f"{result['uploaded']}건 임베딩 저장 완료",
    )


@router.post("/search")
async def search_documents(request: SearchRequest):
    try:
        result = search_similar(
            query=request.query,
            k=request.k,
            collection=request.collection,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 검색 실패: {e}")

    return ApiResponse.ok(
        data=result,
        code="EMBED-200",
        message="유사도 검색 성공",
    )
