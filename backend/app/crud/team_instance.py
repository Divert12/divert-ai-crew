# backend/app/crud/team_instance.py
"""
Opérations CRUD pour les instances d'équipes
"""
from sqlalchemy.orm import Session, joinedload
from app.models.team_instance import TeamInstance
from app.schemas.team_instance import TeamInstanceCreate
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.crew import Crew
def get_user_team_instances(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[TeamInstance]:
    """
    Récupère toutes les équipes d'un utilisateur avec les données crew et workflow chargées
    """
    return (db.query(TeamInstance)
            .options(joinedload(TeamInstance.crew), joinedload(TeamInstance.workflow))  # ✅ Charge les relations crew et workflow
            .filter(TeamInstance.user_id == user_id, TeamInstance.is_active == True)
            .offset(skip)
            .limit(limit)
            .all())

def create_team_instance(db: Session, team_instance: TeamInstanceCreate, user_id: int) -> TeamInstance:
    """
    Ajoute une équipe aux équipes de l'utilisateur
    """
    
    # ✅ AJOUTÉ : Générer un nom par défaut si pas fourni
    crew = db.query(Crew).filter(Crew.id == team_instance.crew_id).first()
    default_name = team_instance.name or (crew.name if crew else f"Équipe {team_instance.crew_id}")
    
    db_team_instance = TeamInstance(
        user_id=user_id,
        crew_id=team_instance.crew_id,
        name=default_name  # ✅ Toujours une valeur
    )
    db.add(db_team_instance)
    db.commit()
    db.refresh(db_team_instance)
    
    # Charger les relations crew et workflow pour la réponse
    return db.query(TeamInstance).options(joinedload(TeamInstance.crew), joinedload(TeamInstance.workflow)).filter(TeamInstance.id == db_team_instance.id).first()

def get_team_instance_by_id(db: Session, instance_id: UUID, user_id: int) -> Optional[TeamInstance]:
    """
    Récupère une instance d'équipe par son ID pour un utilisateur donné
    """
    # Convert UUID to string if necessary (database stores as string)
    instance_id_str = str(instance_id) if isinstance(instance_id, UUID) else instance_id
    
    return (db.query(TeamInstance)
            .options(joinedload(TeamInstance.crew), joinedload(TeamInstance.workflow))
            .filter(
                TeamInstance.id == instance_id_str,
                TeamInstance.user_id == user_id,
                TeamInstance.is_active == True
            ).first())

def update_team_instance_execution(db: Session, instance_id: UUID, user_id: int) -> Optional[TeamInstance]:
    """
    Met à jour la date de dernière exécution d'une instance
    """
    # Convert UUID to string if necessary (database stores as string)
    instance_id_str = str(instance_id) if isinstance(instance_id, UUID) else instance_id
    
    team_instance = get_team_instance_by_id(db, instance_id_str, user_id)
    if team_instance:
        team_instance.last_executed = datetime.utcnow()
        db.commit()
        db.refresh(team_instance)
        return team_instance

def check_user_has_crew(db: Session, user_id: int, crew_id: int) -> bool:
    """
    Vérifie si un utilisateur a déjà ajouté une équipe
    """
    return (db.query(TeamInstance)
            .filter(
                TeamInstance.user_id == user_id,
                TeamInstance.crew_id == crew_id,
                TeamInstance.is_active == True
            ).first() is not None)