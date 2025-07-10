import os
import json
import logging
import asyncio
import aiohttp
import uuid
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class N8NExecutorService:
    """
    Service pour exécuter des workflows N8N via l'API N8N locale.
    """
    def __init__(self, 
                 workflows_root_dir: str = "static/workflows",
                 n8n_api_url: str = "http://localhost:5678/api/v1"):
        self.workflows_base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", workflows_root_dir
        )
        self.workflows_base_path = os.path.normpath(self.workflows_base_path)
        self.n8n_api_url = n8n_api_url
        
        # Configuration de l'authentification N8N
        self.n8n_api_key = os.getenv("N8N_API_KEY")
        self.n8n_auth_user = os.getenv("N8N_BASIC_AUTH_USER")
        self.n8n_auth_password = os.getenv("N8N_BASIC_AUTH_PASSWORD")
        
        logger.info(f"N8N Workflow execution base path: {self.workflows_base_path}")
        logger.info(f"N8N API URL: {n8n_api_url}")
        logger.info(f"N8N API Key configured: {'Yes' if self.n8n_api_key else 'No'}")
        logger.info(f"N8N Basic Auth configured: {'Yes' if self.n8n_auth_user else 'No'}")

    async def check_n8n_health(self) -> bool:
        """Vérifie si N8N est accessible."""
        try:
            headers = {}
            if self.n8n_api_key:
                headers["X-N8N-API-KEY"] = self.n8n_api_key
            
            auth = None
            if self.n8n_auth_user and self.n8n_auth_password:
                auth = aiohttp.BasicAuth(self.n8n_auth_user, self.n8n_auth_password)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.n8n_api_url}/workflows",
                    headers=headers,
                    auth=auth
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"N8N health check failed: {e}")
            return False

    async def install_workflow(self, folder_name: str) -> Dict[str, Any]:
        """
        Installe un workflow dans N8N depuis le dossier local.
        """
        workflow_path = os.path.join(self.workflows_base_path, folder_name)
        workflow_file = os.path.join(workflow_path, "workflow.json")
        meta_file = os.path.join(workflow_path, "workflow_meta.json")

        if not os.path.exists(workflow_file):
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

        # Charger le workflow et les métadonnées
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
            
        meta_data = {}
        if os.path.exists(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)

        # Préparer le workflow pour N8N
        workflow_payload = {
            "name": meta_data.get("name", folder_name),
            "nodes": workflow_data.get("nodes", []),
            "connections": workflow_data.get("connections", {}),
            "active": False,  # Commence inactif
            "settings": workflow_data.get("settings", {}),
            "tags": meta_data.get("tags", [])
        }

        # Installer dans N8N via API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.n8n_api_url}/workflows",
                    json=workflow_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Workflow installed successfully: {result['id']}")
                        return {
                            "success": True,
                            "workflow_id": result["id"],
                            "name": result["name"]
                        }
                    else:
                        error_msg = await response.text()
                        raise Exception(f"Failed to install workflow: {error_msg}")
        except Exception as e:
            logger.error(f"Error installing workflow '{folder_name}': {e}")
            raise

    async def execute_workflow(self, folder_name: str, inputs: Dict[str, Any], user_credentials: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Exécute un workflow N8N avec les inputs et credentials utilisateur.
        """
        workflow_path = os.path.join(self.workflows_base_path, folder_name)
        meta_file = os.path.join(workflow_path, "workflow_meta.json")

        # Charger les métadonnées pour récupérer l'ID du workflow
        if not os.path.exists(meta_file):
            raise FileNotFoundError(f"Workflow metadata not found: {meta_file}")

        with open(meta_file, 'r', encoding='utf-8') as f:
            meta_data = json.load(f)

        workflow_id = meta_data.get("n8n_workflow_id")
        if not workflow_id:
            # Installer le workflow s'il n'existe pas encore
            install_result = await self.install_workflow(folder_name)
            workflow_id = install_result["workflow_id"]
            
            # Mettre à jour les métadonnées
            meta_data["n8n_workflow_id"] = workflow_id
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=2)

        # Configurer les credentials si fournis
        if user_credentials:
            await self._configure_credentials(workflow_id, user_credentials)

        # Exécuter le workflow
        try:
            async with aiohttp.ClientSession() as session:
                execution_payload = {
                    "workflowData": {"id": workflow_id},
                    "startNodes": [],
                    "destinationNode": None,
                    **inputs
                }
                
                async with session.post(
                    f"{self.n8n_api_url}/workflows/{workflow_id}/execute",
                    json=execution_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Workflow executed successfully: {workflow_id}")
                        return {
                            "success": True,
                            "execution_id": result.get("executionId"),
                            "data": result.get("data", {})
                        }
                    else:
                        error_msg = await response.text()
                        raise Exception(f"Workflow execution failed: {error_msg}")
        except Exception as e:
            logger.error(f"Error executing workflow '{folder_name}': {e}")
            raise

    async def clone_workflow(self, template_path: str, user_id: str, credential_map: Dict[str, str]) -> Tuple[int, str]:
        """
        Clone un workflow template pour un utilisateur avec ses credentials.
        
        Args:
            template_path: Chemin vers le template JSON
            user_id: ID de l'utilisateur
            credential_map: Mapping des services vers IDs des credentials
            
        Returns:
            Tuple[workflow_id, webhook_url]
        """
        try:
            # Charger le template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Générer un ID unique pour ce workflow utilisateur
            workflow_id = str(uuid.uuid4())
            webhook_id = str(uuid.uuid4())
            
            # Cloner et personnaliser le template
            cloned_workflow = self._personalize_template(
                template_data, user_id, workflow_id, webhook_id, credential_map
            )
            
            # Créer le workflow via l'API N8N
            headers = {"Content-Type": "application/json"}
            
            # Ajouter l'authentification appropriée
            if self.n8n_api_key:
                headers["X-N8N-API-KEY"] = self.n8n_api_key
            
            auth = None
            if self.n8n_auth_user and self.n8n_auth_password:
                auth = aiohttp.BasicAuth(self.n8n_auth_user, self.n8n_auth_password)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.n8n_api_url}/workflows",
                    json=cloned_workflow,
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status not in [200, 201]:
                        error_msg = await response.text()
                        raise Exception(f"Failed to create workflow: {error_msg}")
                    
                    result = await response.json()
                    n8n_workflow_id = result["id"]
                    logger.info(f"Workflow created successfully with ID: {n8n_workflow_id}")
            
            # Activer le workflow (optionnel - on continue même si ça échoue)
            try:
                await self._activate_workflow(n8n_workflow_id)
                logger.info(f"Workflow {n8n_workflow_id} activated successfully")
            except Exception as activation_error:
                logger.warning(f"Failed to activate workflow {n8n_workflow_id}: {activation_error}")
                # On continue quand même car le workflow est créé
            
            # Construire l'URL du webhook
            webhook_url = f"{self.n8n_api_url.replace('/api/v1', '')}/webhook/gmail-to-drive-{workflow_id}"
            
            logger.info(f"Workflow cloned successfully: {n8n_workflow_id} for user {user_id}")
            return n8n_workflow_id, webhook_url
            
        except Exception as e:
            logger.error(f"Error cloning workflow: {e}")
            raise
    
    def _personalize_template(self, template: Dict[str, Any], user_id: str, workflow_id: str, 
                            webhook_id: str, credential_map: Dict[str, str]) -> Dict[str, Any]:
        """
        Personnalise un template avec les données utilisateur.
        """
        # Convertir le template en string pour faire les remplacements
        template_str = json.dumps(template)
        
        # Remplacer les placeholders
        template_str = template_str.replace("{{WORKFLOW_ID}}", workflow_id)
        template_str = template_str.replace("{{WEBHOOK_ID}}", webhook_id)
        template_str = template_str.replace("{{USER_ID}}", user_id)
        
        # Remplacer les credentials
        for service, cred_id in credential_map.items():
            if service == "gmail":
                template_str = template_str.replace("{{CREDENTIAL_ID_GMAIL}}", str(cred_id))
            elif service == "google_drive":
                template_str = template_str.replace("{{CREDENTIAL_ID_GOOGLE_DRIVE}}", str(cred_id))
        
        # Reconvertir en dict
        personalized = json.loads(template_str)
        
        # Ajouter un nom unique
        personalized["name"] = f"{template['name']} - User {user_id}"
        
        # Supprimer les champs en lecture seule que N8N assigne automatiquement
        read_only_fields = ["id", "active", "createdAt", "updatedAt"]
        for field in read_only_fields:
            if field in personalized:
                del personalized[field]
        
        return personalized
    
    async def _activate_workflow(self, workflow_id: int) -> None:
        """
        Active un workflow.
        """
        try:
            headers = {"Content-Type": "application/json"}
            
            # Ajouter l'authentification appropriée
            if self.n8n_api_key:
                headers["X-N8N-API-KEY"] = self.n8n_api_key
            
            auth = None
            if self.n8n_auth_user and self.n8n_auth_password:
                auth = aiohttp.BasicAuth(self.n8n_auth_user, self.n8n_auth_password)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.n8n_api_url}/workflows/{workflow_id}/activate",
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status not in [200, 204]:
                        error_msg = await response.text()
                        raise Exception(f"Failed to activate workflow: {error_msg}")
                    
                    logger.info(f"Workflow {workflow_id} activated successfully")
        except Exception as e:
            logger.error(f"Error activating workflow {workflow_id}: {e}")
            raise

    async def execute_workflow_by_id(self, workflow_id: int) -> Dict[str, Any]:
        """
        Exécute un workflow par son ID.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.n8n_api_url}/workflows/{workflow_id}/execute",
                    json={"data": {}},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Workflow {workflow_id} executed successfully")
                        return {
                            "success": True,
                            "execution_id": result.get("executionId"),
                            "data": result.get("data", {})
                        }
                    else:
                        error_msg = await response.text()
                        raise Exception(f"Workflow execution failed: {error_msg}")
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            raise

    async def toggle_workflow(self, workflow_id: int, active: bool) -> None:
        """
        Active ou désactive un workflow.
        """
        try:
            action = "activate" if active else "deactivate"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.n8n_api_url}/workflows/{workflow_id}/{action}",
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status not in [200, 204]:
                        error_msg = await response.text()
                        raise Exception(f"Failed to {action} workflow: {error_msg}")
                    
                    logger.info(f"Workflow {workflow_id} {action}d successfully")
        except Exception as e:
            logger.error(f"Error toggling workflow {workflow_id}: {e}")
            raise
    
    async def delete_workflow(self, workflow_id: int) -> None:
        """
        Supprime un workflow dans N8N.
        """
        try:
            headers = {}
            if self.n8n_api_key:
                headers["X-N8N-API-KEY"] = self.n8n_api_key
            
            auth = None
            if self.n8n_auth_user and self.n8n_auth_password:
                auth = aiohttp.BasicAuth(self.n8n_auth_user, self.n8n_auth_password)
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.n8n_api_url}/workflows/{workflow_id}",
                    headers=headers,
                    auth=auth
                ) as response:
                    if response.status not in [200, 204]:
                        error_msg = await response.text()
                        raise Exception(f"Failed to delete workflow: {error_msg}")
                    
                    logger.info(f"Workflow {workflow_id} deleted successfully from N8N")
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise

    async def _configure_credentials(self, workflow_id: str, user_credentials: Dict[str, Any]):
        """
        Configure les credentials pour un workflow spécifique.
        """
        # Cette fonction dépend de votre stratégie de gestion des credentials
        # Peut utiliser l'API N8N credentials ou des variables d'environnement
        pass

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'un workflow.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.n8n_api_url}/workflows/{workflow_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Failed to get workflow status: {response.status}")
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            raise

