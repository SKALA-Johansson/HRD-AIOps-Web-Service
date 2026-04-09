"""
Embedding Agent Service
포트: 10028
역할: BGE-M3 임베딩 생성 및 Qdrant 벡터 저장/검색
"""
import logging
import py_eureka_client.eureka_client as eureka_client
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.routers.embeddings import router as embeddings_router
from app.services.embedding_service import warm_up

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"[Startup] {settings.SERVICE_NAME} 시작 (port={settings.SERVICE_PORT})")

    try:
        warm_up()
        logger.info("[Embedding] BGE-M3 모델 로딩 및 Qdrant 컬렉션 준비 완료")
    except Exception as e:
        logger.warning(f"[Embedding] 초기화 실패 (요청 시 재시도): {e}")

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

    yield

    logger.info("[Shutdown] 서비스 종료 시작")
    await eureka_client.stop_async()
    logger.info("[Shutdown] 종료 완료")


app = FastAPI(
    title="Embedding Agent Service",
    description="BGE-M3 임베딩 생성 및 Qdrant 벡터 저장/검색 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(embeddings_router)


@app.get("/health")
def health_check():
    return {
        "status": "UP",
        "service": settings.SERVICE_NAME,
        "port": settings.SERVICE_PORT,
        "model": settings.BGE_M3_MODEL_NAME,
        "collection": settings.QDRANT_COLLECTION,
    }


@app.get("/")
def root():
    return {"message": f"{settings.SERVICE_NAME} is running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.SERVICE_PORT, reload=True)
