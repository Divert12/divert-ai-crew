from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.sql import func

from app.database.database import get_db
from app.core.security import get_current_user
from app.services.credential_manager import CredentialManager, INTEGRATION_TEMPLATES
from app.models.user import User, UserIntegration
from app.models.user import User, UserIntegration 

router = APIRouter()
credential_manager = CredentialManager()

class CredentialRequest(BaseModel):
    service_name: str
    credentials: Dict[str, str]

class IntegrationResponse(BaseModel):
    service_name: str
    status: str
    service_type: str
    configured_at: str = None

# Public endpoint to get available integration templates
@router.get("/templates", response_model=List[Dict[str, Any]])
async def get_integration_templates():
    """Récupère la liste des templates d'intégrations disponibles (public)."""
    
    integrations = []
    for service_name, template in INTEGRATION_TEMPLATES.items():
        integrations.append({
            "service_name": service_name,
            "display_name": service_name.replace('_', ' ').title(),
            "service_type": template["type"],
            "fields": template["fields"],
            "instructions": template["instructions"],
            "status": "not_configured",
            "is_configured": False,
            "configured_at": None,
            "icon": f"/icons/{service_name}.svg"
        })
    
    return integrations

@router.get("/", response_model=List[Dict[str, Any]])
async def get_available_integrations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère toutes les intégrations disponibles avec leur statut pour l'utilisateur."""
    
    # Récupérer les intégrations configurées par l'utilisateur
    user_integrations = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user["id"],
        UserIntegration.is_active == True
    ).all()
    
    configured_services = {
        integration.service_name: {
            "status": integration.status,
            "configured_at": integration.created_at.isoformat() if integration.created_at else None
        }
        for integration in user_integrations
    }
    
    # Préparer la liste complète avec statuts
    integrations = []
    for service_name, template in INTEGRATION_TEMPLATES.items():
        is_configured = service_name in configured_services
        integrations.append({
            "service_name": service_name,
            "display_name": service_name.replace('_', ' ').title(),
            "service_type": template["type"],
            "fields": template["fields"],
            "instructions": template["instructions"],
            "status": configured_services.get(service_name, {}).get("status", "not_configured"),
            "is_configured": is_configured,
            "configured_at": configured_services.get(service_name, {}).get("configured_at"),
            "icon": f"/icons/{service_name}.svg"
        })
    
    return integrations

@router.get("/integrations", response_model=List[Dict[str, Any]])
async def get_available_integrations_alt(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Récupère toutes les intégrations disponibles avec leur statut pour l'utilisateur."""
    
    # Récupérer les intégrations configurées par l'utilisateur
    user_integrations = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user["id"],
        UserIntegration.is_active == True
    ).all()
    
    configured_services = {
        integration.service_name: {
            "status": integration.status,
            "configured_at": integration.created_at.isoformat() if integration.created_at else None
        }
        for integration in user_integrations
    }
    
    # Préparer la liste complète avec statuts
    integrations = []
    for service_name, template in INTEGRATION_TEMPLATES.items():
        is_configured = service_name in configured_services
        integrations.append({
            "service_name": service_name,
            "display_name": service_name.replace('_', ' ').title(),
            "service_type": template["type"],
            "fields": template["fields"],
            "instructions": template["instructions"],
            "status": configured_services.get(service_name, {}).get("status", "not_configured"),
            "is_configured": is_configured,
            "configured_at": configured_services.get(service_name, {}).get("configured_at"),
            "icon": f"/icons/{service_name}.svg"
        })
    
    return integrations