class N8NDiscoveryService:
    """
    Service pour découvrir et synchroniser les workflows N8N.
    """
    def __init__(self, workflows_root_dir: str = "static/workflows"):
        self.workflows_base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", workflows_root_dir
        )
        self.workflows_base_path = os.path.normpath(self.workflows_base_path)

    def discover_workflows(self) -> List[Dict[str, Any]]:
        """
        Scanne et découvre les workflows N8N disponibles.
        """
        discovered_workflows = []
        if not os.path.exists(self.workflows_base_path):
            logger.warning(f"Workflows path does not exist: {self.workflows_base_path}")
            return []

        for folder_name in os.listdir(self.workflows_base_path):
            workflow_folder_path = os.path.join(self.workflows_base_path, folder_name)
            if os.path.isdir(workflow_folder_path) and not folder_name.startswith('__'):
                workflow_file = os.path.join(workflow_folder_path, "workflow.json")
                meta_file = os.path.join(workflow_folder_path, "workflow_meta.json")
                
                if os.path.exists(workflow_file):
                    try:
                        # Charger les métadonnées
                        meta = {"name": folder_name, "description": "", "category": "automation"}
                        if os.path.exists(meta_file):
                            with open(meta_file, 'r', encoding='utf-8') as f:
                                meta.update(json.load(f))
                        
                        # Analyser le workflow pour extraire des infos
                        with open(workflow_file, 'r', encoding='utf-8') as f:
                            workflow_data = json.load(f)
                            
                        meta.update({
                            "folder_name": folder_name,
                            "type": "n8n_workflow",
                            "node_count": len(workflow_data.get("nodes", [])),
                            "integrations": self._extract_integrations(workflow_data),
                            "is_active": True
                        })
                        
                        discovered_workflows.append(meta)
                        logger.info(f"Discovered N8N workflow: {meta['name']} (folder: {folder_name})")
                        
                    except Exception as e:
                        logger.error(f"Error processing workflow '{folder_name}': {e}")

        logger.info(f"Total N8N workflows discovered: {len(discovered_workflows)}")
        return discovered_workflows

    def _extract_integrations(self, workflow_data: Dict[str, Any]) -> List[str]:
        """
        Extrait les intégrations utilisées dans un workflow.
        """
        integrations = set()
        nodes = workflow_data.get("nodes", [])
        
        for node in nodes:
            node_type = node.get("type", "")
            if node_type and node_type != "n8n-nodes-base.start":
                # Mapper les types de nodes vers des noms d'intégrations
                integration = self._map_node_to_integration(node_type)
                if integration:
                    integrations.add(integration)
        
        return list(integrations)

    def _map_node_to_integration(self, node_type: str) -> Optional[str]:
        """
        Mappe un type de node N8N vers un nom d'intégration.
        """
        mapping = {
            "n8n-nodes-base.telegram": "Telegram",
            "n8n-nodes-base.gmail": "Gmail",
            "n8n-nodes-base.googleSheets": "Google Sheets",
            "n8n-nodes-base.slack": "Slack",
            "n8n-nodes-base.discord": "Discord",
            "n8n-nodes-base.webhook": "Webhook",
            "n8n-nodes-base.httpRequest": "HTTP Request",
            "n8n-nodes-base.openAi": "OpenAI",
            "n8n-nodes-base.airtable": "Airtable",
            # Ajoutez d'autres mappings selon vos besoins
        }
        return mapping.get(node_type)