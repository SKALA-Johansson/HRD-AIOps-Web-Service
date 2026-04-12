"""
Kafka Consumer/Producer
- 소비: learning-logs (Learning.ActivityLogged, Learning.AnomalyDetected)
- 발행: learning-logs (Learning.ActivityLogged, Learning.AnomalyDetected)
"""
import json
import asyncio
import logging
from datetime import datetime
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.config import settings

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        )
        await _producer.start()
    return _producer


async def stop_producer():
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None


async def publish_event(event_type: str, payload: dict):
    """learning-logs 토픽으로 이벤트 발행"""
    producer = await get_producer()
    event = {
        "event_type": event_type,
        "event_id": payload.get("session_id", payload.get("employee_id", "")),
        "timestamp": datetime.utcnow().isoformat(),
        "source": settings.SERVICE_NAME,
        "payload": payload,
    }
    await producer.send(settings.KAFKA_PRODUCE_TOPIC, value=event)
    logger.info(f"[Kafka] {event_type} 발행: {event['event_id']}")


async def publish_activity_logged(
    employee_id: str,
    session_id: str,
    activity_type: str,
    module_id: str | None = None,
    score: float | None = None,
    duration_minutes: int | None = None,
):
    """Learning.ActivityLogged 이벤트 발행"""
    await publish_event("Learning.ActivityLogged", {
        "employee_id": employee_id,
        "session_id": session_id,
        "activity_type": activity_type,
        "module_id": module_id,
        "score": score,
        "duration_minutes": duration_minutes,
        "logged_at": datetime.utcnow().isoformat(),
    })


async def publish_anomaly_detected(
    employee_id: str,
    anomaly_type: str,
    description: str,
    severity: str,
):
    """Learning.AnomalyDetected 이벤트 발행"""
    await publish_event("Learning.AnomalyDetected", {
        "employee_id": employee_id,
        "anomaly_type": anomaly_type,
        "description": description,
        "severity": severity,
        "detected_at": datetime.utcnow().isoformat(),
    })


async def publish_learning_completed(
    user_id: str,
    module_id: str | None,
    completion_type: str,
    score: float | None = None,
    max_score: float | None = None,
    passed: bool | None = None,
    curriculum_id: str | None = None,
    week_number: int | None = None,
):
    """
    완료 이벤트 발행
    - completion_type: "ASSIGNMENT" | "QUIZ"
    - curriculum_id, week_number: 주차 완료 감지에 필요
    """
    event_type = "Learning.AssignmentCompleted" if completion_type == "ASSIGNMENT" else "Learning.QuizCompleted"
    await publish_event(event_type, {
        "user_id": user_id,
        "module_id": module_id,
        "curriculum_id": curriculum_id,
        "week_number": week_number,
        "score": score,
        "max_score": max_score,
        "passed": passed,
        "completed_at": datetime.utcnow().isoformat(),
    })


