"""
AI Tutor Agent Service
포트: 10024
역할: 실시간 AI 튜터링, 과제 자동 채점/피드백, 성장 리포트 생성, 학습 이상 징후 탐지 (RAG 사용)
이벤트:
  - 소비: learning-logs (Learning.ActivityLogged, Learning.AnomalyDetected)
  - 발행: learning-logs (Learning.ActivityLogged, Learning.AnomalyDetected)
"""
import asyncio
import logging
import py_eureka_client.eureka_client as eureka_client
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import create_tables
from app.routers.tutor import router as tutor_router
from app.services.kafka_service import consume_learning_logs, stop_producer

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
    consumer_task = asyncio.create_task(consume_learning_logs(app_state))
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
    title="AI Tutor Agent Service",
    description="실시간 AI 튜터링, 자동 채점/피드백, 성장 리포트, 이상 징후 탐지 (RAG 기반)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(tutor_router)


@app.get("/health")
def health_check():
    return {"status": "UP", "service": settings.SERVICE_NAME, "port": settings.SERVICE_PORT}


@app.get("/")
def root():
    return {"message": f"{settings.SERVICE_NAME} is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=True)
