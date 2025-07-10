"""
Schémas Pydantic pour les utilisateurs
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur"""
    password: str

class UserLogin(BaseModel):
    """Schéma pour la connexion d'un utilisateur"""
    username: str
    password: str

class UserResponse(UserBase):
    """Schéma de réponse pour un utilisateur"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str
    token_type: str

class UserShort(BaseModel):
    """Schéma utilisateur simplifié pour l'inclusion dans le token"""
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class TokenWithUser(BaseModel):
    """Schéma pour le token JWT avec infos utilisateur incluses"""
    access_token: str
    token_type: str
    user: UserShort