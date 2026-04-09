from datetime import datetime
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.curriculum import Curriculum, Module
from app.schemas.curriculum import (
    CurriculumGenerateRequest,
    CurriculumUpdateRequest,
    CurriculumApproveRequest,
    CurriculumGeneratingResponse,
    CurriculumDetailResponse,
    ModuleSummary,
    ModuleResponse,
    CurriculumResponse,
)
from app.schemas.response import ApiResponse
from app.services.curriculum_agent import curriculum_designer_agent
from app.services.kafka_service import publish_event
from app.rag.qdrant_client import add_documents

router = APIRouter(prefix="/curriculums", tags=["curriculums"])


# ── 내부 헬퍼 ──────────────────────────────────────────────────────

def _to_detail(c: Curriculum) -> CurriculumDetailResponse:
    """api.md §9 응답 형식"""
    return CurriculumDetailResponse(
        curriculumId=c.id,
        goalId=c.goal_id,
        title=c.title,
        status=c.status.upper(),
        modules=[
            ModuleSummary(moduleId=m.id, week=m.week_number, title=m.title)
            for m in sorted(c.modules, key=lambda x: x.week_number)
        ],
    )


def _module_to_response(m: Module) -> ModuleResponse:
    return ModuleResponse(
        id=m.id,
        curriculum_id=m.curriculum_id,
        week_number=m.week_number,
        title=m.title,
        description=m.description,
        content=m.content,
        learning_objectives=m.get_learning_objectives(),
        resources=m.get_resources(),
        assignments=m.get_assignments(),
        estimated_hours=m.estimated_hours,
        created_at=m.created_at,
    )


async def _run_curriculum_generation(curriculum_id: str, goal_id: str):
    """
    백그라운드 태스크: Goal 정보로 커리큘럼 자동 생성
    실제 운영에서는 Goal Service HTTP 호출로 goal 정보 획득
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
        if not curriculum:
            return

        # Goal Service에서 목표 정보 가져오기 (현재는 기본값 사용)
        # TODO: GET http://goal-setter-agent:10021/goals/{goal_id}
        mock_goals = [{
            "title": "핵심 역량 강화",
            "description": "직무 필수 역량 개발",
            "priority": "high",
            "duration_weeks": 12,
            "skills_to_learn": [],
            "success_criteria": "실무 적용 가능 수준 도달",
        }]

        curriculum_data = await curriculum_designer_agent.design_curriculum(
            employee_name=curriculum.employee_name,
            department=curriculum.department,
            role=curriculum.role,
            career_level=curriculum.career_level,
            experience_years=0,
            skills=[],
            goals=mock_goals,
        )

        curriculum.title = curriculum_data.get("title", curriculum.title)
        curriculum.description = curriculum_data.get("description", "")
        curriculum.total_weeks = curriculum_data.get("total_weeks", 12)
        curriculum.status = "draft"

        for mod_data in curriculum_data.get("modules", []):
            module = Module(
                curriculum_id=curriculum.id,
                week_number=mod_data.get("week_number", 1),
                title=mod_data.get("title", ""),
                description=mod_data.get("description", ""),
                content=mod_data.get("content", ""),
                estimated_hours=mod_data.get("estimated_hours", 8),
            )
            module.set_learning_objectives(mod_data.get("learning_objectives", []))
            module.set_resources(mod_data.get("resources", []))
            module.set_assignments(mod_data.get("assignments", []))
            db.add(module)

        db.commit()

        await publish_event("Curriculum.Created", {
            "curriculum_id": curriculum.id,
            "goal_id": goal_id,
            "employee_id": curriculum.employee_id,
            "title": curriculum.title,
        })
    except Exception:
        curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
        if curriculum:
            curriculum.status = "error"
            db.commit()
    finally:
        db.close()


# ── 8) 커리큘럼 자동 생성 요청 ────────────────────────────────────────

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_curriculum(
    request: CurriculumGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    api.md §8 - POST /curriculums/generate
    비동기로 커리큘럼 생성을 시작하고 즉시 GENERATING 상태를 반환합니다.
    """
    curriculum = Curriculum(
        goal_id=str(request.goalId),
        employee_id="0",
        employee_name="TBD",
        department="TBD",
        role="TBD",
        career_level="junior",
        title="커리큘럼 생성 중...",
        total_weeks=12,
        status="generating",
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)

    background_tasks.add_task(_run_curriculum_generation, curriculum.id, str(request.goalId))

    return ApiResponse.created(
        data=CurriculumGeneratingResponse(
            curriculumId=hash(curriculum.id) % 100000,
            status="GENERATING",
        ),
        code="CURRICULUM-202",
        message="커리큘럼 생성 요청이 접수되었습니다.",
    )


# ── 9) 개인 커리큘럼 조회 ──────────────────────────────────────────────

