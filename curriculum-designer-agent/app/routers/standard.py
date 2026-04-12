"""
부서/역할별 정석(기준) 커리큘럼 관리
POST   /curriculums/standard          - 정석 커리큘럼 등록
GET    /curriculums/standard          - 목록 조회 (department, role, career_level 필터)
GET    /curriculums/standard/{id}     - 상세 조회
DELETE /curriculums/standard/{id}     - 비활성화
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.standard_curriculum import StandardCurriculum, StandardModule
from app.schemas.standard import StandardCurriculumCreate, StandardCurriculumResponse
from app.schemas.response import ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/curriculums/standard", tags=["standard-curriculum"])


@router.post("", status_code=201)
def create_standard_curriculum(request: StandardCurriculumCreate, db: Session = Depends(get_db)):
    """정석 커리큘럼 등록 (같은 department+role+career_level 조합 기존 항목은 비활성화)"""
    # 기존 활성 항목 비활성화
    existing = db.query(StandardCurriculum).filter(
        StandardCurriculum.department == request.department,
        StandardCurriculum.role == request.role,
        StandardCurriculum.career_level == request.career_level,
        StandardCurriculum.is_active == True,
    ).all()
    for sc in existing:
        sc.is_active = False

    sc = StandardCurriculum(
        department=request.department,
        role=request.role,
        career_level=request.career_level,
        title=request.title,
        description=request.description,
        total_weeks=request.total_weeks,
    )
    db.add(sc)
    db.flush()

    for mod_data in request.modules:
        mod = StandardModule(curriculum_id=sc.id, **mod_data.model_dump(exclude={"topics", "learning_objectives"}))
        mod.set_topics(mod_data.topics)
        mod.set_learning_objectives(mod_data.learning_objectives)
        db.add(mod)

    db.commit()
    db.refresh(sc)
    logger.info(f"[Standard] 정석 커리큘럼 등록: {sc.department}/{sc.role}/{sc.career_level}")

    return ApiResponse.created(
        data=_to_response(sc),
        code="STANDARD-201",
        message="정석 커리큘럼이 등록되었습니다.",
    )


@router.get("")
def list_standard_curriculums(
    department: str | None = None,
    role: str | None = None,
    career_level: str | None = None,
    db: Session = Depends(get_db),
):
    """정석 커리큘럼 목록 조회"""
    q = db.query(StandardCurriculum).filter(StandardCurriculum.is_active == True)
    if department:
        q = q.filter(StandardCurriculum.department == department)
    if role:
        q = q.filter(StandardCurriculum.role == role)
    if career_level:
        q = q.filter(StandardCurriculum.career_level == career_level)

    items = q.order_by(StandardCurriculum.department, StandardCurriculum.role).all()
    return ApiResponse.ok(
        data=[_to_response(sc) for sc in items],
        code="STANDARD-200",
        message=f"{len(items)}건 조회",
    )


@router.get("/{curriculum_id}")
def get_standard_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    sc = db.query(StandardCurriculum).filter(StandardCurriculum.id == curriculum_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="정석 커리큘럼을 찾을 수 없습니다.")
    return ApiResponse.ok(data=_to_response(sc), code="STANDARD-200", message="조회 성공")


@router.delete("/{curriculum_id}")
def deactivate_standard_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    sc = db.query(StandardCurriculum).filter(StandardCurriculum.id == curriculum_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="정석 커리큘럼을 찾을 수 없습니다.")
    sc.is_active = False
    db.commit()
    return ApiResponse.ok(data={"id": curriculum_id}, code="STANDARD-200", message="비활성화 완료")


def _to_response(sc: StandardCurriculum) -> dict:
    return {
        "id": sc.id,
        "department": sc.department,
        "role": sc.role,
        "career_level": sc.career_level,
        "title": sc.title,
        "description": sc.description,
        "total_weeks": sc.total_weeks,
        "is_active": sc.is_active,
        "modules": [
            {
                "id": m.id,
                "week_number": m.week_number,
                "title": m.title,
                "description": m.description,
                "topics": m.get_topics(),
                "learning_objectives": m.get_learning_objectives(),
                "estimated_hours": m.estimated_hours,
            }
            for m in sc.modules
        ],
        "created_at": sc.created_at,
        "updated_at": sc.updated_at,
    }
