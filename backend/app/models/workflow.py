from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database.database import Base
from sqlalchemy.orm import relationship 

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    folder_name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    type = Column(String, default="n8n_workflow")  # "n8n_workflow" ou "crewai"
    
    # Métadonnées N8N
    n8n_workflow_id = Column(String)  # ID dans N8N après installation
    node_count = Column(Integer, default=0)
    integrations = Column(JSON)  # Liste des intégrations requises
    required_credentials = Column(JSON)  # Credentials nécessaires
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Détails d'exécution
    n8n_execution_id = Column(String)
    status = Column(String, default="running")  # "running", "success", "failed"
    inputs = Column(JSON)
    outputs = Column(JSON)
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relations
    workflow = relationship("Workflow")
    user = relationship("User")