@router.get("/{curriculum_id}")
def get_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    """api.md §9 - GET /curriculums/{curriculumId}"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return ApiResponse.ok(
        data=_to_detail(c),
        code="CURRICULUM-200",
        message="커리큘럼 조회 성공",
    )


# ── 10) 커리큘럼 수정 요청 ────────────────────────────────────────────

@router.put("/{curriculum_id}")
async def update_curriculum(curriculum_id: str, request: CurriculumUpdateRequest, db: Session = Depends(get_db)):
    """
    api.md §10 - PUT /curriculums/{curriculumId}
    제목 및 모듈 수동 수정 또는 AI 재생성
    """
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    if request.title:
        c.title = request.title

    if request.modules:
        # 명시된 모듈만 제목/순서 업데이트
        for mod_update in request.modules:
            mod_id = mod_update.get("moduleId")
            if mod_id:
                module = db.query(Module).filter(Module.id == mod_id, Module.curriculum_id == curriculum_id).first()
                if module:
                    if "title" in mod_update:
                        module.title = mod_update["title"]
                    if "week" in mod_update:
                        module.week_number = mod_update["week"]

    c.version += 1
    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)

    await publish_event("Curriculum.Revised", {
        "curriculum_id": c.id,
        "employee_id": c.employee_id,
        "version": c.version,
    })

    return ApiResponse.ok(
        data=_to_detail(c),
        code="CURRICULUM-200",
        message="커리큘럼이 수정되었습니다.",
    )


# ── 커리큘럼 승인 (api.md §12 - Approval Service 위임 가능) ─────────────

@router.post("/{curriculum_id}/approve")
async def approve_curriculum(curriculum_id: str, request: CurriculumApproveRequest, db: Session = Depends(get_db)):
    """커리큘럼 승인/반려 및 Curriculum.Approved 이벤트 발행"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    if c.status not in ("draft", "revised"):
        raise HTTPException(status_code=400, detail=f"Cannot process curriculum with status '{c.status}'")

    if request.action == "APPROVE":
        c.status = "approved"
        c.updated_at = datetime.utcnow()
        db.commit()
        await publish_event("Curriculum.Approved", {
            "curriculum_id": c.id,
            "goal_id": c.goal_id,
            "employee_id": c.employee_id,
            "approved_by": request.comment or "HR",
        })
        return ApiResponse.ok(
            data={"curriculumId": c.id, "status": "APPROVED"},
            code="CURRICULUM-200",
            message="커리큘럼이 승인되었습니다.",
        )
    elif request.action == "REJECT":
        c.status = "rejected"
        c.revision_note = request.comment
        c.updated_at = datetime.utcnow()
        db.commit()
        return ApiResponse.ok(
            data={"curriculumId": c.id, "status": "REJECTED"},
            code="CURRICULUM-200",
            message="커리큘럼이 반려되었습니다.",
        )
    else:
        raise HTTPException(status_code=400, detail="action must be APPROVE or REJECT")


# ── 직원별 커리큘럼 목록 조회 ────────────────────────────────────────

@router.get("/employee/{employee_id}")
def get_curriculums_by_employee(employee_id: str, db: Session = Depends(get_db)):
    cs = db.query(Curriculum).filter(Curriculum.employee_id == employee_id).all()
    return ApiResponse.ok(
        data=[_to_detail(c) for c in cs],
        code="CURRICULUM-200",
        message="커리큘럼 목록 조회 성공",
    )


# ── 모듈 콘텐츠 생성 ─────────────────────────────────────────────────

@router.get("/{curriculum_id}/modules/{module_id}/contents")
async def get_module_content(curriculum_id: str, module_id: str, db: Session = Depends(get_db)):
    """api.md §15 호환 - 학습 콘텐츠 조회 (RAG 기반 생성)"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    module = db.query(Module).filter(Module.id == module_id, Module.curriculum_id == curriculum_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    if not module.content:
        content = await curriculum_designer_agent.generate_module_content(
            module_title=module.title,
            learning_objectives=module.get_learning_objectives(),
            role=c.role,
            department=c.department,
        )
        module.content = content
        db.commit()

    return ApiResponse.ok(
        data=[{"contentId": module.id, "title": module.title, "type": "TEXT", "content": module.content}],
        code="LEARNING-200",
        message="학습 콘텐츠 조회 성공",
    )


# ── RAG 문서 업로드 ──────────────────────────────────────────────────

class RagUploadRequest(BaseModel):
    texts: list[str]
    metadatas: list[dict] | None = None


@router.post("/rag/documents")
async def upload_rag_documents(request: RagUploadRequest):
    await add_documents(request.texts, request.metadatas)
    return ApiResponse.ok(
        data={"uploaded": len(request.texts)},
        code="COMMON-200",
        message=f"{len(request.texts)}건의 문서가 업로드되었습니다.",
    )
