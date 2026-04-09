import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(100), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    career_level = Column(String(50), nullable=False)  # junior / mid / senior
    experience_years = Column(Integer, default=0)
    skills = Column(Text, nullable=False)       # JSON list: ["Python", "SQL", ...]
    goals = Column(Text, nullable=True)         # JSON list of goal objects
    status = Column(
        SAEnum("generating", "draft", "approved", "rejected", "error", name="goal_status"),
        default="draft",
        nullable=False,
    )
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_skills(self) -> list:
        return json.loads(self.skills) if self.skills else []

    def set_skills(self, skills: list):
        self.skills = json.dumps(skills, ensure_ascii=False)

    def get_goals(self) -> list:
        return json.loads(self.goals) if self.goals else []

    def set_goals(self, goals: list):
        self.goals = json.dumps(goals, ensure_ascii=False)
