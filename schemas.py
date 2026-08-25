from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    status: str = "planejado"
    priority: str = "media"
    manager: Optional[str] = None
    budget: Optional[str] = None
    progress: int = 0
    deadline: Optional[str] = None
    risks: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AIQuery(BaseModel):
    query: str

class AIResponse(BaseModel):
    answer: str
    sources: list[str]
