from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── REST API Request ───────────────────────────────────────────────

class TutorSessionRequest(BaseModel):
    """POST /tutor/sessions - api.md §18 (질문+답변 통합)"""
    userId: str
    curriculumId: Optional[str] = "0"
    question: str


class AssignmentGradeRequest(BaseModel):
    """POST /tutor/assignments/{submissionId}/grade - api.md §19"""
    # submissionId는 path parameter
    pass


class QuizGradingRequest(BaseModel):
    user_id: Optional[str] = "0"
    module_id: Optional[str] = None
    question: str
    answer: str
    student_answer: str
    max_score: float = 100.0


class AssignmentGradingRequest(BaseModel):
    user_id: Optional[str] = "0"
    module_id: Optional[str] = None
    assignment_title: str
    assignment_description: str
    student_submission: str
    rubric: Optional[str] = None
    max_score: float = 100.0


class GrowthReportRequest(BaseModel):
    employee_id: str
    employee_name: str
    period_days: int = 30


# ── REST API Response ──────────────────────────────────────────────

class ReferenceItem(BaseModel):
    title: str
    source: str


class TutorSessionResponse(BaseModel):
    """POST /tutor/sessions 응답 - api.md §18"""
    sessionId: str
    answer: str
    references: list[ReferenceItem] = []


class GradingStatusResponse(BaseModel):
    """POST /tutor/assignments/{submissionId}/grade 응답 - api.md §19"""
    gradingStatus: str = "IN_PROGRESS"


class FeedbackDetailResponse(BaseModel):
    """GET /tutor/feedback/{submissionId} 응답 - api.md §20"""
    score: float
    strengths: list[str]
    improvements: list[str]


# ── 내부 전체 모델 (서비스 내부용) ────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    session_id: str
    employee_id: str
    feedback_type: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    passed: Optional[bool] = None
    summary: Optional[str] = None
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendations: list[str] = []
    detail: Optional[str] = None
    is_anomaly: bool = False
    anomaly_type: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    curriculum_id: Optional[str] = None
    module_id: Optional[str] = None
    module_title: Optional[str] = None
    session_type: str
    messages: list[ChatMessage] = []
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GrowthReportResponse(BaseModel):
    employee_id: str
    employee_name: str
    period_days: int
    total_sessions: int
    total_learning_hours: float
    average_score: float
    strengths: list[str]
    weaknesses: list[str]
    growth_trend: str
    recommendations: list[str]
    report_content: str
    generated_at: datetime
