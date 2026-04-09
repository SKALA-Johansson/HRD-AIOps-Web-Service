"""
신입 정보 PDF 업로드 → 파싱 → Qdrant 저장
POST /goals/ingest/pdf
"""
import io
import logging
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from app.rag.qdrant_client import add_documents
from app.schemas.response import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/goals/ingest", tags=["ingest"])

CHUNK_SIZE = 800    # 청크당 문자 수
CHUNK_OVERLAP = 100 # 청크 간 겹치는 문자 수


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """텍스트를 일정 크기로 분할 (슬라이딩 윈도우)"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 50]  # 너무 짧은 조각 제거


@router.post("/pdf")
async def ingest_pdf(
    file: UploadFile = File(..., description="신입 정보 PDF 파일"),
    employee_id: str = Form(default="", description="직원 ID (메타데이터용)"),
    employee_name: str = Form(default="", description="직원 이름 (메타데이터용)"),
    department: str = Form(default="", description="부서 (메타데이터용)"),
    role: str = Form(default="", description="직무 (메타데이터용)"),
):
    """
    신입 정보 PDF를 업로드하면 텍스트를 추출하여 Qdrant(employee_profiles)에 저장합니다.
    저장된 내용은 AI가 교육 목표를 설정할 때 RAG 참고 자료로 활용됩니다.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    # PDF 텍스트 추출
    try:
        reader = PdfReader(io.BytesIO(content))
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append((i + 1, text))
    except Exception as e:
        logger.error(f"[PDF] 파싱 실패: {e}")
        raise HTTPException(status_code=422, detail=f"PDF 파싱 실패: {e}")

    if not pages_text:
        raise HTTPException(status_code=422, detail="PDF에서 텍스트를 추출할 수 없습니다.")

    # 청킹
    chunks = []
    metadatas = []
    base_meta = {
        "source": file.filename,
        "employee_id": employee_id,
        "employee_name": employee_name,
        "department": department,
        "role": role,
        "type": "employee_profile",
    }

    for page_num, text in pages_text:
        for chunk in _chunk_text(text):
            chunks.append(chunk)
            metadatas.append({**base_meta, "page": page_num})

    # Qdrant 저장
    try:
        await add_documents(chunks, metadatas)
    except Exception as e:
        logger.error(f"[Qdrant] 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=f"벡터 DB 저장 실패: {e}")

    logger.info(f"[PDF Ingest] {file.filename} → {len(chunks)}개 청크 저장 완료")

    return ApiResponse.ok(
        data={
            "filename": file.filename,
            "total_pages": len(pages_text),
            "total_chunks": len(chunks),
            "employee_id": employee_id,
            "employee_name": employee_name,
        },
        code="INGEST-200",
        message=f"PDF 파싱 완료: {len(chunks)}개 청크가 벡터 DB에 저장되었습니다.",
    )
