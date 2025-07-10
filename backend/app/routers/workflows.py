from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
import json
import logging

from app.database.database import get_db
from app.core.security import get_current_user
from app.services.n8n_executor import N8NExecutorService, N8NDiscoveryService
from app.services.credential_manager import CredentialManager, INTEGRATION_TEMPLATES
from app.models.user import User
from app.models.workflow import Workflow, WorkflowExecution
from app.schemas.workflow import WorkflowResponse, CredentialCreate, WorkflowExecutionInput
from app.models.workflow import Workflow, WorkflowExecution
from app.models.user import  UserIntegration

logger = logging.getLogger(__name__) 

router = APIRouter()
n8n_executor = N8NExecutorService()
n8n_discovery = N8NDiscoveryService()
credential_manager = CredentialManager()

@router.get("/workflows", response_model=List[WorkflowResponse])
async def get_workflows(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des workflows disponibles."""
    query = db.query(Workflow).filter(Workflow.type == "n8n_workflow", Workflow.is_active == True, Workflow.category != "Cloned")
    
    if category:
        query = query.filter(Workflow.category == category)
    
    workflows = query.offset(skip).limit(limit).all()
    return workflows

@router.get("/workflows/{workflow_id}")
async def get_workflow_details(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les détails d'un workflow spécifique."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Vérifier les credentials requis pour cet utilisateur
    required_creds = workflow.required_credentials or []
    credential_status = credential_manager.validate_required_credentials(
        db, current_user.id, required_creds
    )
    
    return {
        **workflow.__dict__,
        "credential_status": credential_status,
        "missing_credentials": [
            cred for cred, configured in credential_status.items() 
            if not configured
        ]
    }

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: int,
    execution_input: WorkflowExecutionInput = WorkflowExecutionInput(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exécute un workflow N8N."""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Vérifier les credentials requis
    required_creds = workflow.required_credentials or []
    credential_status = credential_manager.validate_required_credentials(
        db, current_user.id, required_creds
    )
    
    missing_creds = [cred for cred, configured in credential_status.items() if not configured]
    if missing_creds:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing credentials for: {', '.join(missing_creds)}"
        )
    
    # Récupérer les credentials utilisateur
    user_credentials = {}
    for service in required_creds:
        creds = credential_manager.get_user_credentials(db, current_user.id, service)
        if creds:
            user_credentials[service] = creds
    
    try:
        # Vérifier que N8N est accessible
        if not await n8n_executor.check_n8n_health():
            raise HTTPException(status_code=503, detail="N8N service is not available")
        
        # Créer un enregistrement d'exécution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=current_user.id,
            inputs=execution_input.inputs,
            status="running"
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # Exécuter le workflow
        result = await n8n_executor.execute_workflow(
            workflow.folder_name, 
            execution_input.inputs, 
            user_credentials
        )
        
        # Mettre à jour l'exécution
        execution.status = "success" if result["success"] else "failed"
        execution.outputs = result.get("data", {})
        execution.n8n_execution_id = result.get("execution_id")
        db.commit()
        
        return {
            "execution_id": execution.id,
            "status": execution.status,
            "result": result
        }
        
    except Exception as e:
        # Mettre à jour l'exécution en cas d'erreur
        execution.status = "failed"
        execution.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/credentials/{service_name}")