@router.post("/configure")
async def configure_integration(
    request: CredentialRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Configure une nouvelle intégration pour l'utilisateur."""
    
    service_name = request.service_name.lower()
    
    # Vérifier que le service est supporté
    if service_name not in INTEGRATION_TEMPLATES:
        raise HTTPException(
            status_code=400, 
            detail=f"Service '{service_name}' is not supported"
        )
    
    template = INTEGRATION_TEMPLATES[service_name]
    
    # Valider les champs requis
    required_fields = [field["name"] for field in template["fields"] if field["required"]]
    missing_fields = [field for field in required_fields if field not in request.credentials]
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    try:
        # Tester la configuration (optionnel - implement selon vos besoins)
        test_result = await test_integration(service_name, request.credentials)
        
        # Sauvegarder les credentials
        credential_manager.store_user_credentials(
            db=db,
            user_id=current_user["id"],
            service_name=service_name,
            credential_type=template["type"],
            credentials=request.credentials
        )
        
        # Mettre à jour le statut
        integration = db.query(UserIntegration).filter(
            UserIntegration.user_id == current_user["id"],
            UserIntegration.service_name == service_name
        ).first()
        
        if integration:
            integration.status = "connected" if test_result else "error"
            integration.last_tested = func.now()
            db.commit()
        
        return {
            "message": f"{service_name.title()} integration configured successfully",
            "status": "connected" if test_result else "error",
            "service_name": service_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{service_name}")
async def remove_integration(
    service_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Supprime une intégration."""
    
    integration = db.query(UserIntegration).filter(
        UserIntegration.user_id == current_user["id"],
        UserIntegration.service_name == service_name.lower()
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration.is_active = False
    integration.status = "not_configured"
    db.commit()
    
    return {"message": f"{service_name.title()} integration removed successfully"}

@router.post("/{service_name}/test")
async def test_integration_endpoint(
    service_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Teste une intégration existante."""
    
    # Récupérer les credentials
    credentials = credential_manager.get_user_credentials(db, current_user["id"], service_name.lower())
    
    if not credentials:
        raise HTTPException(status_code=404, detail="Integration not configured")
    
    try:
        test_result = await test_integration(service_name.lower(), credentials)
        
        # Mettre à jour le statut
        integration = db.query(UserIntegration).filter(
            UserIntegration.user_id == current_user["id"],
            UserIntegration.service_name == service_name.lower()
        ).first()
        
        if integration:
            integration.status = "connected" if test_result else "error"
            integration.last_tested = func.now()
            db.commit()
        
        return {
            "status": "connected" if test_result else "error",
            "message": "Test successful" if test_result else "Test failed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def test_integration(service_name: str, credentials: Dict[str, str]) -> bool:
    """Teste si une intégration fonctionne correctement."""
    
    try:
        if service_name == "telegram":
            # Test simple pour Telegram
            import aiohttp
            token = credentials.get("bot_token")
            if not token:
                return False
                
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.telegram.org/bot{token}/getMe") as response:
                    return response.status == 200
                    
        elif service_name == "discord":
            # Test pour Discord webhook
            webhook_url = credentials.get("webhook_url")
            if not webhook_url:
                return False
            return "discord.com/api/webhooks" in webhook_url
            
        elif service_name == "slack":
            # Test pour Slack webhook
            webhook_url = credentials.get("webhook_url")
            if not webhook_url:
                return False
            return "hooks.slack.com" in webhook_url
            
        elif service_name == "gmail":
            # Test pour Gmail OAuth2
            client_id = credentials.get("client_id")
            client_secret = credentials.get("client_secret")
            refresh_token = credentials.get("refresh_token")
            
            if not all([client_id, client_secret, refresh_token]):
                return False
            
            # Test de base - vérifier que les credentials sont présents
            return True
            
        elif service_name == "google_drive":
            # Test pour Google Drive OAuth2
            client_id = credentials.get("client_id")
            client_secret = credentials.get("client_secret")
            refresh_token = credentials.get("refresh_token")
            
            if not all([client_id, client_secret, refresh_token]):
                return False
            
            # Test de base - vérifier que les credentials sont présents
            return True
            
        elif service_name == "openai":
            # Test pour OpenAI API
            api_key = credentials.get("api_key")
            if not api_key:
                return False
            return api_key.startswith("sk-")
            
        elif service_name == "twitter":
            # Test pour Twitter API
            required_fields = ["api_key", "api_secret", "access_token", "access_token_secret"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "facebook":
            # Test pour Facebook API
            required_fields = ["app_id", "app_secret", "access_token"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "instagram":
            # Test pour Instagram API
            required_fields = ["access_token", "business_account_id"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "linkedin":
            # Test pour LinkedIn API
            required_fields = ["client_id", "client_secret", "access_token"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "youtube":
            # Test pour YouTube API
            required_fields = ["client_id", "client_secret", "refresh_token"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "notion":
            # Test pour Notion API
            token = credentials.get("token")
            return bool(token and token.startswith("secret_"))
            
        elif service_name == "airtable":
            # Test pour Airtable API
            api_key = credentials.get("api_key")
            return bool(api_key and api_key.startswith("key"))
            
        elif service_name == "zapier":
            # Test pour Zapier Webhook
            webhook_url = credentials.get("webhook_url")
            return bool(webhook_url and "hooks.zapier.com" in webhook_url)
            
        elif service_name == "hubspot":
            # Test pour HubSpot API
            api_key = credentials.get("api_key")
            return bool(api_key and len(api_key) > 20)
            
        elif service_name == "salesforce":
            # Test pour Salesforce API
            required_fields = ["consumer_key", "consumer_secret", "access_token"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "stripe":
            # Test pour Stripe API
            secret_key = credentials.get("secret_key")
            return bool(secret_key and secret_key.startswith("sk_"))
            
        elif service_name == "paypal":
            # Test pour PayPal API
            required_fields = ["client_id", "client_secret"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "shopify":
            # Test pour Shopify API
            required_fields = ["api_key", "password", "shop_domain"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "aws":
            # Test pour AWS
            required_fields = ["access_key_id", "secret_access_key", "region"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "azure":
            # Test pour Azure
            required_fields = ["client_id", "client_secret", "tenant_id"]
            return all(credentials.get(field) for field in required_fields)
            
        elif service_name == "gcp":
            # Test pour Google Cloud Platform
            required_fields = ["service_account_email", "private_key", "project_id"]
            return all(credentials.get(field) for field in required_fields)
            
        # Default validation for unknown services
        return True
        
    except Exception as e:
        print(f"Test failed for {service_name}: {e}")
        return False