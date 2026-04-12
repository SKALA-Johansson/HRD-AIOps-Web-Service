import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tutor import TutorSession, Feedback, LearningActivity

logger = logging.getLogger(__name__)
from app.schemas.tutor import (
    TutorSessionRequest,
    TutorSessionResponse,
    ReferenceItem,
    GradingStatusResponse,
    FeedbackDetailResponse,
    QuizGradingRequest,
    AssignmentGradingRequest,
    FeedbackResponse,
    GrowthReportRequest,
    GrowthReportResponse,
)
from app.schemas.response import ApiResponse
from app.services.tutor_agent import ai_tutor_agent
from app.services.kafka_service import (
    publish_activity_logged,
    publish_anomaly_detected,
    publish_learning_completed,
)
from app.rag.qdrant_client import add_documents

router = APIRouter(prefix="/tutor", tags=["ai-tutor"])


def _feedback_to_response(f: Feedback) -> FeedbackResponse:
    return FeedbackResponse(
        id=f.id,
        session_id=f.session_id,
        employee_id=f.employee_id,
        feedback_type=f.feedback_type,
        score=f.score,
        max_score=f.max_score,
        passed=f.passed,
        summary=f.summary,
        strengths=f.get_strengths(),
        weaknesses=f.get_weaknesses(),
        recommendations=f.get_recommendations(),
        detail=f.detail,
        is_anomaly=f.is_anomaly,
        anomaly_type=f.anomaly_type,
        created_at=f.created_at,
    )


