# backend/app/routers/my_teams.py
"""
Routeur pour la gestion des équipes de l'utilisateur
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.database.database import get_db
from app.schemas.team_instance import TeamInstanceCreate, TeamInstanceResponse, CrewInput
from app.crud.team_instance import (
    get_user_team_instances,
    create_team_instance,
    get_team_instance_by_id,
    update_team_instance_execution,
    check_user_has_crew
)
from app.crud.crew import get_crew_by_id
from app.core.security import get_current_user
from app.services.crew_executor import CrewExecutorService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_my_teams(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Récupère toutes les équipes et workflows de l'utilisateur connecté
    """
    try:
        logger.info(f"📋 Récupération des équipes/workflows pour l'utilisateur {current_user['username']}")
        
        from app.models.team_instance import TeamInstance
        from app.models.crew import Crew
        from app.models.workflow import Workflow
        
        # Récupérer toutes les instances de l'utilisateur
        instances = db.query(TeamInstance).filter(
            TeamInstance.user_id == current_user["id"],
            TeamInstance.is_active == True
        ).offset(skip).limit(limit).all()
        
        result = []
        for instance in instances:
            instance_data = {
                "id": instance.id,
                "name": instance.name,
                "is_active": instance.is_active,
                "created_at": instance.created_at.isoformat(),
                "last_executed": instance.last_executed.isoformat() if instance.last_executed else None
            }
            
            # Si c'est un crew
            if instance.crew_id:
                crew = db.query(Crew).filter(Crew.id == instance.crew_id).first()
                if crew:
                    instance_data.update({
                        "crew": {
                            "id": crew.id,
                            "name": crew.name,
                            "description": crew.description,
                            "category": crew.category,
                            "folder_name": crew.folder_name
                        },
                        "type": "crew"
                    })
            
            # Si c'est un workflow
            elif instance.workflow_id:
                workflow = db.query(Workflow).filter(Workflow.id == instance.workflow_id).first()
                if workflow:
                    instance_data.update({
                        "workflow": {
                            "id": workflow.id,
                            "name": workflow.name,
                            "description": workflow.description,
                            "category": workflow.category,
                            "folder_name": workflow.folder_name
                        },
                        "type": "workflow"
                    })
            
            result.append(instance_data)
        
        logger.info(f"✅ {len(result)} équipes/workflows trouvées pour {current_user['username']}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des équipes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des équipes"
        )

