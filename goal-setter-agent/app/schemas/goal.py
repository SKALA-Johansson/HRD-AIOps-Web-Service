from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LearningGoalItem(BaseModel):
    title: str
    description: str
    priority: str          # high / medium / low
    duration_weeks: int
    skills_to_learn: list[str]
    success_criteria: str


# ── REST API Request/Response ──────────────────────────────────────

class GoalGenerateRequest(BaseModel):
    """POST /goals/generate - api.md §5"""
    userId: int
    profileId: int


class GoalCreateRequest(BaseModel):
    """POST /goals - HR 수동 목표 정의 - api.md §7"""
    targetType: str          # INDIVIDUAL / GROUP
    company: Optional[str] = None
    jobFamily: Optional[str] = None
    title: str
    description: str


class GoalGeneratingResponse(BaseModel):
    """비동기 생성 접수 응답"""
    goalDraftId: int
    status: str = "GENERATING"


class GoalDetailResponse(BaseModel):
    """GET /goals/{goalId} 응답 - api.md §6"""
    goalId: str
    userId: int
    title: str
    description: str
    status: str


class GoalApproveRequest(BaseModel):
    action: str     # APPROVE / REJECT
    comment: Optional[str] = None


class GoalRejectRequest(BaseModel):
    rejected_by: str
    reason: str


# ── 내부 전체 정보 (서비스 내부용) ──────────────────────────────────

class GoalFullResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    department: str
    role: str
    career_level: str
    experience_years: int
    skills: list[str]
    goals: list[LearningGoalItem]
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
