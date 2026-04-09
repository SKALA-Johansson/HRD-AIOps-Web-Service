from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── REST API Request ───────────────────────────────────────────────

class CurriculumGenerateRequest(BaseModel):
    """POST /curriculums/generate - api.md §8"""
    goalId: str


class CurriculumUpdateRequest(BaseModel):
    """PUT /curriculums/{curriculumId} - api.md §10"""
    title: Optional[str] = None
    modules: Optional[list[dict]] = None   # [{moduleId, week, title}, ...]


# ── REST API Response ──────────────────────────────────────────────

class CurriculumGeneratingResponse(BaseModel):
    """비동기 생성 접수 응답"""
    curriculumId: str
    status: str = "GENERATING"


class ModuleSummary(BaseModel):
    """api.md §9 modules 항목"""
    moduleId: str
    week: int
    title: str


class CurriculumDetailResponse(BaseModel):
    """GET /curriculums/{curriculumId} 응답 - api.md §9"""
    curriculumId: str
    goalId: str
    title: str
    status: str
    modules: list[ModuleSummary] = []


# ── 내부 전체 응답 (서비스 내부용) ────────────────────────────────────

class ModuleResponse(BaseModel):
    id: str
    curriculum_id: str
    week_number: int
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    learning_objectives: list[str]
    resources: list[str]
    assignments: list[str]
    estimated_hours: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CurriculumResponse(BaseModel):
    id: str
    goal_id: str
    employee_id: str
    employee_name: str
    department: str
    role: str
    career_level: str
    title: str
    description: Optional[str] = None
    total_weeks: int
    status: str
    revision_note: Optional[str] = None
    version: int
    modules: list[ModuleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CurriculumApproveRequest(BaseModel):
    action: str          # APPROVE / REJECT
    comment: Optional[str] = None
