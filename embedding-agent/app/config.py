from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "embedding-agent"
    SERVICE_PORT: int = 10028

    # Eureka
    EUREKA_SERVER_URL: str = "http://localhost:8761/eureka"
    EUREKA_INSTANCE_HOST: str = "localhost"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "bge_m3_docs"

    # BGE-M3
    BGE_M3_MODEL_NAME: str = "BAAI/bge-m3"
    BGE_M3_DEVICE: str = "cpu"
    BGE_BATCH_SIZE: int = 16

    class Config:
        env_file = ".env"


settings = Settings()