async def _run_grading(
    feedback_id: str,
    submission_data: dict,
    user_id: str,
    module_id: str | None,
    completion_type: str,
    curriculum_id: str | None = None,
    week_number: int | None = None,
):
    """백그라운드 채점 태스크"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            return

        result = await ai_tutor_agent.grade_assignment(
            assignment_title=submission_data.get("title", "과제"),
            assignment_description=submission_data.get("description", ""),
            student_submission=submission_data.get("submission", ""),
            rubric=submission_data.get("rubric"),
            max_score=submission_data.get("max_score", 100.0),
        )
        feedback.score = result.get("score")
        feedback.max_score = result.get("max_score")
        feedback.passed = result.get("passed")
        feedback.summary = result.get("summary")
        feedback.detail = result.get("detail")
        feedback.set_strengths(result.get("strengths", []))
        feedback.set_weaknesses(result.get("weaknesses", []))
        feedback.set_recommendations(result.get("recommendations", []))
        db.commit()

        try:
            await publish_learning_completed(
                user_id=user_id,
                module_id=module_id,
                completion_type=completion_type,
                score=feedback.score,
                max_score=feedback.max_score,
                passed=feedback.passed,
                curriculum_id=curriculum_id,
                week_number=week_number,
            )
        except Exception as e:
            logger.warning(f"[Kafka] 과제 완료 이벤트 발행 실패 (무시): {e}")
    finally:
        db.close()


# ══════════════════════════════════════════════════════════════════
#  18) AI 튜터 질문 - POST /tutor/sessions
#  api.md: {userId, curriculumId, question} → {sessionId, answer, references}
# ══════════════════════════════════════════════════════════════════

@router.post("/sessions")
async def ask_tutor(request: TutorSessionRequest, db: Session = Depends(get_db)):
    """
    api.md §18 - POST /tutor/sessions
    질문을 받아 RAG 기반 답변을 생성하고 세션에 저장합니다.
    """
    # 기존 활성 세션 재사용 (같은 userId+curriculumId), 없으면 새로 생성
    session = (
        db.query(TutorSession)
        .filter(
            TutorSession.employee_id == str(request.userId),
            TutorSession.curriculum_id == str(request.curriculumId),
            TutorSession.status == "active",
        )
        .order_by(TutorSession.started_at.desc())
        .first()
    )
    if session is None:
        session = TutorSession(
            employee_id=str(request.userId),
            employee_name=f"User_{request.userId}",
            curriculum_id=str(request.curriculumId),
            session_type="chat",
            status="active",
        )
        session.set_messages([])
        db.add(session)
        db.commit()
        db.refresh(session)

    conversation_history = session.get_messages()

    # RAG 검색 + AI 답변 생성 (단일 호출)
    answer, rag_sources = await ai_tutor_agent.chat(
        user_message=request.question,
        conversation_history=conversation_history,
        module_title=None,
    )

    session.add_message("user", request.question)
    session.add_message("assistant", answer)
    db.commit()

    await publish_activity_logged(
        employee_id=str(request.userId),
        session_id=session.id,
        activity_type="chat",
    )

    references = [
        ReferenceItem(title=src[:80] if len(src) > 80 else src, source="RAG")
        for src in rag_sources
    ]

    return ApiResponse.ok(
        data=TutorSessionResponse(sessionId=session.id, answer=answer, references=references),
        code="TUTOR-200",
        message="답변 생성 완료",
    )


# ══════════════════════════════════════════════════════════════════
#  19) 과제 자동 채점 요청 - POST /tutor/assignments/{submissionId}/grade
# ══════════════════════════════════════════════════════════════════

@router.post("/assignments/{submission_id}/grade")
async def grade_assignment_async(
    submission_id: str,
    background_tasks: BackgroundTasks,
    request: AssignmentGradingRequest,
    db: Session = Depends(get_db),
):
    """
    api.md §19 - POST /tutor/assignments/{submissionId}/grade
    비동기 채점을 시작하고 IN_PROGRESS 상태를 즉시 반환합니다.
    """
    # 세션 placeholder 생성
    session = TutorSession(
        employee_id="0",
        employee_name="system",
        session_type="assignment",
        status="active",
    )
    session.set_messages([])
    db.add(session)
    db.flush()

    feedback = Feedback(
        session_id=session.id,
        employee_id=request.user_id or "0",
        feedback_type="assignment_grading",
        summary="채점 진행 중",
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    submission_data = {
        "title": request.assignment_title,
        "description": request.assignment_description,
        "submission": request.student_submission,
        "rubric": request.rubric,
        "max_score": request.max_score,
    }
    background_tasks.add_task(
        _run_grading,
        feedback.id,
        submission_data,
        request.user_id or "0",
        request.module_id,
        "ASSIGNMENT",
        request.curriculum_id,
        request.week_number,
    )

    return ApiResponse.ok(
        data=GradingStatusResponse(gradingStatus="IN_PROGRESS"),
        code="TUTOR-202",
        message="자동 채점이 시작되었습니다.",
    )


class QuizGenerateRequest(BaseModel):
    module_id: Optional[str] = None
    module_title: str
    learning_objectives: list[str] = []
    content: str = ""
    num_questions: int = 4


class QuizSubmitRequest(BaseModel):
    user_id: Optional[str] = "0"
    module_id: Optional[str] = None
    curriculum_id: Optional[str] = None   # 주차 완료 감지에 필요
    week_number: Optional[int] = None     # 주차 완료 감지에 필요
    questions: list[dict]          # generate 때 받은 questions 전체 (correct_answer 포함)
    student_answers: list[str]     # 학생이 선택한 답 (A/B/C/D), 순서 대응


@router.post("/quizzes/generate")
async def generate_quiz(request: QuizGenerateRequest):
    """
    POST /tutor/quizzes/generate
    모듈 학습 목표 기반 객관식 퀴즈 문제를 생성합니다.
    """
    questions = await ai_tutor_agent.generate_quiz(
        module_title=request.module_title,
        learning_objectives=request.learning_objectives,
        content=request.content,
        num_questions=request.num_questions,
    )
    return ApiResponse.ok(
        data={
            "moduleId": request.module_id,
            "questions": questions,
        },
        code="TUTOR-200",
        message=f"퀴즈 {len(questions)}문제가 생성되었습니다.",
    )


@router.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    request: QuizSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    POST /tutor/quizzes/{quiz_id}/submit
    퀴즈 답안을 일괄 제출하고 즉시 채점 결과를 반환합니다.
    """
    result = await ai_tutor_agent.grade_quiz_batch(
        questions=request.questions,
        student_answers=request.student_answers,
        user_id=request.user_id or "0",
        module_id=request.module_id,
    )

    # 세션 + 피드백 기록
    session = TutorSession(
        employee_id=request.user_id or "0",
        employee_name=f"User_{request.user_id or '0'}",
        module_id=request.module_id,
        session_type="quiz",
        status="completed",
    )
    session.set_messages([])
    db.add(session)
    db.flush()

    feedback = Feedback(
        session_id=session.id,
        employee_id=request.user_id or "0",
        feedback_type="quiz_grading",
        score=result.get("total_score"),
        max_score=result.get("max_score"),
        passed=result.get("passed"),
        summary=result.get("summary"),
    )
    feedback.set_strengths([q["question"] for q in result["per_question"] if q["is_correct"]][:3])
    feedback.set_weaknesses([q["question"] for q in result["per_question"] if not q["is_correct"]][:3])
    db.add(feedback)
    db.commit()

    try:
        await publish_learning_completed(
            user_id=request.user_id or "0",
            module_id=request.module_id,
            completion_type="QUIZ",
            score=result.get("total_score"),
            max_score=result.get("max_score"),
            passed=result.get("passed"),
            curriculum_id=request.curriculum_id,
            week_number=request.week_number,
        )
    except Exception as e:
        logger.warning(f"[Kafka] 퀴즈 완료 이벤트 발행 실패 (무시): {e}")

    return ApiResponse.ok(
        data={
            "quizId": quiz_id,
            "score": result.get("total_score"),
            "maxScore": result.get("max_score"),
            "passed": result.get("passed"),
            "summary": result.get("summary"),
            "perQuestion": result.get("per_question", []),
            "feedbackId": feedback.id,
        },
        code="TUTOR-200",
        message="퀴즈 채점이 완료되었습니다.",
    )


