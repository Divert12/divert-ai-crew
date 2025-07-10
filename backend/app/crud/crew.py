
from sqlalchemy.orm import Session
from app.models.crew import Crew
from app.schemas.crew import CrewCreate
from typing import List, Optional

def get_crews(db: Session, skip: int = 0, limit: int = 100) -> List[Crew]:
    """
    Récupère la liste des équipes disponibles
    
    Args:
        db: Session de base de données
        skip: Nombre d'éléments à ignorer
        limit: Nombre maximum d'éléments à retourner
        
    Returns:
        Liste des équipes
    """
    return db.query(Crew).filter(Crew.is_active == True).offset(skip).limit(limit).all()

def get_crew_by_id(db: Session, crew_id: int) -> Optional[Crew]:
    """
    Récupère une équipe par son ID
    
    Args:
        db: Session de base de données
        crew_id: ID de l'équipe
        
    Returns:
        Crew ou None si non trouvé
    """
    return db.query(Crew).filter(Crew.id == crew_id, Crew.is_active == True).first()

def create_crew(db: Session, crew: CrewCreate) -> Crew:
    """
    Crée une nouvelle équipe
    
    Args:
        db: Session de base de données
        crew: Données de l'équipe à créer
        
    Returns:
        Crew créée
    """
    db_crew = Crew(**crew.dict())
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)
    return db_crew

def get_crews_by_category(db: Session, category: str) -> List[Crew]:
    """
    Récupère les équipes par catégorie
    
    Args:
        db: Session de base de données
        category: Catégorie des équipes
        
    Returns:
        Liste des équipes de la catégorie
    """
    return db.query(Crew).filter(Crew.category == category, Crew.is_active == True).all()