from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="planejado")
    priority = Column(String, default="media")
    manager = Column(String)
    budget = Column(String)
    progress = Column(Integer, default=0)
    deadline = Column(String)
    risks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
