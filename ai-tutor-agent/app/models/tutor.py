import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base


class TutorSession(Base):
    __tablename__ = "tutor_sessions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(100), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    curriculum_id = Column(String(100), nullable=True, index=True)
    module_id = Column(String(100), nullable=True)
    module_title = Column(String(200), nullable=True)
    session_type = Column(
        SAEnum("chat", "quiz", "assignment", name="session_type"),
        default="chat",
        nullable=False,
    )
    messages = Column(Text, nullable=True)          # JSON list of {role, content, timestamp}
    status = Column(
        SAEnum("active", "completed", "abandoned", name="session_status"),
        default="active",
        nullable=False,
    )
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    feedback = relationship("Feedback", back_populates="session", cascade="all, delete-orphan")

    def get_messages(self) -> list:
        return json.loads(self.messages) if self.messages else []

    def set_messages(self, messages: list):
        self.messages = json.dumps(messages, ensure_ascii=False)

    def add_message(self, role: str, content: str):
        msgs = self.get_messages()
        msgs.append({"role": role, "content": content, "timestamp": datetime.utcnow().isoformat()})
        self.set_messages(msgs)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(CHAR(36), ForeignKey("tutor_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(100), nullable=False, index=True)
    feedback_type = Column(
        SAEnum("quiz_grading", "assignment_grading", "growth_report", "anomaly", name="feedback_type"),
        nullable=False,
    )
    # 퀴즈/과제 채점
    score = Column(Float, nullable=True)            # 0~100
    max_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    # 피드백 내용
    summary = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)         # JSON list
    weaknesses = Column(Text, nullable=True)        # JSON list
    recommendations = Column(Text, nullable=True)   # JSON list
    detail = Column(Text, nullable=True)            # 상세 피드백
    # 이상 감지
    is_anomaly = Column(Boolean, default=False)
    anomaly_type = Column(String(100), nullable=True)  # inactivity / low_score / consecutive_fail
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("TutorSession", back_populates="feedback")

    def get_strengths(self) -> list:
        return json.loads(self.strengths) if self.strengths else []

    def set_strengths(self, v: list):
        self.strengths = json.dumps(v, ensure_ascii=False)

    def get_weaknesses(self) -> list:
        return json.loads(self.weaknesses) if self.weaknesses else []

    def set_weaknesses(self, v: list):
        self.weaknesses = json.dumps(v, ensure_ascii=False)

    def get_recommendations(self) -> list:
        return json.loads(self.recommendations) if self.recommendations else []

    def set_recommendations(self, v: list):
        self.recommendations = json.dumps(v, ensure_ascii=False)


class LearningActivity(Base):
    """학습 활동 로그 (Kafka learning-logs 이벤트 저장)"""
    __tablename__ = "learning_activities"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(100), nullable=False, index=True)
    session_id = Column(String(100), nullable=True)
    activity_type = Column(String(100), nullable=False)  # module_view, quiz_submit, chat, etc.
    module_id = Column(String(100), nullable=True)
    score = Column(Float, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    # SQLAlchemy Declarative에서 `metadata`는 예약어라 파이썬 속성명을 분리합니다.
    event_metadata = Column("metadata", Text, nullable=True)  # JSON
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)
