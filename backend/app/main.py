from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from app.database.database import engine, Base
from app.routers import auth, store, my_teams, integrations
from app.core.security import get_current_user
import logging
import os
from dotenv import load_dotenv
from app.services.unified_discovery import UnifiedDiscoveryService
from app.database.database import get_db
from app.routers import workflows, integrations

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_encryption_key():
    """Set up encryption key for user credentials"""
    if not os.getenv("CREDENTIAL_ENCRYPTION_KEY"):
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        os.environ["CREDENTIAL_ENCRYPTION_KEY"] = key
        logger.warning(f"Generated encryption key for development: {key}")
        logger.warning("Set CREDENTIAL_ENCRYPTION_KEY in your .env file for production!")
        
        try:
            env_file = ".env"
            env_content = ""
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    env_content = f.read()
            
            if "CREDENTIAL_ENCRYPTION_KEY" not in env_content:
                with open(env_file, 'a') as f:
                    f.write(f"\nCREDENTIAL_ENCRYPTION_KEY={key}\n")
                logger.info("Encryption key saved to .env file")
        except Exception as e:
            logger.warning(f"Could not save key to .env: {e}")
    else:
        logger.info("Credential encryption key loaded from environment")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("Starting Divert.ai application...")
    
    setup_encryption_key()
    
    # Import models to register them
    from app.models.user import User, UserIntegration
    from app.models.crew import Crew
    from app.models.team_instance import TeamInstance
    from app.models.workflow import Workflow, WorkflowExecution
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        logger.error("Try deleting divert_ai.db and restarting")
        raise
    
    # Auto-sync crews and workflows on startup
    await sync_all_automations_on_startup()
    
    yield
    
    logger.info("Shutting down Divert.ai application...")

async def sync_all_automations_on_startup():
    """Sync CrewAI teams and N8N workflows on startup"""
    try:
        logger.info("Syncing automations...")
        
        unified_discovery = UnifiedDiscoveryService()
        db = next(get_db())
        
        try:
            result = unified_discovery.auto_sync_all(db)
            
            logger.info("Synchronization completed successfully:")
            logger.info(f"   Crews - Added: {result['crews']['added']}, Updated: {result['crews']['updated']}, Total: {result['crews']['total']}")
            logger.info(f"   Workflows - Added: {result['workflows']['added']}, Updated: {result['workflows']['updated']}, Total: {result['workflows']['total']}")
            
            if result.get('errors'):
                for error in result['errors']:
                    logger.warning(f"Warning: {error}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Automation sync failed: {e}")
        logger.error("Application continues without sync")

app = FastAPI(
    title="Divert.ai Backend",
    description="Backend for Divert.ai - AI Teams and Workflow Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(store.router, prefix="/store", tags=["Store"])
app.include_router(my_teams.router, prefix="/my-teams", tags=["My Teams"])
app.include_router(integrations.router, prefix="/integrations", tags=["External Integrations"])
app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])

@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "Welcome to Divert.ai API",
        "version": "1.0.0",
        "documentation": "/docs",
        "features": ["CrewAI Teams", "N8N Workflows", "External Integrations"]
    }

@app.get("/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user)):
    """User dashboard endpoint - requires authentication"""
    return {
        "message": f"Dashboard for {current_user['username']}",
        "user_id": current_user["id"],
        "status": "In development"
    }

# Route de vérification de santé de l'API
@app.get("/health")
async def health_check():
    """Route de vérification de santé de l'API"""
    return {
        "status": "healthy", 
        "service": "divert-ai-backend",
        "features": {
            "crews": "enabled",
            "workflows": "enabled", 
            "integrations": "enabled"
        }
    }

# Route pour déclencher une synchronisation manuelle complète
@app.post("/admin/sync-all")
async def manual_sync_all():
    """Déclenche une synchronisation manuelle des équipes CrewAI ET workflows N8N"""
    try:
        logger.info("🔄 Synchronisation manuelle complète demandée...")
        
        unified_discovery = UnifiedDiscoveryService()
        db = next(get_db())
        
        try:
            result = unified_discovery.auto_sync_all(db)
            logger.info(f"✅ Synchronisation manuelle terminée: {result}")
            return {
                "success": True,
                "message": "Synchronisation complète terminée avec succès",
                "results": result
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation manuelle: {e}")
        return {
            "success": False,
            "message": f"Erreur lors de la synchronisation: {str(e)}"
        }

# Routes pour l'exécution et le contrôle des workflows

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow_direct(
    workflow_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Lance l'exécution manuelle d'un workflow N8N."""
    try:
        from app.services.n8n_executor import N8NExecutorService
        from app.models.workflow import Workflow, WorkflowExecution
        
        db = next(get_db())
        
        try:
            # Vérifier que le workflow existe
            workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            # Créer un enregistrement d'exécution
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                user_id=current_user["id"],
                inputs={},
                status="running"
            )
            db.add(execution)
            db.commit()
            db.refresh(execution)
            
            # Exécuter via N8N
            executor = N8NExecutorService()
            n8n_workflow_id = int(workflow.n8n_workflow_id)
            result = await executor.execute_workflow_by_id(n8n_workflow_id)
            
            # Mettre à jour l'exécution
            execution.status = "success" if result["success"] else "failed"
            execution.outputs = result.get("data", {})
            execution.n8n_execution_id = result.get("execution_id")
            db.commit()
            
            logger.info(f"✅ Workflow {workflow_id} executed successfully")
            
            return {
                "success": True,
                "execution_id": execution.id,
                "result": result
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error executing workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/workflows/{workflow_id}")
async def toggle_workflow_direct(
    workflow_id: int,
    toggle_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Active ou désactive un workflow N8N."""
    try:
        from app.services.n8n_executor import N8NExecutorService
        from app.models.workflow import Workflow
        
        active = toggle_data.get("active", False)
        
        db = next(get_db())
        
        try:
            # Vérifier que le workflow existe
            workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            
            # Basculer l'état dans N8N
            executor = N8NExecutorService()
            n8n_workflow_id = int(workflow.n8n_workflow_id)
            await executor.toggle_workflow(n8n_workflow_id, active)
            
            # Mettre à jour en base de données
            workflow.is_active = active
            db.commit()
            
            logger.info(f"✅ Workflow {workflow_id} {'activated' if active else 'deactivated'}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "active": active,
                "message": f"Workflow {'activated' if active else 'deactivated'} successfully"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error toggling workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Route legacy pour compatibilité
@app.post("/admin/sync-crews")
async def manual_sync_crews():
    """Synchronisation manuelle des équipes CrewAI SEULEMENT (legacy)"""
    try:
        logger.info("🔄 Synchronisation manuelle des crews (legacy endpoint)...")
        
        from app.services.crew_executor import CrewDiscoveryService
        discovery = CrewDiscoveryService()
        db = next(get_db())
        
        try:
            result = discovery.sync_crews_with_database(db)
            logger.info(f"✅ Synchronisation crews terminée: {result}")
            return {
                "success": True,
                "message": "Synchronisation crews terminée avec succès",
                "result": result
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation crews: {e}")
        return {
            "success": False,
            "message": f"Erreur lors de la synchronisation: {str(e)}"
        }