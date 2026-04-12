import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base


class Curriculum(Base):
    __tablename__ = "curriculums"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String(100), nullable=False, index=True)
    employee_id = Column(String(100), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    career_level = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_weeks = Column(Integer, default=12)
    status = Column(
        SAEnum("generating", "draft", "approved", "rejected", "revised", "active", "completed", "error", name="curriculum_status"),
        default="draft",
        nullable=False,
    )
    revision_note = Column(Text, nullable=True)
    existing_skills = Column(Text, nullable=True)   # JSON list — PDF에서 추출한 역량
    skill_analysis = Column(Text, nullable=True)    # JSON — AI 모듈 포함/제외 판단 결과
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    modules = relationship("Module", back_populates="curriculum", cascade="all, delete-orphan")

    def get_existing_skills(self) -> list:
        return json.loads(self.existing_skills) if self.existing_skills else []

    def set_existing_skills(self, skills: list):
        self.existing_skills = json.dumps(skills, ensure_ascii=False)

    def get_skill_analysis(self) -> dict:
        return json.loads(self.skill_analysis) if self.skill_analysis else {}

    def set_skill_analysis(self, analysis: dict):
        self.skill_analysis = json.dumps(analysis, ensure_ascii=False)


class Module(Base):
    __tablename__ = "modules"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    curriculum_id = Column(CHAR(36), ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)      # RAG로 생성된 학습 콘텐츠
    learning_objectives = Column(Text, nullable=True)  # JSON list
    resources = Column(Text, nullable=True)            # JSON list (참고자료)
    assignments = Column(Text, nullable=True)          # JSON list (과제)
    estimated_hours = Column(Integer, default=8)
    created_at = Column(DateTime, default=datetime.utcnow)

    curriculum = relationship("Curriculum", back_populates="modules")

    def get_learning_objectives(self) -> list:
        return json.loads(self.learning_objectives) if self.learning_objectives else []

    def set_learning_objectives(self, objs: list):
        self.learning_objectives = json.dumps(objs, ensure_ascii=False)

    def get_resources(self) -> list:
        return json.loads(self.resources) if self.resources else []

    def set_resources(self, resources: list):
        self.resources = json.dumps(resources, ensure_ascii=False)

    def get_assignments(self) -> list:
        return json.loads(self.assignments) if self.assignments else []

    def set_assignments(self, assignments: list):
        self.assignments = json.dumps(assignments, ensure_ascii=False)