@router.post("/quizzes/{quiz_id}/grade")
async def grade_quiz(
    quiz_id: str,
    request: QuizGradingRequest,
    db: Session = Depends(get_db),
):
    """
    퀴즈 즉시 채점 후 완료 이벤트를 발행합니다.
    """
    result = await ai_tutor_agent.grade_quiz(
        question=request.question,
        answer=request.answer,
        student_answer=request.student_answer,
        max_score=request.max_score,
    )

    session = TutorSession(
        employee_id=request.user_id or "0",
        employee_name=f"User_{request.user_id or '0'}",
        module_id=request.module_id,
        session_type="quiz",
        status="completed",
    )
    session.set_messages([])
    db.add(session)
    db.flush()

    feedback = Feedback(
        session_id=session.id,
        employee_id=request.user_id or "0",
        feedback_type="quiz_grading",
        score=result.get("score"),
        max_score=result.get("max_score"),
        passed=result.get("passed"),
        summary=result.get("summary"),
        detail=result.get("detail"),
    )
    feedback.set_strengths(result.get("strengths", []))
    feedback.set_weaknesses(result.get("weaknesses", []))
    feedback.set_recommendations(result.get("recommendations", []))
    db.add(feedback)
    db.commit()

    await publish_learning_completed(
        user_id=request.user_id or "0",
        module_id=request.module_id,
        completion_type="QUIZ",
        score=result.get("score"),
        max_score=result.get("max_score"),
        passed=result.get("passed"),
    )

    return ApiResponse.ok(
        data={
            "quizId": quiz_id,
            "score": result.get("score"),
            "passed": result.get("passed"),
            "feedbackId": feedback.id,
        },
        code="TUTOR-200",
        message="퀴즈 채점이 완료되었습니다.",
    )


# ══════════════════════════════════════════════════════════════════
#  20) 피드백 조회 - GET /tutor/feedback/{submissionId}
# ══════════════════════════════════════════════════════════════════

