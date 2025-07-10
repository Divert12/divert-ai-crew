from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database.database import Base

class TeamInstance(Base):
    __tablename__ = "team_instances"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crew_id = Column(Integer, ForeignKey("crews.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    
    name = Column(String, nullable=False)
    description = Column(Text)
    inputs = Column(JSON)
    status = Column(String, default="inactive")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # Relations
    user = relationship("User", back_populates="team_instances")
    crew = relationship("Crew", back_populates="team_instances")  
    workflow = relationship("Workflow")