"""
Schémas Pydantic pour TeamInstance avec relations
"""
import uuid as uuid_module
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# ✅ Schémas pour les relations imbriquées
class UserInTeamInstance(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class CrewInTeamInstance(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    folder_name: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

# Schémas principaux
class TeamInstanceCreate(BaseModel):
    crew_id: int
    name: Optional[str] = None

class CrewInput(BaseModel):
    topic: str

class TeamInstanceResponse(BaseModel):
    id: uuid_module.UUID = Field(description="Unique identifier")
    user_id: int
    crew_id: int
    name: Optional[str] = None
    is_active: bool = True
    last_executed: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # ✅ FIX: Relations avec des schémas Pydantic appropriés
    user: Optional[UserInTeamInstance] = None
    crew: Optional[CrewInTeamInstance] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            uuid_module.UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }
    )

class TeamInstanceUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None