@router.get("/feedback/{submission_id}")
def get_feedback(submission_id: str, db: Session = Depends(get_db)):
    """
    api.md §20 - GET /tutor/feedback/{submissionId}
    submissionId = feedback.id
    """
    feedback = db.query(Feedback).filter(Feedback.id == submission_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return ApiResponse.ok(
        data=FeedbackDetailResponse(
            score=feedback.score or 0,
            strengths=feedback.get_strengths(),
            improvements=feedback.get_weaknesses(),
        ),
        code="TUTOR-200",
        message="피드백 조회 성공",
    )


# ══════════════════════════════════════════════════════════════════
#  21) 성장 리포트 조회 - GET /reports/users/{userId}
# ══════════════════════════════════════════════════════════════════

@router.get("/reports/users/{user_id}")
async def get_growth_report(user_id: str, period_days: int = 30, db: Session = Depends(get_db)):
    """api.md §21 - 개인 성장 리포트 조회"""
    since = datetime.utcnow() - timedelta(days=period_days)

    sessions = (
        db.query(TutorSession)
        .filter(TutorSession.employee_id == user_id, TutorSession.started_at >= since)
        .all()
    )
    activities = (
        db.query(LearningActivity)
        .filter(LearningActivity.employee_id == user_id, LearningActivity.logged_at >= since)
        .order_by(LearningActivity.logged_at.desc())
        .all()
    )
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.employee_id == user_id, Feedback.created_at >= since)
        .all()
    )
    scores = [f.score for f in feedbacks if f.score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    total_hours = sum(a.duration_minutes or 0 for a in activities) / 60

    report_data = await ai_tutor_agent.generate_growth_report(
        employee_name=f"User_{user_id}",
        period_days=period_days,
        total_sessions=len(sessions),
        total_learning_hours=total_hours,
        average_score=avg_score,
        recent_activities=[{"activity_type": a.activity_type, "module_id": a.module_id, "score": a.score, "duration_minutes": a.duration_minutes} for a in activities],
        recent_feedback=[{"feedback_type": f.feedback_type, "score": f.score, "passed": f.passed} for f in feedbacks],
    )

    return ApiResponse.ok(
        data={
            "reportId": hash(f"{user_id}{datetime.utcnow().date()}") % 100000,
            "userId": int(user_id) if user_id.isdigit() else user_id,
            "strengths": report_data.get("strengths", []),
            "weaknesses": report_data.get("weaknesses", []),
            "achievementMetrics": {"averageScore": avg_score, "totalSessions": len(sessions)},
        },
        code="REPORT-200",
        message="성장 리포트 조회 성공",
    )


# ══════════════════════════════════════════════════════════════════
#  주차별 성장 리포트 목록 조회
# ══════════════════════════════════════════════════════════════════

@router.get("/reports/users/{user_id}/weekly")
def get_weekly_reports(
    user_id: str,
    curriculum_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    GET /tutor/reports/users/{userId}/weekly
    사용자의 주차별 성장 리포트 목록을 최신순으로 반환합니다.
    curriculum_id 쿼리 파라미터로 필터 가능.
    """
    query = (
        db.query(Feedback, TutorSession)
        .join(TutorSession, Feedback.session_id == TutorSession.id)
        .filter(
            Feedback.employee_id == user_id,
            Feedback.feedback_type == "growth_report",
        )
    )
    if curriculum_id:
        query = query.filter(TutorSession.curriculum_id == curriculum_id)

    rows = query.order_by(Feedback.created_at.desc()).all()

    reports = [
        {
            "reportId": f.id,
            "weekTitle": s.module_title or "성장 리포트",
            "curriculumId": s.curriculum_id,
            "score": f.score,
            "summary": f.summary,
            "strengths": f.get_strengths(),
            "weaknesses": f.get_weaknesses(),
            "recommendations": f.get_recommendations(),
            "detail": f.detail,
            "createdAt": f.created_at.isoformat() if f.created_at else None,
        }
        for f, s in rows
    ]

    return ApiResponse.ok(
        data=reports,
        code="REPORT-200",
        message=f"주차별 성장 리포트 {len(reports)}건 조회 완료",
    )


# ══════════════════════════════════════════════════════════════════
#  HR용 퀴즈 리포트 목록 조회
# ══════════════════════════════════════════════════════════════════

@router.get("/reports/hr/users/{user_id}")
def get_hr_reports(
    user_id: str,
    curriculum_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    GET /tutor/reports/hr/users/{userId}
    HR가 특정 사원의 퀴즈·과제 AI 리포트를 최신순으로 조회합니다.
    """
    HR_REPORT_TYPES = ["quiz_hr_report", "assignment_hr_report", "growth_report"]

    query = (
        db.query(Feedback, TutorSession)
        .join(TutorSession, Feedback.session_id == TutorSession.id)
        .filter(
            Feedback.employee_id == user_id,
            Feedback.feedback_type.in_(HR_REPORT_TYPES),
        )
    )
    if curriculum_id:
        query = query.filter(TutorSession.curriculum_id == curriculum_id)

    rows = query.order_by(Feedback.created_at.desc()).all()

    TYPE_MAP = {
        "assignment_hr_report": "assignment",
        "quiz_hr_report": "quiz",
        "growth_report": "growth",
    }
    DEFAULT_TITLE_MAP = {
        "assignment_hr_report": "과제",
        "quiz_hr_report": "퀴즈",
        "growth_report": "주차 성장 리포트",
    }

    reports = [
        {
            "reportId": f.id,
            "reportType": TYPE_MAP.get(f.feedback_type, "quiz"),
            "moduleTitle": s.module_title or DEFAULT_TITLE_MAP.get(f.feedback_type, "리포트"),
            "moduleId": s.module_id,
            "curriculumId": s.curriculum_id,
            "score": f.score,
            "maxScore": f.max_score,
            "passed": f.passed,
            "summary": f.summary,
            "strengths": f.get_strengths(),
            "weaknesses": f.get_weaknesses(),
            "recommendations": f.get_recommendations(),
            "detail": f.detail,
            "createdAt": f.created_at.isoformat() if f.created_at else None,
        }
        for f, s in rows
    ]

    return ApiResponse.ok(
        data=reports,
        code="REPORT-200",
        message=f"HR 리포트 {len(reports)}건 조회 완료",
    )


# ══════════════════════════════════════════════════════════════════
#  이상 징후 탐지
# ══════════════════════════════════════════════════════════════════

@router.post("/anomaly/check/{employee_id}")
async def check_anomaly(employee_id: str, db: Session = Depends(get_db)):
    """학습 이상 징후를 즉시 점검합니다."""
    last = (
        db.query(LearningActivity)
        .filter(LearningActivity.employee_id == employee_id)
        .order_by(LearningActivity.logged_at.desc())
        .first()
    )
    recent_scores = [
        a.score for a in
        db.query(LearningActivity)
        .filter(LearningActivity.employee_id == employee_id, LearningActivity.score.isnot(None))
        .order_by(LearningActivity.logged_at.desc()).limit(5).all()
    ]
    recent_feedbacks = (
        db.query(Feedback)
        .filter(Feedback.employee_id == employee_id)
        .order_by(Feedback.created_at.desc()).limit(10).all()
    )
    consecutive_fails = sum(1 for fb in recent_feedbacks if fb.passed is False)

    anomaly = ai_tutor_agent.detect_anomaly(
        employee_id=employee_id,
        last_activity_at=last.logged_at if last else None,
        recent_scores=recent_scores,
        consecutive_fails=consecutive_fails,
    )

    if anomaly:
        await publish_anomaly_detected(
            employee_id=employee_id,
            anomaly_type=anomaly["anomaly_type"],
            description=anomaly["description"],
            severity=anomaly["severity"],
        )

    return ApiResponse.ok(
        data={"anomalyDetected": anomaly is not None, "anomaly": anomaly, "checkedAt": datetime.utcnow().isoformat()},
        code="COMMON-200",
        message="이상 징후 점검 완료",
    )


# ══════════════════════════════════════════════════════════════════
#  RAG 문서 업로드
# ══════════════════════════════════════════════════════════════════

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
