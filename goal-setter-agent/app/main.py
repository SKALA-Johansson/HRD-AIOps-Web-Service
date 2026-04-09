"""
Goal Setter Agent Service
포트: 10021
역할: 신입사원 프로필 분석, 개인별 교육 목표 자동 설정/승인
이벤트:
  - 소비: onboarding-events (User.ProfileUpdated)
  - 발행: curriculum-events (Goal.Defined)
"""
import asyncio
import logging
import py_eureka_client.eureka_client as eureka_client
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import create_tables
from app.routers.goals import router as goals_router
from app.routers.ingest import router as ingest_router
from app.services.kafka_service import consume_onboarding_events, stop_producer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    logger.info(f"[Startup] {settings.SERVICE_NAME} 시작 (port={settings.SERVICE_PORT})")

    # DB 테이블 생성
    create_tables()
    logger.info("[DB] 테이블 초기화 완료")

    # Eureka 등록
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

    # Kafka Consumer 백그라운드 실행
    app_state = {}
    consumer_task = asyncio.create_task(consume_onboarding_events(app_state))
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
    title="Goal Setter Agent Service",
    description="신입사원 프로필 분석 및 개인별 교육 목표 자동 설정/승인 AI Agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(goals_router)
app.include_router(ingest_router)


@app.get("/health")
def health_check():
    return {"status": "UP", "service": settings.SERVICE_NAME, "port": settings.SERVICE_PORT}


@app.get("/")
def root():
    return {"message": f"{settings.SERVICE_NAME} is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=True)
