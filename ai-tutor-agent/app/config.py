from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "ai-tutor-agent"
    SERVICE_PORT: int = 10024

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "tutor_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "ai-tutor-group"
    KAFKA_CONSUME_TOPIC: str = "learning-logs"
    KAFKA_PRODUCE_TOPIC: str = "learning-logs"

    # Eureka
    EUREKA_SERVER_URL: str = "http://localhost:8761/eureka"
    EUREKA_INSTANCE_HOST: str = "localhost"

    # OpenAI
    OPENAI_API_KEY: str = "sk-your-key-here"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "tutor_rag"

    # Anomaly Detection
    ANOMALY_INACTIVITY_HOURS: int = 48
    ANOMALY_LOW_SCORE_THRESHOLD: int = 40
    ANOMALY_CONSECUTIVE_FAILS: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
