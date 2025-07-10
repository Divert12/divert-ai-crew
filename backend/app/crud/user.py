"""
Opérations CRUD pour les utilisateurs
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
from typing import Optional
from datetime import datetime

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Récupère un utilisateur par son nom d'utilisateur
    
    Args:
        db: Session de base de données
        username: Nom d'utilisateur à rechercher
        
    Returns:
        User ou None si non trouvé
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Récupère un utilisateur par son email
    
    Args:
        db: Session de base de données
        email: Email à rechercher
        
    Returns:
        User ou None si non trouvé
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Crée un nouvel utilisateur
    
    Args:
        db: Session de base de données
        user: Données de l'utilisateur à créer
        
    Returns:
        User créé
    """
    hashed_password = hash_password(user.password)
    now = datetime.utcnow()
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        created_at=now,
        updated_at=now
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Récupère un utilisateur par son ID
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur
        
    Returns:
        User ou None si non trouvé
    """
    return db.query(User).filter(User.id == user_id).first()