@router.post("/add-crew", response_model=TeamInstanceResponse)
async def add_crew_to_my_teams(
    team_data: TeamInstanceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ajoute une équipe du store aux équipes de l'utilisateur

    Args:
        team_data: Données de l'instance à créer (crew_id, custom_name)
        current_user: Utilisateur connecté
        db: Session de base de données

    Returns:
        TeamInstance créée

    Raises:
        HTTPException: Si l'équipe n'existe pas dans le store ou si l'utilisateur l'a déjà
    """
    try:
        logger.info(f"👤 Utilisateur {current_user['username']} ajoute l'équipe {team_data.crew_id}")
        
        # Vérifier si l'équipe existe dans le store
        crew = get_crew_by_id(db, team_data.crew_id)
        if not crew:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Équipe non trouvée dans le store"
            )

        # Vérifier si l'utilisateur a déjà ajouté cette équipe
        if check_user_has_crew(db, current_user["id"], team_data.crew_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cette équipe est déjà dans vos équipes"
            )

        # Créer l'instance de l'équipe pour l'utilisateur
        new_team_instance = create_team_instance(db, team_data, current_user["id"])
        
        logger.info(f"✅ Équipe {crew.name} ajoutée avec succès pour {current_user['username']}")
        
        return new_team_instance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout de l'équipe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'ajout de l'équipe"
        )

@router.post("/add-workflow")
async def add_workflow_to_my_teams(
    workflow_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ajoute un workflow du store aux workflows de l'utilisateur
    """
    try:
        workflow_id = workflow_data.get("workflow_id")
        logger.info(f"👤 Utilisateur {current_user['username']} ajoute le workflow {workflow_id}")
        
        # Vérifier si le workflow existe dans le store
        from app.models.workflow import Workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow non trouvé dans le store"
            )

        # Vérifier si l'utilisateur a déjà ajouté ce workflow
        from app.models.team_instance import TeamInstance
        existing = db.query(TeamInstance).filter(
            TeamInstance.user_id == current_user["id"],
            TeamInstance.workflow_id == workflow_id,
            TeamInstance.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ce workflow est déjà dans vos workflows"
            )

        # Créer l'instance de workflow pour l'utilisateur
        new_workflow_instance = TeamInstance(
            user_id=current_user["id"],
            workflow_id=workflow_id,
            name=workflow_data.get("name", workflow.name),
            is_active=True
        )
        
        db.add(new_workflow_instance)
        db.commit()
        db.refresh(new_workflow_instance)
        
        logger.info(f"✅ Workflow {workflow.name} ajouté avec succès pour {current_user['username']}")
        
        return {
            "id": new_workflow_instance.id,
            "name": new_workflow_instance.name,
            "workflow": {
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "category": workflow.category,
                "folder_name": workflow.folder_name
            },
            "is_active": new_workflow_instance.is_active,
            "created_at": new_workflow_instance.created_at.isoformat(),
            "last_executed": new_workflow_instance.last_executed.isoformat() if new_workflow_instance.last_executed else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'ajout du workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'ajout du workflow"
        )

@router.post("/{instance_id}/run")
async def run_my_team_instance(
    instance_id: UUID,
    input_data: CrewInput,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exécute une instance d'équipe CrewAI de l'utilisateur.

    Args:
        instance_id: ID de l'instance d'équipe à exécuter
        input_data: Données d'entrée pour le CrewAI (ex: {"topic": "AI trends"})
        current_user: Utilisateur connecté
        db: Session de base de données

    Returns:
        Résultat de l'exécution du CrewAI

    Raises:
        HTTPException: Si l'instance n'est pas trouvée ou n'appartient pas à l'utilisateur
    """
    try:
        logger.info(f"🚀 Utilisateur {current_user['username']} exécute l'instance {instance_id}")
        
        # Vérifier que l'instance appartient à l'utilisateur
        team_instance = get_team_instance_by_id(db, instance_id, current_user["id"])
        if not team_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance d'équipe non trouvée ou ne vous appartient pas"
            )

        # Récupérer les détails de l'équipe
        crew_details = get_crew_by_id(db, team_instance.crew_id)
        if not crew_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Définition d'équipe associée non trouvée"
            )

        # Préparer l'exécution via CrewExecutorService
        executor_service = CrewExecutorService()
        
        logger.info(f"🎯 Exécution de l'équipe {crew_details.folder_name} avec input: {input_data.topic}")
        
        # Exécuter l'équipe
        crew_output = await executor_service.execute_crew(
            crew_details.folder_name,
            {"topic": input_data.topic}
        )

        # Mettre à jour la date de dernière exécution
        update_team_instance_execution(db, instance_id, current_user["id"])

        logger.info(f"✅ Exécution terminée avec succès pour {current_user['username']}")

        return {
            "success": True,
            "message": "Exécution de l'équipe terminée avec succès",
            "data": crew_output,
            "team_name": team_instance.name or crew_details.name
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de l'équipe {crew_details.folder_name if 'crew_details' in locals() else 'inconnue'}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Échec de l'exécution de l'équipe: {str(e)}"
        )

@router.put("/{instance_id}", response_model=TeamInstanceResponse)
async def update_my_team(
    instance_id: UUID,
    team_update: TeamInstanceCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour une équipe de l'utilisateur (nom personnalisé, etc.)
    """
    try:
        logger.info(f"🔄 Mise à jour de l'équipe {instance_id} par {current_user['username']}")
        
        # Vérifier que l'instance existe et appartient à l'utilisateur
        team_instance = get_team_instance_by_id(db, instance_id, current_user["id"])
        if not team_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance d'équipe non trouvée ou ne vous appartient pas"
            )
        
        # Mettre à jour le nom personnalisé
        team_instance.name = team_update.name
        db.commit()
        db.refresh(team_instance)
        
        logger.info(f"✅ Équipe {instance_id} mise à jour avec succès")
        return team_instance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour"
        )

