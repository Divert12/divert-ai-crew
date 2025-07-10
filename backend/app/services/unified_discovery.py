# app/services/unified_discovery.py
import os
import json
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.services.crew_executor import CrewDiscoveryService
from app.services.n8n_executor import N8NDiscoveryService

logger = logging.getLogger(__name__)

class UnifiedDiscoveryService:
    """
    Service unifié pour découvrir automatiquement les crews ET les workflows N8N.
    """
    
    def __init__(self):
        self.crew_discovery = CrewDiscoveryService()
        self.n8n_discovery = N8NDiscoveryService()
    
    def auto_sync_all(self, db: Session) -> Dict[str, Any]:
        """
        Synchronise automatiquement tous les crews et workflows.
        À appeler au démarrage de l'app ou via endpoint.
        """
        results = {
            "crews": {"added": 0, "updated": 0, "total": 0},
            "workflows": {"added": 0, "updated": 0, "total": 0},
            "errors": []
        }
        
        try:
            # Synchroniser les crews CrewAI
            crew_result = self.crew_discovery.sync_crews_with_database(db)
            results["crews"] = crew_result
            
            # Synchroniser les workflows N8N
            workflow_result = self.sync_n8n_workflows(db)
            results["workflows"] = workflow_result
            
        except Exception as e:
            logger.error(f"Error during auto-sync: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def sync_n8n_workflows(self, db: Session) -> Dict[str, int]:
        """
        Synchronise les workflows N8N avec la base de données.
        """
        from app.models.workflow import Workflow
        
        discovered_workflows = self.n8n_discovery.discover_workflows()
        added_count = 0
        updated_count = 0
        
        for workflow_data in discovered_workflows:
            try:
                existing = db.query(Workflow).filter(
                    Workflow.folder_name == workflow_data["folder_name"],
                    Workflow.type == "n8n_workflow"
                ).first()
                
                if existing:
                    # Mettre à jour si nécessaire (exclure les champs auto-gérés)
                    excluded_fields = {'created_at', 'updated_at', 'id'}
                    changed = False
                    for key, value in workflow_data.items():
                        if key not in excluded_fields and hasattr(existing, key) and getattr(existing, key) != value:
                            setattr(existing, key, value)
                            changed = True
                    
                    if changed:
                        db.commit()
                        db.refresh(existing)
                        updated_count += 1
                        logger.info(f"Updated N8N workflow: {existing.name}")
                else:
                    # Créer nouveau workflow
                    new_workflow = Workflow(
                        name=workflow_data["name"],
                        description=workflow_data["description"],
                        folder_name=workflow_data["folder_name"],
                        category=workflow_data["category"],
                        type="n8n_workflow",
                        node_count=workflow_data.get("node_count", 0),
                        integrations=workflow_data.get("integrations", []),
                        required_credentials=workflow_data.get("required_credentials", []),
                        is_active=True
                    )
                    db.add(new_workflow)
                    db.commit()
                    db.refresh(new_workflow)
                    added_count += 1
                    logger.info(f"Added new N8N workflow: {new_workflow.name}")
                    
            except Exception as e:
                logger.error(f"Error syncing workflow {workflow_data.get('folder_name', 'unknown')}: {e}")
        
        return {"added": added_count, "updated": updated_count, "total": len(discovered_workflows)}