import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base


class StandardCurriculum(Base):
    """부서/역할별 정석 커리큘럼 (기준 커리큘럼)"""
    __tablename__ = "standard_curriculums"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    department = Column(String(100), nullable=False, index=True)   # 부서 (예: 개발팀, 데이터팀)
    role = Column(String(100), nullable=False, index=True)          # 직무 (예: 백엔드 엔지니어)
    career_level = Column(String(50), nullable=False, index=True)   # junior / mid / senior
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_weeks = Column(Integer, default=12)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    modules = relationship("StandardModule", back_populates="curriculum",
                           cascade="all, delete-orphan", order_by="StandardModule.week_number")


class StandardModule(Base):
    """정석 커리큘럼의 주차별 모듈"""
    __tablename__ = "standard_modules"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    curriculum_id = Column(CHAR(36), ForeignKey("standard_curriculums.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    topics = Column(Text, nullable=True)            # JSON list: 이 모듈이 다루는 스킬/주제 키워드
    learning_objectives = Column(Text, nullable=True)  # JSON list
    estimated_hours = Column(Integer, default=8)
    created_at = Column(DateTime, default=datetime.utcnow)

    curriculum = relationship("StandardCurriculum", back_populates="modules")

    def get_topics(self) -> list[str]:
        return json.loads(self.topics) if self.topics else []

    def set_topics(self, topics: list[str]):
        self.topics = json.dumps(topics, ensure_ascii=False)

    def get_learning_objectives(self) -> list[str]:
        return json.loads(self.learning_objectives) if self.learning_objectives else []

    def set_learning_objectives(self, objs: list[str]):
        self.learning_objectives = json.dumps(objs, ensure_ascii=False)
