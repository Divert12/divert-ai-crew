from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    folder_name: str

class WorkflowCreate(WorkflowBase):
    type: str = "n8n_workflow"
    node_count: Optional[int] = 0
    integrations: Optional[List[str]] = []
    required_credentials: Optional[List[str]] = []

class WorkflowResponse(WorkflowBase):
    id: int
    type: str
    node_count: int
    integrations: List[str]
    required_credentials: List[str]
    n8n_workflow_id: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CredentialCreate(BaseModel):
    credentials: Dict[str, str]

class IntegrationStatus(BaseModel):
    service_name: str
    status: str
    configured_at: Optional[str] = None
    is_configured: bool

class WorkflowExecutionInput(BaseModel):
    inputs: Optional[Dict[str, Any]] = {}