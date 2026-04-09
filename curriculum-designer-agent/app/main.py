"""
Curriculum Designer Agent Service
포트: 10022
역할: 교육 목표 기반 맞춤형 커리큘럼 자동 생성, 교육 콘텐츠 생성 (RAG 사용)
이벤트:
  - 소비: curriculum-events (Goal.Defined, Curriculum.Approved, Curriculum.Revised)
  - 발행: curriculum-events (Curriculum.Created, Curriculum.Updated)
"""
import asyncio
import logging
import py_eureka_client.eureka_client as eureka_client
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import create_tables
from app.routers.curriculums import router as curriculums_router
from app.services.kafka_service import consume_curriculum_events, stop_producer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    logger.info(f"[Startup] {settings.SERVICE_NAME} 시작 (port={settings.SERVICE_PORT})")

    create_tables()
    logger.info("[DB] 테이블 초기화 완료")

    try:
        await eureka_client.init_async(
            eureka_server=settings.EUREKA_SERVER_URL,
            app_name=settings.SERVICE_NAME,
            instance_port=settings.SERVICE_PORT,
            instance_host=settings.EUREKA_INSTANCE_HOST,
        )
        logger.info(f"[Eureka] 서비스 등록 완료: {settings.SERVICE_NAME}")
    except Exception as e:
        logger.warning(f"[Eureka] 등록 실패 (무시하고 계속): {e}")

    app_state = {}
    consumer_task = asyncio.create_task(consume_curriculum_events(app_state))
    logger.info("[Kafka] Consumer 백그라운드 시작")

    yield

    # ── Shutdown ──────────────────────────────────────────
    logger.info("[Shutdown] 서비스 종료 시작")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await stop_producer()
    await eureka_client.stop_async()
    logger.info("[Shutdown] 종료 완료")


app = FastAPI(
    title="Curriculum Designer Agent Service",
    description="교육 목표 기반 맞춤형 커리큘럼 자동 생성 AI Agent (RAG 사용)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(curriculums_router)


@app.get("/health")
def health_check():
    return {"status": "UP", "service": settings.SERVICE_NAME, "port": settings.SERVICE_PORT}


@app.get("/")
def root():
    return {"message": f"{settings.SERVICE_NAME} is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=True)
