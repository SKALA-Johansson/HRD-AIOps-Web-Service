from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "goal-setter-agent"
    SERVICE_PORT: int = 10021

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "goal_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "goal-setter-group"
    KAFKA_CONSUME_TOPIC: str = "onboarding-events"
    KAFKA_PRODUCE_TOPIC: str = "curriculum-events"

    # Eureka
    EUREKA_SERVER_URL: str = "http://localhost:8761/eureka"
    EUREKA_INSTANCE_HOST: str = "localhost"

    # OpenAI
    OPENAI_API_KEY: str = "sk-your-key-here"
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


settings = Settings()