async def consume_learning_logs(app_state: dict):
    """
    learning-logs 토픽 이벤트 처리:
    - Learning.ActivityLogged → DB 저장 및 이상 징후 검사
    - Learning.AnomalyDetected → 이상 징후 처리
    """
    from app.database import SessionLocal
    from app.models.tutor import LearningActivity, Feedback, TutorSession
    from app.services.tutor_agent import ai_tutor_agent

    consumer = AIOKafkaConsumer(
        settings.KAFKA_CONSUME_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info(f"[Kafka] Consumer 시작: topic={settings.KAFKA_CONSUME_TOPIC}")

    try:
        async for msg in consumer:
            event = msg.value
            event_type = event.get("event_type")
            payload = event.get("payload", {})

            # ── Learning.ActivityLogged ──────────────────────────────
            if event_type == "Learning.ActivityLogged":
                employee_id = payload.get("employee_id")
                logger.info(f"[Kafka] Learning.ActivityLogged: employee_id={employee_id}")

                db = SessionLocal()
                try:
                    # 활동 저장
                    activity = LearningActivity(
                        employee_id=employee_id,
                        session_id=payload.get("session_id"),
                        activity_type=payload.get("activity_type", ""),
                        module_id=payload.get("module_id"),
                        score=payload.get("score"),
                        duration_minutes=payload.get("duration_minutes"),
                    )
                    db.add(activity)
                    db.commit()

                    # 이상 징후 탐지
                    from sqlalchemy import func
                    from app.models.tutor import LearningActivity as LA

                    last_activity = (
                        db.query(LA)
                        .filter(LA.employee_id == employee_id)
                        .order_by(LA.logged_at.desc())
                        .offset(1)
                        .first()
                    )
                    last_at = last_activity.logged_at if last_activity else None

                    recent_scores = [
                        a.score for a in
                        db.query(LA)
                        .filter(LA.employee_id == employee_id, LA.score.isnot(None))
                        .order_by(LA.logged_at.desc())
                        .limit(5)
                        .all()
                    ]

                    recent_feedbacks = (
                        db.query(Feedback)
                        .filter(Feedback.employee_id == employee_id, Feedback.passed.is_(False))
                        .order_by(Feedback.created_at.desc())
                        .limit(10)
                        .all()
                    )
                    consecutive_fails = 0
                    for fb in recent_feedbacks:
                        if fb.passed is False:
                            consecutive_fails += 1
                        else:
                            break

                    anomaly = ai_tutor_agent.detect_anomaly(
                        employee_id=employee_id,
                        last_activity_at=last_at,
                        recent_scores=recent_scores,
                        consecutive_fails=consecutive_fails,
                    )

                    if anomaly:
                        logger.warning(f"[Anomaly] {employee_id}: {anomaly['anomaly_type']}")
                        await publish_anomaly_detected(
                            employee_id=employee_id,
                            anomaly_type=anomaly["anomaly_type"],
                            description=anomaly["description"],
                            severity=anomaly["severity"],
                        )
                finally:
                    db.close()

            # ── Learning.AnomalyDetected ─────────────────────────────
            elif event_type == "Learning.AnomalyDetected":
                # 외부 시스템(모니터링/알림)에서 수신한 이상 징후 로그만 기록
                logger.warning(
                    f"[Anomaly Received] employee={payload.get('employee_id')} "
                    f"type={payload.get('anomaly_type')} severity={payload.get('severity')}"
                )

            # ── Learning.WeekCompleted ────────────────────────────────
            elif event_type == "Learning.WeekCompleted":
                user_id = payload.get("user_id")
                curriculum_id = payload.get("curriculum_id")
                week_number = payload.get("week_number")
                avg_score = payload.get("average_score", 0.0)

                logger.info(
                    f"[WeekCompleted] user={user_id}, curriculum={curriculum_id}, "
                    f"week={week_number} → 성장 리포트 생성 시작"
                )

                db = SessionLocal()
                try:
                    since_week_start = datetime.utcnow().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    # 해당 커리큘럼 세션 + 전체 활동/피드백
                    sessions = (
                        db.query(TutorSession)
                        .filter(TutorSession.employee_id == user_id)
                        .all()
                    )
                    activities = (
                        db.query(LearningActivity)
                        .filter(LearningActivity.employee_id == user_id)
                        .order_by(LearningActivity.logged_at.desc())
                        .limit(50)
                        .all()
                    )
                    feedbacks = (
                        db.query(Feedback)
                        .filter(
                            Feedback.employee_id == user_id,
                            Feedback.feedback_type == "quiz_grading",
                        )
                        .order_by(Feedback.created_at.desc())
                        .limit(30)
                        .all()
                    )

                    scores = [f.score for f in feedbacks if f.score is not None]
                    computed_avg = sum(scores) / len(scores) if scores else avg_score
                    total_hours = sum(a.duration_minutes or 0 for a in activities) / 60

                    report_data = await ai_tutor_agent.generate_growth_report(
                        employee_name=f"User_{user_id}",
                        period_days=7,
                        total_sessions=len(sessions),
                        total_learning_hours=total_hours,
                        average_score=computed_avg,
                        recent_activities=[
                            {
                                "activity_type": a.activity_type,
                                "module_id": a.module_id,
                                "score": a.score,
                                "duration_minutes": a.duration_minutes,
                            }
                            for a in activities
                        ],
                        recent_feedback=[
                            {
                                "feedback_type": f.feedback_type,
                                "score": f.score,
                                "passed": f.passed,
                            }
                            for f in feedbacks
                        ],
                    )

                    # TutorSession 레코드 (리포트용)
                    report_session = TutorSession(
                        employee_id=user_id,
                        employee_name=f"User_{user_id}",
                        curriculum_id=curriculum_id,
                        module_title=f"{week_number}주차 성장 리포트",
                        session_type="chat",
                        status="completed",
                    )
                    report_session.set_messages([])
                    db.add(report_session)
                    db.flush()

                    # Feedback 레코드 (growth_report)
                    report_feedback = Feedback(
                        session_id=report_session.id,
                        employee_id=user_id,
                        feedback_type="growth_report",
                        score=computed_avg,
                        summary=(
                            f"{week_number}주차 완료 — "
                            + report_data.get("growth_trend", "")
                        ),
                        detail=report_data.get("report_content", ""),
                    )
                    report_feedback.set_strengths(report_data.get("strengths", []))
                    report_feedback.set_weaknesses(report_data.get("weaknesses", []))
                    report_feedback.set_recommendations(
                        report_data.get("recommendations", [])
                    )
                    db.add(report_feedback)
                    db.commit()

                    logger.info(
                        f"[WeekCompleted] {week_number}주차 성장 리포트 저장 완료: "
                        f"feedback_id={report_feedback.id}"
                    )
                except Exception as e:
                    logger.error(f"[WeekCompleted] 리포트 생성 실패: {e}", exc_info=True)
                finally:
                    db.close()

    except asyncio.CancelledError:
        logger.info("[Kafka] Consumer 종료 요청")
    finally:
        await consumer.stop()
