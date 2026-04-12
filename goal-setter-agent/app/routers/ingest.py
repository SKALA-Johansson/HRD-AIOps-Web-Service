"""
신입 정보 PDF 업로드 → LLM 프로필 파싱 → 교육 목표 자동 생성 → RDB 저장
POST /goals/ingest/pdf
"""
import io
import logging
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from app.database import SessionLocal
from app.models.goal import Goal
from app.schemas.response import ApiResponse
from app.services.goal_agent import goal_setter_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/goals/ingest", tags=["ingest"])


@router.post("/pdf")
async def ingest_pdf(
    file: UploadFile = File(..., description="신입 정보 PDF 파일"),
    employee_id: str = Form(default="", description="직원 ID"),
    employee_name: str = Form(default="", description="직원 이름 (없으면 LLM 추출)"),
    department: str = Form(default="", description="부서 (없으면 LLM 추출)"),
    role: str = Form(default="", description="직무 (없으면 LLM 추출)"),
):
    """
    백엔드로부터 신입사원 지원서 PDF를 수신합니다.

    처리 흐름:
    1. PDF 텍스트 추출 (pypdf)
    2. LLM으로 직원 프로필 파싱 (이름, 부서, 역할, 보유 스킬 등)
    3. 파싱된 프로필 기반으로 교육 목표 자동 생성
    4. RDB에 사원 보유 역량(콤마 구분) + 교육 목표 저장
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    # ── 1. PDF 텍스트 추출 ────────────────────────────────────────────
    try:
        reader = PdfReader(io.BytesIO(content))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n".join(t for t in pages_text if t.strip())
    except Exception as e:
        logger.error(f"[PDF] 파싱 실패: {e}")
        raise HTTPException(status_code=422, detail=f"PDF 파싱 실패: {e}")

    if not full_text.strip():
        raise HTTPException(status_code=422, detail="PDF에서 텍스트를 추출할 수 없습니다.")

    # ── 2. LLM으로 직원 프로필 파싱 ──────────────────────────────────
    try:
        extracted = await goal_setter_agent.extract_profile_from_pdf_text(full_text)
    except Exception as e:
        logger.error(f"[LLM] 프로필 추출 실패: {e}")
        raise HTTPException(status_code=500, detail=f"프로필 추출 실패: {e}")

    # Form 파라미터 우선, 없으면 LLM 추출값
    final_name       = employee_name or extracted.get("employee_name", "미상")
    final_department = department    or extracted.get("department", "미분류")
    final_role       = role          or extracted.get("role", "신입")
    final_level      = extracted.get("career_level", "junior")
    final_experience = extracted.get("experience_years", 0)
    final_skills     = extracted.get("skills", [])

    skills_csv = ",".join(s.strip() for s in final_skills if s.strip())

    logger.info(
        f"[Ingest] 프로필 확정: name={final_name}, dept={final_department}, "
        f"role={final_role}, skills={skills_csv}"
    )

    # ── 3. 교육 목표 자동 생성 ────────────────────────────────────────
    try:
        goals = await goal_setter_agent.generate_goals(
            employee_id=employee_id or "0",
            employee_name=final_name,
            department=final_department,
            role=final_role,
            career_level=final_level,
            experience_years=final_experience,
            skills=final_skills,
        )
    except Exception as e:
        logger.error(f"[LLM] 교육 목표 생성 실패: {e}")
        goals = []

    # ── 4. RDB 저장: 사원 보유 역량(콤마 구분) + 교육 목표 ────────────
    goal_id = None
    db = SessionLocal()
    try:
        goal_record = Goal(
            employee_id=employee_id or "0",
            employee_name=final_name,
            department=final_department,
            role=final_role,
            career_level=final_level,
            experience_years=final_experience,
            status="draft",
        )
        goal_record.skills = skills_csv   # 콤마 구분 문자열로 직접 저장
        goal_record.set_goals(goals)
        db.add(goal_record)
        db.commit()
        db.refresh(goal_record)
        goal_id = goal_record.id
        logger.info(f"[DB] Goal 저장 완료: goal_id={goal_id}, skills='{skills_csv}'")
    except Exception as e:
        logger.error(f"[DB] Goal 저장 실패: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {e}")
    finally:
        db.close()

    return ApiResponse.ok(
        data={
            "filename": file.filename,
            "goal_id": goal_id,
            "extracted_profile": {
                "employee_name": final_name,
                "department": final_department,
                "role": final_role,
                "career_level": final_level,
                "experience_years": final_experience,
                "skills": skills_csv,
            },
            "goals_generated": len(goals),
        },
        code="INGEST-200",
        message=f"PDF 처리 완료: 보유 역량 {len(final_skills)}개 저장, 교육 목표 {len(goals)}개 생성",
    )
