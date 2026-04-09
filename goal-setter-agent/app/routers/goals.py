import asyncio
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.goal import Goal
from app.schemas.goal import (
    GoalGenerateRequest,
    GoalCreateRequest,
    GoalApproveRequest,
    GoalGeneratingResponse,
    GoalDetailResponse,
    GoalFullResponse,
)
from app.schemas.response import ApiResponse
from app.services.goal_agent import goal_setter_agent
from app.services.kafka_service import publish_goal_defined

router = APIRouter(prefix="/goals", tags=["goals"])


# ── 내부 헬퍼 ──────────────────────────────────────────────────────

def _to_detail(goal: Goal) -> GoalDetailResponse:
    """api.md §6 응답 형식"""
    goals_list = goal.get_goals()
    title = goals_list[0].get("title", "교육 목표") if goals_list else "교육 목표"
    desc = goals_list[0].get("description", "") if goals_list else ""
    return GoalDetailResponse(
        goalId=goal.id,
        userId=int(goal.employee_id) if goal.employee_id.isdigit() else 0,
        title=title,
        description=desc,
        status=goal.status.upper(),
    )


async def _run_goal_generation(goal_id: str, employee_id: str, profile_data: dict):
    """
    백그라운드 태스크: AI Agent로 목표 생성 후 DB 업데이트
    실제 운영에서는 profile service HTTP 호출로 profile_data 획득
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        goals = await goal_setter_agent.generate_goals(
            employee_id=employee_id,
            employee_name=profile_data.get("employee_name", f"User_{employee_id}"),
            department=profile_data.get("department", "미분류"),
            role=profile_data.get("desiredJob", profile_data.get("role", "신입")),
            career_level=profile_data.get("career_level", "junior"),
            experience_years=profile_data.get("experience_years", 0),
            skills=profile_data.get("skills", []),
        )
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if goal:
            goals_list = goals if isinstance(goals, list) else []
            title = goals_list[0].get("title", "맞춤형 교육 목표") if goals_list else "맞춤형 교육 목표"
            desc = goals_list[0].get("description", "") if goals_list else ""
            goal.set_goals(goals)
            goal.status = "draft"
            db.commit()
    except Exception as e:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if goal:
            goal.status = "error"
            db.commit()
    finally:
        db.close()


# ── 5) 개인 교육 목표 자동 생성 요청 ─────────────────────────────────

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_goals(
    request: GoalGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    api.md §5 - POST /goals/generate
    비동기로 목표 생성을 시작하고 goalDraftId와 GENERATING 상태를 즉시 반환합니다.
    """
    # Draft 레코드 먼저 생성 (status=generating)
    goal_record = Goal(
        employee_id=str(request.userId),
        employee_name=f"User_{request.userId}",
        department="TBD",
        role="TBD",
        career_level="junior",
        experience_years=0,
        status="generating",
    )
    goal_record.set_skills([])
    goal_record.set_goals([])
    db.add(goal_record)
    db.commit()
    db.refresh(goal_record)

    # 백그라운드에서 AI 생성 (실제로는 Profile Service HTTP 호출 후 profile_data 획득)
    profile_data = {"employee_name": f"User_{request.userId}", "profileId": request.profileId}
    background_tasks.add_task(_run_goal_generation, goal_record.id, str(request.userId), profile_data)

    return ApiResponse.created(
        data=GoalGeneratingResponse(goalDraftId=hash(goal_record.id) % 100000, status="GENERATING"),
        code="GOAL-202",
        message="교육 목표 생성 요청이 접수되었습니다.",
    )


# ── 6) 개인 교육 목표 조회 ───────────────────────────────────────────

@router.get("/{goal_id}")
def get_goal(goal_id: str, db: Session = Depends(get_db)):
    """api.md §6 - GET /goals/{goalId}"""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return ApiResponse.ok(data=_to_detail(goal), code="GOAL-200", message="교육 목표 조회 성공")


# ── 7) HR 교육 목표 수동 정의 ────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
def create_goal_manually(request: GoalCreateRequest, db: Session = Depends(get_db)):
    """api.md §7 - POST /goals (HR 수동 목표 정의)"""
    goal_record = Goal(
        employee_id="0",
        employee_name="HR",
        department=request.jobFamily or "ALL",
        role=request.jobFamily or "ALL",
        career_level="junior",
        experience_years=0,
        status="draft",
    )
    goal_record.set_skills([])
    goal_record.set_goals([{
        "title": request.title,
        "description": request.description,
        "priority": "high",
        "duration_weeks": 12,
        "skills_to_learn": [],
        "success_criteria": request.description,
    }])
    db.add(goal_record)
    db.commit()
    db.refresh(goal_record)
    return ApiResponse.created(
        data={"goalId": goal_record.id, "status": "DRAFT"},
        code="GOAL-201",
        message="교육 목표가 등록되었습니다.",
    )


# ── 목표 승인 (api.md §11 - Approval Service 위임 가능) ───────────────

@router.post("/{goal_id}/approve")
async def approve_goal(goal_id: str, request: GoalApproveRequest, db: Session = Depends(get_db)):
    """목표 승인/반려 처리 및 Goal.Defined 이벤트 발행"""
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.status not in ("draft", "generating"):
        raise HTTPException(status_code=400, detail=f"Cannot process goal with status '{goal.status}'")

    if request.action == "APPROVE":
        goal.status = "approved"
        goal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(goal)
        await publish_goal_defined({
            "id": goal.id,
            "employee_id": goal.employee_id,
            "employee_name": goal.employee_name,
            "department": goal.department,
            "role": goal.role,
            "career_level": goal.career_level,
            "experience_years": goal.experience_years,
            "skills": goal.get_skills(),
            "goals": goal.get_goals(),
        })
        return ApiResponse.ok(
            data={"goalId": goal.id, "status": "APPROVED"},
            code="GOAL-200",
            message="목표가 승인되었습니다.",
        )
    elif request.action == "REJECT":
        goal.status = "rejected"
        goal.rejection_reason = request.comment
        goal.updated_at = datetime.utcnow()
        db.commit()
        return ApiResponse.ok(
            data={"goalId": goal.id, "status": "REJECTED"},
            code="GOAL-200",
            message="목표가 반려되었습니다.",
        )
    else:
        raise HTTPException(status_code=400, detail="action must be APPROVE or REJECT")


# ── 내부용: 직원별 목표 목록 조회 ──────────────────────────────────────

@router.get("/employee/{employee_id}")
def get_goals_by_employee(employee_id: str, db: Session = Depends(get_db)):
    goals = db.query(Goal).filter(Goal.employee_id == employee_id).order_by(Goal.created_at.desc()).all()
    data = [_to_detail(g) for g in goals]
    return ApiResponse.ok(data=data, code="GOAL-200", message="목표 목록 조회 성공")