async def store_credentials(
    service_name: str,
    credentials: CredentialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stocke les credentials d'un utilisateur pour un service."""
    if service_name not in INTEGRATION_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service_name}")
    
    template = INTEGRATION_TEMPLATES[service_name]
    
    try:
        stored_credential = credential_manager.store_user_credentials(
            db=db,
            user_id=current_user.id,
            service_name=service_name,
            credential_type=template["type"],
            credentials=credentials.credentials
        )
        
        return {
            "message": f"Credentials stored successfully for {service_name}",
            "credential_id": stored_credential.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credentials")
async def get_user_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les intégrations configurées par l'utilisateur."""
    integrations = credential_manager.get_user_integrations(db, current_user.id)
    
    return {
        "configured_integrations": integrations,
        "available_integrations": {
            name: {
                "type": template["type"],
                "fields": template["fields"],
                "instructions": template["instructions"]
            }
            for name, template in INTEGRATION_TEMPLATES.items()
        }
    }

@router.delete("/credentials/{service_name}")
async def delete_credentials(
    service_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime les credentials d'un service."""
    credential = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user.id,
        UserIntegration.service_name == service_name
    ).first()
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credentials not found")
    
    credential.is_active = False
    db.commit()
    
    return {"message": f"Credentials for {service_name} have been deactivated"}

@router.post("/sync-workflows")
async def sync_workflows(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Synchronise les workflows depuis le système de fichiers."""
    try:
        discovered_workflows = n8n_discovery.discover_workflows()
        added_count = 0
        updated_count = 0
        
        for workflow_data in discovered_workflows:
            existing = db.query(Workflow).filter(
                Workflow.folder_name == workflow_data["folder_name"]
            ).first()
            
            if existing:
                # Mettre à jour
                for key, value in workflow_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                updated_count += 1
            else:
                # Créer nouveau
                new_workflow = Workflow(**workflow_data)
                db.add(new_workflow)
                added_count += 1
        
        db.commit()
        
        return {
            "message": "Workflows synchronized successfully",
            "added": added_count,
            "updated": updated_count,
            "total": len(discovered_workflows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions")
async def get_user_executions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère l'historique des exécutions de l'utilisateur."""
    executions = db.query(WorkflowExecution).filter(
        WorkflowExecution.user_id == current_user.id
    ).order_by(WorkflowExecution.started_at.desc()).offset(skip).limit(limit).all()
    
    return executions

# Nouveaux endpoints pour le clonage de workflows

@router.get("/templates")
async def get_workflow_templates(db: Session = Depends(get_db)):
    """Récupère la liste des templates de workflows disponibles."""
    try:
        templates = n8n_discovery.discover_workflows()
        
        # Ajouter les services requis pour chaque template
        for template in templates:
            template_path = os.path.join(
                n8n_discovery.workflows_base_path, 
                template["folder_name"], 
                "workflow_meta.json"
            )
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    template["required_services"] = meta.get("required_services", [])
                    template["required_credentials"] = meta.get("required_credentials", [])
        
        return {
            "templates": templates,
            "total": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_name}/clone")
async def clone_workflow_template(
    template_name: str,
    clone_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clone un template de workflow pour un utilisateur avec ses credentials."""
    try:
        user_id = str(current_user.id)
        credential_map = clone_data.get("credentials", {})
        
        # Construire le chemin vers le template
        template_path = os.path.join(
            n8n_discovery.workflows_base_path,
            template_name,
            "workflow.json"
        )
        
        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")
        
        # Vérifier que l'utilisateur a les credentials requis
        meta_path = os.path.join(
            n8n_discovery.workflows_base_path,
            template_name,
            "workflow_meta.json"
        )
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                required_services = meta.get("required_services", [])
                
                # Vérifier que tous les services requis ont des credentials
                # Permet le clonage même si aucun service n'est requis
                missing_services = []
                for service in required_services:
                    if service not in credential_map:
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
        workflow_id, webhook_url = await n8n_executor.clone_workflow(
            template_path, user_id, credential_map
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
            required_credentials=list(credential_map.keys())
        )
        
        db.add(workflow_instance)
        db.commit()
        db.refresh(workflow_instance)
        
        # Ajouter automatiquement le workflow aux équipes de l'utilisateur
        from app.models.team_instance import TeamInstance
        team_instance = TeamInstance(
            user_id=current_user.id,
            workflow_id=workflow_instance.id,
            name=f"{template_name} - User {user_id}",
            is_active=True
        )
        
        db.add(team_instance)
        db.commit()
        db.refresh(team_instance)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "webhook_url": webhook_url,
            "database_id": workflow_instance.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cloning workflow template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{workflow_id}/execute")
async def execute_workflow_instance(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lance l'exécution manuelle d'une instance de workflow."""
    try:
        # Vérifier que le workflow existe et appartient à l'utilisateur
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Utiliser l'ID N8N pour l'exécution
        n8n_workflow_id = int(workflow.n8n_workflow_id)
        
        # Créer un enregistrement d'exécution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=current_user.id,
            inputs={},
            status="running"
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # Exécuter via N8N
        result = await n8n_executor.execute_workflow_by_id(n8n_workflow_id)
        
        # Mettre à jour l'exécution
        execution.status = "success" if result["success"] else "failed"
        execution.outputs = result.get("data", {})
        execution.n8n_execution_id = result.get("execution_id")
        db.commit()
        
        return {
            "success": True,
            "execution_id": execution.id,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/instances/{workflow_id}")
async def toggle_workflow_instance(
    workflow_id: int,
    toggle_data: Dict[str, bool],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Active ou désactive une instance de workflow."""
    try:
        active = toggle_data.get("active", False)
        
        # Vérifier que le workflow existe
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Basculer l'état dans N8N
        n8n_workflow_id = int(workflow.n8n_workflow_id)
        await n8n_executor.toggle_workflow(n8n_workflow_id, active)
        
        # Mettre à jour en base de données
        workflow.is_active = active
        db.commit()
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "active": active,
            "message": f"Workflow {'activated' if active else 'deactivated'} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))