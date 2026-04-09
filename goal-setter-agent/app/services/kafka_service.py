"""
Kafka Consumer/Producer Service
- Consumer: onboarding-events (User.ProfileUpdated)
- Producer: curriculum-events (Goal.Defined)
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


async def publish_goal_defined(goal_data: dict):
    """
    Goal.Defined 이벤트를 curriculum-events 토픽으로 발행
    """
    producer = await get_producer()
    event = {
        "event_type": "Goal.Defined",
        "event_id": goal_data["id"],
        "timestamp": datetime.utcnow().isoformat(),
        "source": settings.SERVICE_NAME,
        "payload": {
            "goal_id": goal_data["id"],
            "employee_id": goal_data["employee_id"],
            "employee_name": goal_data["employee_name"],
            "department": goal_data["department"],
            "role": goal_data["role"],
            "career_level": goal_data["career_level"],
            "experience_years": goal_data["experience_years"],
            "skills": goal_data["skills"],
            "goals": goal_data["goals"],
        },
    }
    await producer.send(settings.KAFKA_PRODUCE_TOPIC, value=event)
    logger.info(f"[Kafka] Goal.Defined 발행 완료: goal_id={goal_data['id']}, employee_id={goal_data['employee_id']}")


async def consume_onboarding_events(app_state: dict):
    """
    onboarding-events 토픽에서 User.ProfileUpdated 이벤트를 소비하여
    자동으로 교육 목표를 생성합니다.
    """
    from app.services.goal_agent import goal_setter_agent
    from app.database import SessionLocal
    from app.models.goal import Goal

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

            if event_type != "User.ProfileUpdated":
                continue

            logger.info(f"[Kafka] User.ProfileUpdated 수신: {event.get('event_id')}")
            payload = event.get("payload", {})

            try:
                # AI Agent로 목표 생성
                goals = await goal_setter_agent.analyze_profile_and_set_goals(payload)

                # DB 저장
                db = SessionLocal()
                try:
                    goal_record = Goal(
                        employee_id=payload.get("employee_id", ""),
                        employee_name=payload.get("employee_name", ""),
                        department=payload.get("department", ""),
                        role=payload.get("role", ""),
                        career_level=payload.get("career_level", "junior"),
                        experience_years=payload.get("experience_years", 0),
                        status="draft",
                    )
                    goal_record.set_skills(payload.get("skills", []))
                    goal_record.set_goals(goals)
                    db.add(goal_record)
                    db.commit()
                    db.refresh(goal_record)
                    logger.info(f"[DB] Goal 저장 완료: goal_id={goal_record.id}")
                finally:
                    db.close()

            except Exception as e:
                logger.error(f"[Kafka] 이벤트 처리 실패: {e}", exc_info=True)

    except asyncio.CancelledError:
        logger.info("[Kafka] Consumer 종료 요청")
    finally:
        await consumer.stop()
        logger.info("[Kafka] Consumer 종료 완료")
