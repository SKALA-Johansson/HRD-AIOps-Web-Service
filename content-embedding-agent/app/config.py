from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "content-embedding-agent"
    SERVICE_PORT: int = 10028

    # Eureka
    EUREKA_SERVER_URL: str = "http://localhost:8761/eureka"
    EUREKA_INSTANCE_HOST: str = "localhost"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "embedded_docs"

    # OpenAI
    OPENAI_API_KEY: str = "sk-your-key-here"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"


settings = Settings()
