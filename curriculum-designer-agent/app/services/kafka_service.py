"""
Kafka Consumer/Producer
- 소비: curriculum-events (Goal.Defined, Curriculum.Revised)
- 발행: curriculum-events (Curriculum.Created, Curriculum.Revised)
          learning-events (Curriculum.Approved)  ← api.md §3 토픽 기준
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
    """
    이벤트 발행
    - Curriculum.Approved → learning-events  (api.md §3 기준)
    - 나머지             → curriculum-events
    """
    producer = await get_producer()
    event = {
        "event_type": event_type,
        "event_id": payload.get("curriculum_id", ""),
        "timestamp": datetime.utcnow().isoformat(),
        "source": settings.SERVICE_NAME,
        "payload": payload,
    }
    # api.md §3: Curriculum.Approved 는 learning-events 토픽
    topic = "learning-events" if event_type == "Curriculum.Approved" else settings.KAFKA_PRODUCE_TOPIC
    await producer.send(topic, value=event)
    logger.info(f"[Kafka] {event_type} 발행 완료 → topic={topic}")


async def consume_curriculum_events(app_state: dict):
    """
    curriculum-events 토픽 이벤트 처리:
    - Goal.Defined → 커리큘럼 자동 생성
    - Curriculum.Approved → 상태 업데이트, 활성화
    - Curriculum.Revised → 커리큘럼 수정
    """
    from app.services.curriculum_agent import curriculum_designer_agent
    from app.database import SessionLocal
    from app.models.curriculum import Curriculum, Module

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

            # ── Goal.Defined: 커리큘럼 자동 생성 ──────────────────────
            if event_type == "Goal.Defined":
                logger.info(f"[Kafka] Goal.Defined 수신: goal_id={payload.get('goal_id')}")
                try:
                    curriculum_data = await curriculum_designer_agent.design_curriculum(
                        employee_name=payload.get("employee_name", ""),
                        department=payload.get("department", ""),
                        role=payload.get("role", ""),
                        career_level=payload.get("career_level", "junior"),
                        experience_years=payload.get("experience_years", 0),
                        skills=payload.get("skills", []),
                        goals=payload.get("goals", []),
                    )
                    db = SessionLocal()
                    try:
                        curriculum = Curriculum(
                            goal_id=payload.get("goal_id", ""),
                            employee_id=payload.get("employee_id", ""),
                            employee_name=payload.get("employee_name", ""),
                            department=payload.get("department", ""),
                            role=payload.get("role", ""),
                            career_level=payload.get("career_level", "junior"),
                            title=curriculum_data.get("title", "맞춤형 교육 커리큘럼"),
                            description=curriculum_data.get("description", ""),
                            total_weeks=curriculum_data.get("total_weeks", 12),
                            status="draft",
                        )
                        db.add(curriculum)
                        db.flush()

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
                        db.refresh(curriculum)
                        logger.info(f"[DB] Curriculum 생성 완료: {curriculum.id}")

                        # Curriculum.Created 이벤트 발행
                        await publish_event("Curriculum.Created", {
                            "curriculum_id": curriculum.id,
                            "goal_id": curriculum.goal_id,
                            "employee_id": curriculum.employee_id,
                            "title": curriculum.title,
                            "total_weeks": curriculum.total_weeks,
                        })
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"[Kafka] Goal.Defined 처리 실패: {e}", exc_info=True)

            # ── Curriculum.Approved: 상태를 active로 전환 ──────────────
            elif event_type == "Curriculum.Approved":
                curriculum_id = payload.get("curriculum_id")
                logger.info(f"[Kafka] Curriculum.Approved 수신: {curriculum_id}")
                db = SessionLocal()
                try:
                    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
                    if c:
                        c.status = "active"
                        db.commit()
                        logger.info(f"[DB] Curriculum 활성화: {curriculum_id}")
                finally:
                    db.close()

            # ── Curriculum.Revised: 수정 요청 처리 ────────────────────
            elif event_type == "Curriculum.Revised":
                curriculum_id = payload.get("curriculum_id")
                revision_note = payload.get("revision_note", "")
                logger.info(f"[Kafka] Curriculum.Revised 수신: {curriculum_id}")
                try:
                    db = SessionLocal()
                    try:
                        c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
                        if not c:
                            continue
                        current = {"title": c.title, "description": c.description, "modules": []}
                        revised = await curriculum_designer_agent.revise_curriculum(current, revision_note)
                        c.title = revised.get("title", c.title)
                        c.description = revised.get("description", c.description)
                        c.total_weeks = revised.get("total_weeks", c.total_weeks)
                        c.revision_note = revision_note
                        c.status = "revised"
                        c.version += 1

                        # 기존 모듈 삭제 후 재생성
                        db.query(Module).filter(Module.curriculum_id == curriculum_id).delete()
                        for mod_data in revised.get("modules", []):
                            module = Module(
                                curriculum_id=c.id,
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
                        logger.info(f"[DB] Curriculum 수정 완료: {curriculum_id} (v{c.version})")
                    finally:
                        db.close()
                except Exception as e:
                    logger.error(f"[Kafka] Curriculum.Revised 처리 실패: {e}", exc_info=True)

    except asyncio.CancelledError:
        logger.info("[Kafka] Consumer 종료 요청")
    finally:
        await consumer.stop()
