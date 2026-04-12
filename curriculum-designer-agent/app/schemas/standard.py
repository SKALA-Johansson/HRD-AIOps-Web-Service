from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StandardModuleCreate(BaseModel):
    week_number: int
    title: str
    description: Optional[str] = None
    topics: list[str] = []            # 이 모듈이 다루는 스킬/주제 키워드
    learning_objectives: list[str] = []
    estimated_hours: int = 8


class StandardCurriculumCreate(BaseModel):
    department: str
    role: str
    career_level: str = "junior"      # junior / mid / senior
    title: str
    description: Optional[str] = None
    total_weeks: int = 12
    modules: list[StandardModuleCreate] = []


class StandardModuleResponse(BaseModel):
    id: str
    week_number: int
    title: str
    description: Optional[str] = None
    topics: list[str]
    learning_objectives: list[str]
    estimated_hours: int

    model_config = {"from_attributes": True}


class StandardCurriculumResponse(BaseModel):
    id: str
    department: str
    role: str
    career_level: str
    title: str
    description: Optional[str] = None
    total_weeks: int
    is_active: bool
    modules: list[StandardModuleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