@router.delete("/{instance_id}")
async def remove_team(
    instance_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime une équipe des équipes de l'utilisateur (désactivation)
    """
    try:
        logger.info(f"🗑️ Suppression de l'équipe {instance_id} par {current_user['username']}")
        
        # Vérifier que l'instance existe et appartient à l'utilisateur
        team_instance = get_team_instance_by_id(db, instance_id, current_user["id"])
        if not team_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance d'équipe non trouvée ou ne vous appartient pas"
            )
        
        # Désactiver l'instance au lieu de la supprimer
        team_instance.is_active = False
        db.commit()
        
        logger.info(f"✅ Équipe {instance_id} supprimée avec succès")
        return {"message": "Équipe supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression"
        )

@router.delete("/{instance_id}/delete-cloned-workflow")
async def delete_cloned_workflow(
    instance_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime complètement un workflow cloné et nettoie toutes les données associées
    """
    try:
        logger.info(f"🗑️ Suppression complète du workflow cloné {instance_id} par {current_user['username']}")
        
        # Vérifier que l'instance existe et appartient à l'utilisateur
        team_instance = get_team_instance_by_id(db, instance_id, current_user["id"])
        if not team_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance d'équipe non trouvée ou ne vous appartient pas"
            )
        
        # Vérifier que c'est bien un workflow cloné
        if not team_instance.workflow_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette instance n'est pas un workflow"
            )
        
        from app.models.workflow import Workflow
        workflow = db.query(Workflow).filter(Workflow.id == team_instance.workflow_id).first()
        if not workflow or workflow.category != "Cloned":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce workflow n'est pas un workflow cloné"
            )
        
        # Supprimer dans N8N si possible
        try:
            if workflow.n8n_workflow_id:
                from app.services.n8n_executor import N8NExecutorService
                n8n_executor = N8NExecutorService()
                # Try to convert to int, but handle string IDs gracefully
                try:
                    n8n_id = int(workflow.n8n_workflow_id)
                    await n8n_executor.delete_workflow(n8n_id)
                    logger.info(f"✅ Workflow N8N {workflow.n8n_workflow_id} supprimé")
                except ValueError:
                    logger.warning(f"⚠️ N8N workflow ID '{workflow.n8n_workflow_id}' is not a valid integer, skipping N8N deletion")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la suppression N8N: {e}")
            # Continue même si la suppression N8N échoue
        
        # Supprimer les exécutions associées
        from app.models.workflow import WorkflowExecution
        db.query(WorkflowExecution).filter(WorkflowExecution.workflow_id == workflow.id).delete()
        
        # Supprimer la TeamInstance
        db.delete(team_instance)
        
        # Supprimer le Workflow cloné
        db.delete(workflow)
        
        db.commit()
        
        logger.info(f"✅ Workflow cloné {instance_id} supprimé complètement")
        return {
            "message": "Workflow cloné supprimé avec succès",
            "cleaned_up": {
                "team_instance": True,
                "workflow": True,
                "n8n_workflow": workflow.n8n_workflow_id is not None,
                "executions": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression complète: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression complète"
        )

@router.get("/debug/user")
async def debug_current_user(current_user: dict = Depends(get_current_user)):
    """Route de debug pour vérifier l'authentification"""
    return {
        "user": current_user, 
        "message": "Authentification OK",
        "user_id": current_user["id"],
        "username": current_user["username"]
    }