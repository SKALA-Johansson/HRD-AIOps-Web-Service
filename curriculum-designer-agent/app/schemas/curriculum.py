from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── REST API Request ───────────────────────────────────────────────

class CurriculumGenerateRequest(BaseModel):
    """POST /curriculums/generate - api.md §8"""
    goalId: str
    # 맞춤 커리큘럼 생성에 필요한 직원 정보 (있으면 정석 기반 개인화, 없으면 자유 생성)
    department: Optional[str] = None
    role: Optional[str] = None
    career_level: Optional[str] = "junior"
    employee_name: Optional[str] = None
    existing_skills: list[str] = Field(default_factory=list)      # 직원이 이미 보유한 스킬 목록


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


class SkillDecision(BaseModel):
    module_title: str
    action: str   # INCLUDE | EXCLUDE | ADVANCED
    reason: str


class SkillAnalysis(BaseModel):
    detected_skills: list[str] = Field(default_factory=list)
    decisions: list[SkillDecision] = Field(default_factory=list)


class CurriculumDetailResponse(BaseModel):
    """GET /curriculums/{curriculumId} 응답 - api.md §9"""
    curriculumId: str
    goalId: str
    employeeName: Optional[str] = None
    employeeId: Optional[str] = None
    department: Optional[str] = None
    title: str
    status: str
    modules: list[ModuleSummary] = Field(default_factory=list)
    existingSkills: list[str] = Field(default_factory=list)
    skillAnalysis: Optional[SkillAnalysis] = None


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
    modules: list[ModuleResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CurriculumApproveRequest(BaseModel):
    action: str          # APPROVE / REJECT
    comment: Optional[str] = None
