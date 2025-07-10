from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class CrewBase(BaseModel):
    """Schéma de base pour une équipe"""
    name: str
    description: Optional[str] = None
    category: str = "general"
    folder_name: str
    # Nouveaux champs pour enrichir l'affichage frontend
    tags: Optional[List[str]] = []
    author: Optional[str] = None
    version: Optional[str] = "1.0.0"
    estimated_duration: Optional[str] = None
    difficulty: Optional[str] = "beginner"
    inputs: Optional[Dict[str, Any]] = {}
    outputs: Optional[Dict[str, Any]] = {}

class CrewCreate(CrewBase):
    """Schéma pour la création d'une équipe"""
    pass

class CrewResponse(CrewBase):
    """Schéma de réponse pour une équipe"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema pour les réponses d'exécution
class CrewExecutionRequest(BaseModel):
    crew_id: int
    inputs: Dict[str, Any]

class CrewExecutionResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None