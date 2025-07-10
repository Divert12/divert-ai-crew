# Store API Router - Version Unifiée (Crews + Workflows N8N)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database.database import get_db
from app.schemas.crew import CrewResponse
from app.crud.crew import get_crews, get_crews_by_category, get_crew_by_id
from app.services.crew_executor import CrewDiscoveryService
from app.services.unified_discovery import UnifiedDiscoveryService 
from app.services.credential_manager import CredentialManager  
from app.core.security import get_current_user
from app.models.user import User  
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# ✅ NOUVEAUX : Services unifiés
unified_discovery = UnifiedDiscoveryService()
credential_manager = CredentialManager()

# ✅ GARDÉ : Endpoint legacy pour les crews (compatibilité)
@router.get("/crews", response_model=List[CrewResponse])
async def get_available_crews(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des équipes CrewAI disponibles dans le store
    Args:
        category: Filtre par catégorie (optionnel)
        db: Session de base de données
    Returns:
        Liste des équipes disponibles
    """
    try:
        logger.info(f"📋 Récupération des crews (catégorie: {category or 'toutes'})")
        
        if category:
            crews = get_crews_by_category(db, category)
            logger.info(f"✅ {len(crews)} crews trouvés dans la catégorie '{category}'")
        else:
            crews = get_crews(db)
            logger.info(f"✅ {len(crews)} crews trouvés au total")
        
        return crews
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des crews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des équipes: {str(e)}"
        )

# ✅ NOUVEAU : Endpoint unifié pour toutes les automations
@router.get("/automations")
async def get_all_automations(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    automation_type: Optional[str] = None,
    db: Session = Depends(get_db),
    # ✅ SUPPRIMÉ : current_user: User = Depends(get_current_user)
):
    """
    Récupère toutes les automations disponibles (crews CrewAI + workflows N8N)
    PUBLIQUE - Pas d'authentification requise
    """
    try:
        logger.info(f"🔍 Récupération des automations (type: {automation_type or 'tous'}, catégorie: {category or 'toutes'})")
        
        automations = []
        
        # Crews CrewAI
        if not automation_type or automation_type == "crewai":
            from app.models.crew import Crew
            crews_query = db.query(Crew).filter(Crew.is_active == True)
            if category:
                crews_query = crews_query.filter(Crew.category == category)
            
            crews = crews_query.offset(skip).limit(limit).all()
            for crew in crews:
                automations.append({
                    "id": crew.id,
                    "name": crew.name,
                    "description": crew.description,
                    "category": crew.category,
                    "folder_name": crew.folder_name,
                    "automation_type": "crewai",
                    "execution_type": "crew",
                    "is_active": crew.is_active,
                    "created_at": crew.created_at.isoformat() if crew.created_at else None,
                    "complexity": "Medium",
                    "integrations": [],
                    "required_credentials": [],
                    "can_execute": True  # Crews toujours exécutables
                })
        
        # Workflows N8N  
        if not automation_type or automation_type == "n8n_workflow":
            from app.models.workflow import Workflow
            workflows_query = db.query(Workflow).filter(
                Workflow.is_active == True, 
                Workflow.type == "n8n_workflow",
                Workflow.category != "Cloned"
            )
            if category:
                workflows_query = workflows_query.filter(Workflow.category == category)
            
            workflows = workflows_query.offset(skip).limit(limit).all()
            for workflow in workflows:
                automations.append({
                    "id": workflow.id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "category": workflow.category,
                    "folder_name": workflow.folder_name,
                    "automation_type": "n8n_workflow",
                    "execution_type": "workflow",
                    "is_active": workflow.is_active,
                    "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                    "complexity": "Low",
                    "node_count": workflow.node_count or 0,
                    "integrations": workflow.integrations or [],
                    "required_credentials": workflow.required_credentials or [],
                    "can_execute": True,  # ✅ Pas de vérification user-specific
                    "missing_credentials": []  # ✅ Vide car pas d'user
                })
        
        logger.info(f"✅ {len(automations)} automations trouvées")
        
        return {
            "automations": automations,
            "total": len(automations),
            "filters": {
                "category": category,
                "automation_type": automation_type,
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des automations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des automations: {str(e)}"
        )

# ✅ GARDÉ : Endpoint legacy pour les détails de crew
@router.get("/crews/{crew_id}", response_model=CrewResponse)
async def get_crew_details(crew_id: int, db: Session = Depends(get_db)):
    """
    Récupère les détails d'une équipe CrewAI spécifique
    Args:
        crew_id: ID de l'équipe
        db: Session de base de données
    Returns:
        Détails de l'équipe
    Raises:
        HTTPException: Si l'équipe n'existe pas
    """
    try:
        logger.info(f"🔍 Récupération des détails du crew ID: {crew_id}")
        
        crew = get_crew_by_id(db, crew_id)
        if not crew:
            logger.warning(f"❌ Crew non trouvé: {crew_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crew not found"
            )
        
        logger.info(f"✅ Crew trouvé: {crew.name}")
        return crew
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du crew {crew_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'équipe: {str(e)}"
        )

# ✅ NOUVEAU : Endpoint pour les détails d'automation (unifié)
@router.get("/automations/{automation_id}")
async def get_automation_details(
    automation_id: int,
    automation_type: str,  # "crewai" ou "n8n_workflow"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les détails d'une automation spécifique (crew ou workflow)
    """
    try:
        logger.info(f"🔍 Récupération des détails - Type: {automation_type}, ID: {automation_id}")
        
        if automation_type == "crewai":
            crew = get_crew_by_id(db, automation_id)
            if not crew:
                raise HTTPException(status_code=404, detail="Crew not found")
            
            return {
                **crew.__dict__,
                "automation_type": "crewai",
                "can_execute": True,
                "required_credentials": [],
                "missing_credentials": []
            }
            
        elif automation_type == "n8n_workflow":
            from app.models.workflow import Workflow
            workflow = db.query(Workflow).filter(Workflow.id == automation_id).first()
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            # Vérifier les credentials requis
            required_creds = workflow.required_credentials or []
            credential_status = credential_manager.validate_required_credentials(
                db, current_user.id, required_creds
            ) if required_creds else {}
            
            return {
                **workflow.__dict__,
                "automation_type": "n8n_workflow",
                "credential_status": credential_status,
                "can_execute": all(credential_status.values()) if credential_status else True,
                "missing_credentials": [
                    cred for cred, configured in credential_status.items() 
                    if not configured
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid automation type")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération de l'automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ MODIFIÉ : Endpoint unifié pour synchroniser tout
@router.post("/sync-all")
async def sync_all_automations(db: Session = Depends(get_db)):
    """
    Synchronise toutes les automations (crews CrewAI + workflows N8N) depuis le système de fichiers
    Args:
        db: Session de base de données
    Returns:
        Résultat de la synchronisation complète
    """
    try:
        logger.info("🔄 Synchronisation complète des automations depuis le système de fichiers")
        
        result = unified_discovery.auto_sync_all(db)
        
        logger.info(f"✅ Synchronisation complète terminée: {result}")
        
        return {
            "success": True,
            "message": "Automations synchronized successfully",
            "results": result
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation complète: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la synchronisation: {str(e)}"
        )

# ✅ GARDÉ : Endpoint legacy pour compatibilité (crews seulement)
@router.post("/refresh-crews")
async def refresh_crews_from_filesystem(db: Session = Depends(get_db)):
    """
    Rafraîchit la liste des équipes CrewAI en scannant le système de fichiers
    LEGACY: Utilisez /sync-all maintenant pour synchroniser tout
    """
    try:
        logger.info("🔄 Rafraîchissement des crews depuis le système de fichiers (legacy endpoint)")
        
        discovery_service = CrewDiscoveryService()
        result = discovery_service.sync_crews_with_database(db)
        
        logger.info(f"✅ Rafraîchissement crews terminé: {result}")
        
        return {
            "success": True,
            "message": "Crews refreshed successfully (consider using /sync-all for complete sync)",
            "added": result.get("added", 0),
            "updated": result.get("updated", 0),
            "total": result.get("total", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du rafraîchissement crews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du rafraîchissement: {str(e)}"
        )

# ✅ MODIFIÉ : Endpoint unifié pour les catégories
@router.get("/categories")
async def get_available_categories(db: Session = Depends(get_db)):
    """
    Récupère la liste des catégories disponibles pour tous les types d'automations
    """
    try:
        logger.info("📂 Récupération des catégories disponibles (crews + workflows)")
        
        from app.models.crew import Crew
        from app.models.workflow import Workflow
        
        # Récupérer les catégories des crews
        crew_categories = db.query(Crew.category).filter(
            Crew.is_active == True
        ).distinct().all()
        
        # Récupérer les catégories des workflows
        workflow_categories = db.query(Workflow.category).filter(
            Workflow.is_active == True,
            Workflow.type == "n8n_workflow"
        ).distinct().all()
        
        # Combiner et dédupliquer
        all_categories = set()
        for cat in crew_categories:
            if cat[0]:
                all_categories.add(cat[0])
        for cat in workflow_categories:
            if cat[0]:
                all_categories.add(cat[0])
        
        category_list = sorted(list(all_categories))
        
        logger.info(f"✅ {len(category_list)} catégories trouvées: {category_list}")
        
        return {
            "categories": category_list,
            "total": len(category_list),
            "sources": {
                "crews": len([cat[0] for cat in crew_categories if cat[0]]),
                "workflows": len([cat[0] for cat in workflow_categories if cat[0]])
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des catégories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des catégories: {str(e)}"
        )

# ✅ NOUVEAU : Statistiques du store
@router.get("/stats")
async def get_store_stats(db: Session = Depends(get_db)):
    """
    Récupère les statistiques du store (crews + workflows)
    """
    try:
        from app.models.crew import Crew
        from app.models.workflow import Workflow
        
        # Compter les crews
        total_crews = db.query(Crew).filter(Crew.is_active == True).count()
        
        # Compter les workflows
        total_workflows = db.query(Workflow).filter(
            Workflow.is_active == True,
            Workflow.type == "n8n_workflow"
        ).count()
        
        # Statistiques par catégorie
        crew_categories = db.query(Crew.category, db.func.count(Crew.id)).filter(
            Crew.is_active == True
        ).group_by(Crew.category).all()
        
        workflow_categories = db.query(Workflow.category, db.func.count(Workflow.id)).filter(
            Workflow.is_active == True,
            Workflow.type == "n8n_workflow"
        ).group_by(Workflow.category).all()
        
        return {
            "total_automations": total_crews + total_workflows,
            "crews": {
                "total": total_crews,
                "by_category": {cat: count for cat, count in crew_categories if cat}
            },
            "workflows": {
                "total": total_workflows,
                "by_category": {cat: count for cat, count in workflow_categories if cat}
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ NOUVEAUX : Endpoints pour les templates de workflows

@router.get("/workflows")
async def get_workflow_templates():
    """
    Récupère la liste des templates de workflows disponibles
    """
    try:
        from app.services.n8n_executor import N8NDiscoveryService
        import os
        import json
        
        discovery_service = N8NDiscoveryService()
        templates = discovery_service.discover_workflows()
        
        # Enrichir avec les services requis
        for template in templates:
            meta_path = os.path.join(
                discovery_service.workflows_base_path,
                template["folder_name"],
                "workflow_meta.json"
            )
            
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    template["required_services"] = meta.get("required_services", [])
                    template["required_credentials"] = meta.get("required_credentials", [])
                    template["webhook_path"] = meta.get("webhook_path", "")
                    template["features"] = meta.get("features", [])
        
        logger.info(f"✅ {len(templates)} workflow templates trouvés")
        
        return {
            "workflows": templates,
            "total": len(templates)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération des templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflows/{template_name}/clone")
async def clone_workflow_template(
    template_name: str,
    clone_request: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clone un template de workflow pour un utilisateur
    Body: { "userId": "...", "credentials": { "gmail": credId, "googleDrive": credId } }
    """
    try:
        from app.services.n8n_executor import N8NExecutorService, N8NDiscoveryService
        from sqlalchemy.orm import Session
        from app.database.database import get_db
        import os
        
        user_id = str(clone_request.get("userId", current_user["id"]))
        credentials = clone_request.get("credentials", {})
        
        # Vérifier que le template existe
        discovery_service = N8NDiscoveryService()
        template_path = os.path.join(
            discovery_service.workflows_base_path,
            template_name,
            "workflow.json"
        )
        
        if not os.path.exists(template_path):
            raise HTTPException(
                status_code=404,
                detail=f"Template '{template_name}' not found"
            )
        
        # Vérifier les services requis
        meta_path = os.path.join(
            discovery_service.workflows_base_path,
            template_name,
            "workflow_meta.json"
        )
        
        required_services = []
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                required_services = meta.get("required_services", [])
        
        # Vérifier que tous les credentials requis sont fournis
        # Permet le clonage même si aucun service n'est requis
        missing_services = []
        for service in required_services:
            if service not in credentials:
                missing_services.append(service)
        
        # Seulement bloquer si des services sont requis mais manquants
        if missing_services and required_services:
            raise HTTPException(
                status_code=400,
                detail=f"Missing credentials for services: {', '.join(missing_services)}"
            )
        
        # Imports needed for the function
        from app.models.team_instance import TeamInstance
        from app.models.workflow import Workflow
        import uuid
        
        # Vérifier si l'utilisateur a déjà cloné ce template
        existing_clone = db.query(TeamInstance).join(Workflow).filter(
            TeamInstance.user_id == int(user_id),
            TeamInstance.workflow_id.isnot(None),
            Workflow.category == "Cloned",
            Workflow.description.contains(f"Cloned from template {template_name}"),
            TeamInstance.is_active == True
        ).first()
        
        if existing_clone:
            raise HTTPException(
                status_code=409,
                detail=f"You have already cloned the template '{template_name}'. Check your my-teams page."
            )
        
        # Cloner le workflow
        executor_service = N8NExecutorService()
        workflow_id, webhook_url = await executor_service.clone_workflow(
            template_path, user_id, credentials
        )
        unique_folder_name = f"{template_name}_user_{user_id}_{str(uuid.uuid4())[:8]}"
        
        workflow_instance = Workflow(
            name=f"{template_name} - User {user_id}",
            description=f"Cloned from template {template_name}",
            folder_name=unique_folder_name,
            category="Cloned",
            type="n8n_workflow",
            n8n_workflow_id=str(workflow_id),
            is_active=True,
            required_credentials=list(credentials.keys())
        )
        
        db.add(workflow_instance)
        db.commit()
        db.refresh(workflow_instance)
        
        # Ajouter automatiquement le workflow aux équipes de l'utilisateur
        from app.models.team_instance import TeamInstance
        team_instance = TeamInstance(
            user_id=int(user_id),
            workflow_id=workflow_instance.id,
            name=f"{template_name} - User {user_id}",
            is_active=True
        )
        
        db.add(team_instance)
        db.commit()
        db.refresh(team_instance)
        
        logger.info(f"✅ Template '{template_name}' cloné avec succès: {workflow_id}")
        
        return {
            "success": True,
            "workflowId": workflow_id,
            "webhookUrl": webhook_url,
            "message": f"Workflow '{template_name}' cloned successfully",
            "database_id": workflow_instance.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors du clonage: {e}")
        raise HTTPException(status_code=500, detail=str(e))