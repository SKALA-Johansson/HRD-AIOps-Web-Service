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


async def publish_week_completed(
    user_id: str,
    curriculum_id: str,
    week_number: int,
    total_modules: int,
    scores: list[float],
):
    """Learning.WeekCompleted 이벤트 발행 → learning-logs 토픽"""
    producer = await get_producer()
    avg_score = sum(scores) / len(scores) if scores else 0.0
    event = {
        "event_type": "Learning.WeekCompleted",
        "event_id": f"{user_id}_{curriculum_id}_week{week_number}",
        "timestamp": datetime.utcnow().isoformat(),
        "source": settings.SERVICE_NAME,
        "payload": {
            "user_id": user_id,
            "curriculum_id": curriculum_id,
            "week_number": week_number,
            "total_modules": total_modules,
            "average_score": avg_score,
            "scores": scores,
            "completed_at": datetime.utcnow().isoformat(),
        },
    }
    await producer.send("learning-logs", value=event)
    logger.info(
        f"[Kafka] Learning.WeekCompleted 발행: user={user_id}, "
        f"curriculum={curriculum_id}, week={week_number}"
    )


async def consume_learning_logs(app_state: dict):
    """
    learning-logs 토픽에서 Learning.QuizCompleted 이벤트를 소비:
    - ModuleCompletion 기록
    - 해당 주차 모든 모듈 완료 확인
    - 완료 시 Learning.WeekCompleted 발행
    """
    from app.database import SessionLocal
    from app.models.curriculum import Module, ModuleCompletion

    consumer = AIOKafkaConsumer(
        "learning-logs",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="curriculum-designer-learning-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    await consumer.start()
    logger.info("[Kafka] Learning-logs Consumer 시작")

    try:
        async for msg in consumer:
            event = msg.value
            event_type = event.get("event_type")
            payload = event.get("payload", {})

            if event_type not in ("Learning.QuizCompleted", "Learning.AssignmentCompleted"):
                continue

            user_id = payload.get("user_id")
            module_id = payload.get("module_id")
            curriculum_id = payload.get("curriculum_id")
            week_number = payload.get("week_number")

            if not all([user_id, module_id, curriculum_id, week_number]):
                logger.debug(f"[WeekCheck] 필드 누락으로 스킵: {payload}")
                continue

            logger.info(
                f"[WeekCheck] QuizCompleted: user={user_id}, "
                f"module={module_id}, week={week_number}"
            )

            db = SessionLocal()
            try:
                # 완료 기록 upsert
                existing = (
                    db.query(ModuleCompletion)
                    .filter(
                        ModuleCompletion.user_id == user_id,
                        ModuleCompletion.module_id == module_id,
                    )
                    .first()
                )
                if not existing:
                    db.add(
                        ModuleCompletion(
                            user_id=user_id,
                            module_id=module_id,
                            curriculum_id=curriculum_id,
                            week_number=int(week_number),
                            passed=payload.get("passed"),
                            score=payload.get("score"),
                        )
                    )
                    db.commit()

                # 해당 주차의 전체 모듈 조회
                all_modules = (
                    db.query(Module)
                    .filter(
                        Module.curriculum_id == curriculum_id,
                        Module.week_number == int(week_number),
                    )
                    .all()
                )
                if not all_modules:
                    logger.warning(
                        f"[WeekCheck] curriculum={curriculum_id} week={week_number} 모듈 없음"
                    )
                    continue

                all_module_ids = {m.id for m in all_modules}

                # 이 사용자가 완료한 모듈 ID 집합
                completions = (
                    db.query(ModuleCompletion)
                    .filter(
                        ModuleCompletion.user_id == user_id,
                        ModuleCompletion.curriculum_id == curriculum_id,
                        ModuleCompletion.week_number == int(week_number),
                    )
                    .all()
                )
                completed_ids = {c.module_id for c in completions}

                logger.info(
                    f"[WeekCheck] 완료: {len(completed_ids)}/{len(all_module_ids)} 모듈"
                )

                if all_module_ids <= completed_ids:
                    scores = [c.score for c in completions if c.score is not None]
                    logger.info(
                        f"[WeekCheck] 주차 완료! user={user_id}, week={week_number} "
                        f"→ Learning.WeekCompleted 발행"
                    )
                    await publish_week_completed(
                        user_id=user_id,
                        curriculum_id=curriculum_id,
                        week_number=int(week_number),
                        total_modules=len(all_module_ids),
                        scores=scores,
                    )

            except Exception as e:
                logger.error(f"[WeekCheck] 처리 오류: {e}", exc_info=True)
            finally:
                db.close()

    except asyncio.CancelledError:
        logger.info("[Kafka] Learning-logs Consumer 종료 요청")
    finally:
        await consumer.stop()
