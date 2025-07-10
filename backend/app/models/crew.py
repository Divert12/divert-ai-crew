# backend/app/models/crew.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Crew(Base):
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="general", index=True)
    folder_name = Column(String(255), nullable=False, unique=True, index=True)
    
    # Nouveaux champs pour enrichir l'interface
    tags = Column(JSON, nullable=True, default=list)  # Liste des tags
    author = Column(String(255), nullable=True)
    version = Column(String(50), nullable=True, default="1.0.0")
    estimated_duration = Column(String(100), nullable=True)  # ex: "2-3 minutes"
    difficulty = Column(String(50), nullable=True, default="beginner")  # beginner, intermediate, advanced
    inputs = Column(JSON, nullable=True, default=dict)  # Schéma des inputs attendus
    outputs = Column(JSON, nullable=True, default=dict)  # Schéma des outputs produits
    
    # Champs de gestion
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # ✅ RELATION avec TeamInstance - Cette ligne était manquante !
    team_instances = relationship("TeamInstance", back_populates="crew")
    
    def __repr__(self):
        return f"<Crew(id={self.id}, name='{self.name}', category='{self.category}', folder='{self.folder_name}')>"