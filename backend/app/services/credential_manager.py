import os
import json
import base64
from cryptography.fernet import Fernet
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.user import UserIntegration

class CredentialManager:
    """
    Gestionnaire sécurisé des credentials utilisateur pour les intégrations.
    """
    
    def __init__(self):
        # Clé de chiffrement depuis les variables d'environnement
        encryption_key = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
        if not encryption_key:
            # Générer une clé pour le développement (à ne pas faire en production)
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  Generated encryption key: {encryption_key}")
            print("⚠️  Set CREDENTIAL_ENCRYPTION_KEY environment variable in production!")
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """Chiffre les credentials utilisateur."""
        credentials_json = json.dumps(credentials)
        encrypted_data = self.cipher.encrypt(credentials_json.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, Any]:
        """Déchiffre les credentials utilisateur."""
        try:
            encrypted_data = base64.b64decode(encrypted_credentials.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {e}")

    def store_user_credentials(self, 
                             db: Session, 
                             user_id: int, 
                             service_name: str, 
                             credential_type: str,
                             credentials: Dict[str, Any]) -> UserIntegration:
        """
        Stocke les credentials utilisateur de manière sécurisée.
        """
        # Vérifier si des credentials existent déjà
        existing = db.query(UserIntegration).filter(
            UserIntegration.user_id == user_id,
            UserIntegration.service_name == service_name
        ).first()

        encrypted_creds = self.encrypt_credentials(credentials)

        if existing:
            # Mettre à jour
            existing.encrypted_credentials = encrypted_creds
            existing.credential_type = credential_type
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Créer nouveau
            new_credential = UserIntegration(
                user_id=user_id,
                service_name=service_name,
                credential_type=credential_type,
                encrypted_credentials=encrypted_creds,
                is_active=True
            )
            db.add(new_credential)
            db.commit()
            db.refresh(new_credential)
            return new_credential

    def get_user_credentials(self, 
                           db: Session, 
                           user_id: int, 
                           service_name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère et déchiffre les credentials utilisateur.
        """
        credential = db.query(UserIntegration).filter(
            UserIntegration.user_id == user_id,
            UserIntegration.service_name == service_name,
            UserIntegration.is_active == True
        ).first()

        if credential:
            return self.decrypt_credentials(credential.encrypted_credentials)
        return None

    def get_user_integrations(self, db: Session, user_id: int) -> Dict[str, str]:
        """
        Récupère toutes les intégrations configurées pour un utilisateur.
        """
        credentials = db.query(UserIntegration).filter(
            UserIntegration.user_id == user_id,
            UserIntegration.is_active == True
        ).all()

        return {
            cred.service_name: cred.credential_type 
            for cred in credentials
        }

    def validate_required_credentials(self, 
                                    db: Session, 
                                    user_id: int, 
                                    required_integrations: list) -> Dict[str, bool]:
        """
        Vérifie si l'utilisateur a configuré toutes les intégrations requises.
        """
        user_integrations = self.get_user_integrations(db, user_id)
        
        return {
            integration: integration in user_integrations
            for integration in required_integrations
        }

# Templates de configuration pour les intégrations populaires
INTEGRATION_TEMPLATES = {
    "telegram": {
        "type": "api_key",
        "fields": [
            {"name": "bot_token", "type": "password", "required": True, "description": "Token du bot Telegram"},
            {"name": "chat_id", "type": "text", "required": False, "description": "ID du chat (optionnel)"}
        ],
        "instructions": "1. Créez un bot via @BotFather sur Telegram\n2. Copiez le token fourni\n3. Optionnel: obtenez votre chat_id en envoyant /start au bot"
    },
    "gmail": {
        "type": "oauth",
        "fields": [
            {"name": "client_id", "type": "text", "required": True, "description": "Client ID Google"},
            {"name": "client_secret", "type": "password", "required": True, "description": "Client Secret Google"},
            {"name": "refresh_token", "type": "password", "required": True, "description": "Refresh Token"}
        ],
        "instructions": "1. Créez un projet dans Google Cloud Console\n2. Activez l'API Gmail\n3. Créez des identifiants OAuth 2.0\n4. Autorisez l'application et récupérez le refresh token"
    },
    "slack": {
        "type": "api_key",
        "fields": [
            {"name": "webhook_url", "type": "password", "required": True, "description": "URL du webhook Slack"},
            {"name": "channel", "type": "text", "required": False, "description": "Canal par défaut"}
        ],
        "instructions": "1. Allez dans votre workspace Slack\n2. Créez une nouvelle app\n3. Ajoutez un webhook entrant\n4. Copiez l'URL du webhook"
    },
    "discord": {
        "type": "api_key",
        "fields": [
            {"name": "webhook_url", "type": "password", "required": True, "description": "URL du webhook Discord"},
            {"name": "username", "type": "text", "required": False, "description": "Nom d'utilisateur du bot (optionnel)"}
        ],
        "instructions": "1. Allez dans les paramètres de votre serveur Discord\n2. Intégrations > Webhooks\n3. Créez un nouveau webhook\n4. Copiez l'URL"
    },
    "openai": {
        "type": "api_key",
        "fields": [
            {"name": "api_key", "type": "password", "required": True, "description": "Clé API OpenAI"},
            {"name": "organization", "type": "text", "required": False, "description": "ID de l'organisation (optionnel)"}
        ],
        "instructions": "1. Connectez-vous à platform.openai.com\n2. Allez dans API Keys\n3. Créez une nouvelle clé secrète\n4. Copiez la clé"
    },
    "google_sheets": {
        "type": "service_account",
        "fields": [
            {"name": "service_account_email", "type": "text", "required": True, "description": "Email du compte de service"},
            {"name": "private_key", "type": "textarea", "required": True, "description": "Clé privée du compte de service"}
        ],
        "instructions": "1. Créez un projet dans Google Cloud Console\n2. Activez l'API Google Sheets\n3. Créez un compte de service\n4. Téléchargez le fichier JSON et copiez les valeurs"
    },
    "google_drive": {
        "type": "oauth",
        "fields": [
            {"name": "client_id", "type": "text", "required": True, "description": "Client ID Google"},
            {"name": "client_secret", "type": "password", "required": True, "description": "Client Secret Google"},
            {"name": "refresh_token", "type": "password", "required": True, "description": "Refresh Token"}
        ],
        "instructions": "1. Créez un projet dans Google Cloud Console\n2. Activez l'API Google Drive\n3. Créez des identifiants OAuth 2.0\n4. Autorisez l'application et récupérez le refresh token"
    },
    "twitter": {
        "type": "oauth",
        "fields": [
            {"name": "api_key", "type": "text", "required": True, "description": "Twitter API Key"},
            {"name": "api_secret", "type": "password", "required": True, "description": "Twitter API Secret"},
            {"name": "access_token", "type": "password", "required": True, "description": "Access Token"},
            {"name": "access_token_secret", "type": "password", "required": True, "description": "Access Token Secret"}
        ],
        "instructions": "1. Créez une app sur developer.twitter.com\n2. Générez vos clés API\n3. Activez l'authentification OAuth 1.0a\n4. Copiez tous les tokens"
    },
    "facebook": {
        "type": "oauth",
        "fields": [
            {"name": "app_id", "type": "text", "required": True, "description": "Facebook App ID"},
            {"name": "app_secret", "type": "password", "required": True, "description": "Facebook App Secret"},
            {"name": "access_token", "type": "password", "required": True, "description": "Page Access Token"}
        ],
        "instructions": "1. Créez une app sur developers.facebook.com\n2. Ajoutez les produits nécessaires\n3. Générez un token d'accès de page\n4. Copiez l'App ID, Secret et Token"
    },
    "instagram": {
        "type": "oauth",
        "fields": [
            {"name": "access_token", "type": "password", "required": True, "description": "Instagram Access Token"},
            {"name": "business_account_id", "type": "text", "required": True, "description": "Business Account ID"}
        ],
        "instructions": "1. Connectez votre compte Instagram à Facebook\n2. Créez une app Facebook\n3. Générez un token Instagram\n4. Récupérez votre Business Account ID"
    },
    "linkedin": {
        "type": "oauth",
        "fields": [
            {"name": "client_id", "type": "text", "required": True, "description": "LinkedIn Client ID"},
            {"name": "client_secret", "type": "password", "required": True, "description": "LinkedIn Client Secret"},
            {"name": "access_token", "type": "password", "required": True, "description": "Access Token"}
        ],
        "instructions": "1. Créez une app sur developer.linkedin.com\n2. Configurez les permissions nécessaires\n3. Générez un access token\n4. Copiez les identifiants"
    },
    "youtube": {
        "type": "oauth",
        "fields": [
            {"name": "client_id", "type": "text", "required": True, "description": "Google Client ID"},
            {"name": "client_secret", "type": "password", "required": True, "description": "Google Client Secret"},
            {"name": "refresh_token", "type": "password", "required": True, "description": "Refresh Token"}
        ],
        "instructions": "1. Créez un projet Google Cloud\n2. Activez l'API YouTube\n3. Créez des identifiants OAuth\n4. Autorisez et récupérez le refresh token"
    },
    "notion": {
        "type": "api_key",
        "fields": [
            {"name": "token", "type": "password", "required": True, "description": "Notion Integration Token"},
            {"name": "database_id", "type": "text", "required": False, "description": "Database ID (optionnel)"}
        ],
        "instructions": "1. Allez sur notion.so/my-integrations\n2. Créez une nouvelle intégration\n3. Copiez le token\n4. Partagez vos pages avec l'intégration"
    },
    "airtable": {
        "type": "api_key",
        "fields": [
            {"name": "api_key", "type": "password", "required": True, "description": "Airtable API Key"},
            {"name": "base_id", "type": "text", "required": False, "description": "Base ID (optionnel)"}
        ],
        "instructions": "1. Allez dans votre compte Airtable\n2. Générez une clé API\n3. Trouvez votre Base ID\n4. Copiez les identifiants"
    },
    "zapier": {
        "type": "api_key",
        "fields": [
            {"name": "webhook_url", "type": "password", "required": True, "description": "Zapier Webhook URL"}
        ],
        "instructions": "1. Créez un nouveau Zap\n2. Utilisez Webhooks comme trigger\n3. Copiez l'URL du webhook\n4. Configurez votre automation"
    },
    "hubspot": {
        "type": "api_key",
        "fields": [
            {"name": "api_key", "type": "password", "required": True, "description": "HubSpot API Key"},
            {"name": "portal_id", "type": "text", "required": False, "description": "Portal ID (optionnel)"}
        ],
        "instructions": "1. Allez dans vos paramètres HubSpot\n2. Intégrations > Clés API\n3. Générez une nouvelle clé\n4. Copiez la clé et votre Portal ID"
    },
    "salesforce": {
        "type": "oauth",
        "fields": [
            {"name": "consumer_key", "type": "text", "required": True, "description": "Consumer Key"},
            {"name": "consumer_secret", "type": "password", "required": True, "description": "Consumer Secret"},
            {"name": "access_token", "type": "password", "required": True, "description": "Access Token"}
        ],
        "instructions": "1. Créez une Connected App\n2. Configurez OAuth\n3. Générez les tokens\n4. Copiez tous les identifiants"
    },
    "stripe": {
        "type": "api_key",
        "fields": [
            {"name": "secret_key", "type": "password", "required": True, "description": "Stripe Secret Key"},
            {"name": "publishable_key", "type": "text", "required": False, "description": "Publishable Key (optionnel)"}
        ],
        "instructions": "1. Connectez-vous à Stripe Dashboard\n2. Allez dans API Keys\n3. Révélez votre Secret Key\n4. Copiez les clés"
    },
    "paypal": {
        "type": "oauth",
        "fields": [
            {"name": "client_id", "type": "text", "required": True, "description": "PayPal Client ID"},
            {"name": "client_secret", "type": "password", "required": True, "description": "PayPal Client Secret"}
        ],
        "instructions": "1. Créez une app sur developer.paypal.com\n2. Configurez les permissions\n3. Copiez Client ID et Secret\n4. Activez les webhooks si nécessaire"
    },
    "shopify": {
        "type": "api_key",
        "fields": [
            {"name": "api_key", "type": "password", "required": True, "description": "Shopify Private App API Key"},
            {"name": "password", "type": "password", "required": True, "description": "Shopify Private App Password"},
            {"name": "shop_domain", "type": "text", "required": True, "description": "Shop Domain (ex: mystore.myshopify.com)"}
        ],
        "instructions": "1. Allez dans votre admin Shopify\n2. Apps > Manage private apps\n3. Créez une nouvelle app privée\n4. Copiez API Key, Password et votre domaine"
    },
    "aws": {
        "type": "service_account",
        "fields": [
            {"name": "access_key_id", "type": "text", "required": True, "description": "AWS Access Key ID"},
            {"name": "secret_access_key", "type": "password", "required": True, "description": "AWS Secret Access Key"},
            {"name": "region", "type": "text", "required": True, "description": "AWS Region (ex: us-east-1)"}
        ],
        "instructions": "1. Connectez-vous à AWS Console\n2. IAM > Users\n3. Créez un utilisateur\n4. Attachez les permissions et générez les clés"
    },
    "azure": {
        "type": "service_account",
        "fields": [
            {"name": "client_id", "type": "text", "required": True, "description": "Azure Client ID"},
            {"name": "client_secret", "type": "password", "required": True, "description": "Azure Client Secret"},
            {"name": "tenant_id", "type": "text", "required": True, "description": "Azure Tenant ID"}
        ],
        "instructions": "1. Allez dans Azure Portal\n2. Azure Active Directory > App registrations\n3. Créez une nouvelle app\n4. Générez un secret et copiez les IDs"
    },
    "gcp": {
        "type": "service_account",
        "fields": [
            {"name": "service_account_email", "type": "text", "required": True, "description": "Service Account Email"},
            {"name": "private_key", "type": "textarea", "required": True, "description": "Private Key"},
            {"name": "project_id", "type": "text", "required": True, "description": "Google Cloud Project ID"}
        ],
        "instructions": "1. Allez dans Google Cloud Console\n2. IAM > Service Accounts\n3. Créez un compte de service\n4. Téléchargez le JSON et copiez les valeurs"
    }
}