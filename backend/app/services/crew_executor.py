import os
import importlib.util
import logging
import subprocess
import sys
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

# Adjust import paths for your models and crud if needed
from app.models.crew import Crew
from app.schemas.crew import CrewCreate

logger = logging.getLogger(__name__)

class CrewExecutorService:
    """
    Service pour exécuter dynamiquement les équipes CrewAI.
    """
    def __init__(self, crews_root_dir: str = "static/crews"):
        # Chemin vers le dossier static/crews depuis app/
        self.crews_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", crews_root_dir)
        # Normalisation du chemin pour éviter les problèmes
        self.crews_base_path = os.path.normpath(self.crews_base_path)
        logger.info(f"Crew execution base path: {self.crews_base_path}")

    def _install_crew_dependencies(self, crew_folder_path: str) -> bool:
        """
        Installe les dépendances spécifiques d'un crew depuis son requirements.txt
        """
        requirements_file = os.path.join(crew_folder_path, "requirements.txt")
        if not os.path.exists(requirements_file):
            logger.warning(f"No requirements.txt found for crew at {crew_folder_path}")
            return True
            
        try:
            logger.info(f"Installing dependencies from {requirements_file}")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False

    async def execute_crew(self, folder_name: str, inputs: Dict[str, Any]) -> Any:
        """
        Exécute une équipe CrewAI spécifique.

        Args:
            folder_name: Le nom du dossier de l'équipe (ex: "divert_marketing_pitch").
            inputs: Un dictionnaire d'inputs pour le crew (ex: {"topic": "AI in healthcare"}).

        Returns:
            Le résultat de l'exécution du CrewAI.

        Raises:
            FileNotFoundError: Si le dossier de l'équipe ou le module principal n'est pas trouvé.
            AttributeError: Si la fonction d'exécution du crew n'est pas trouvée.
            Exception: Pour toute autre erreur lors de l'exécution du crew.
        """
        crew_path = os.path.join(self.crews_base_path, folder_name)
        main_crew_module_name = f"{folder_name}_main"
        main_crew_file = os.path.join(crew_path, f"{main_crew_module_name}.py")

        if not os.path.exists(crew_path):
            logger.error(f"Crew folder not found: {crew_path}")
            raise FileNotFoundError(f"Crew folder '{folder_name}' not found.")
        if not os.path.exists(main_crew_file):
            logger.error(f"Main crew file not found: {main_crew_file}")
            raise FileNotFoundError(f"Main crew file '{main_crew_module_name}.py' not found in '{folder_name}'.")

        # Installer les dépendances du crew si nécessaire
        if not self._install_crew_dependencies(crew_path):
            raise Exception(f"Failed to install dependencies for crew '{folder_name}'")

        try:
            # Dynamically load the module
            spec = importlib.util.spec_from_file_location(main_crew_module_name, main_crew_file)
            if spec is None:
                raise ImportError(f"Could not load spec for module {main_crew_module_name}")
            
            crew_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(crew_module)

            # Assuming the crew's main execution function is named 'run_crew'
            if not hasattr(crew_module, 'run_crew'):
                raise AttributeError(f"Function 'run_crew' not found in {main_crew_module_name}.py")

            run_crew_function = getattr(crew_module, 'run_crew')

            # Execute the crew
            crew_result = run_crew_function(**inputs)

            logger.info(f"Successfully executed crew: {folder_name}")
            return crew_result

        except Exception as e:
            logger.error(f"Error executing crew '{folder_name}': {e}", exc_info=True)
            raise Exception(f"Failed to execute crew '{folder_name}': {e}")


# ... (le reste de la classe CrewDiscoveryService reste identique)
class CrewDiscoveryService:
    """
    Service pour découvrir et synchroniser les équipes CrewAI depuis le système de fichiers
    avec la base de données.
    """
    def __init__(self, crews_root_dir: str = "static/crews"):
        # Chemin vers le dossier static/crews depuis app/
        self.crews_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", crews_root_dir)
        # Normalisation du chemin pour éviter les problèmes
        self.crews_base_path = os.path.normpath(self.crews_base_path)
        logger.info(f"Crew discovery base path: {self.crews_base_path}")

    def discover_crews(self) -> List[Dict[str, Any]]:
        """
        Scanne le répertoire des crews et collecte les métadonnées.
        """
        discovered_crews = []
        if not os.path.exists(self.crews_base_path):
            logger.warning(f"Crew discovery path does not exist: {self.crews_base_path}")
            return []

        for folder_name in os.listdir(self.crews_base_path):
            crew_folder_path = os.path.join(self.crews_base_path, folder_name)
            if os.path.isdir(crew_folder_path) and not folder_name.startswith('__'):
                meta_file_path = os.path.join(crew_folder_path, "crew_meta.json")
                if os.path.exists(meta_file_path):
                    try:
                        import json
                        with open(meta_file_path, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                            if "name" in meta and "description" in meta and "category" in meta:
                                meta["folder_name"] = folder_name
                                if "is_active" not in meta:
                                    meta["is_active"] = True
                                discovered_crews.append(meta)
                                logger.info(f"Discovered crew: {meta['name']} (folder: {folder_name})")
                            else:
                                logger.warning(f"Skipping crew in '{folder_name}': crew_meta.json missing required fields.")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error decoding JSON in {meta_file_path}: {e}")
                    except Exception as e:
                        logger.error(f"Error reading meta file for '{folder_name}': {e}")
                else:
                    logger.warning(f"Skipping crew in '{folder_name}': crew_meta.json not found.")
        
        logger.info(f"Total crews discovered: {len(discovered_crews)}")
        return discovered_crews

    def sync_crews_with_database(self, db: Session) -> Dict[str, int]:
        """
        Synchronise les crews découverts avec la base de données.
        """
        from app.crud.crew import create_crew
        
        discovered_crews = self.discover_crews()
        added_count = 0
        updated_count = 0
        
        for crew_data in discovered_crews:
            existing_crew = db.query(Crew).filter(Crew.folder_name == crew_data["folder_name"]).first()
            
            if existing_crew:
                changed = False
                if existing_crew.name != crew_data["name"]:
                    existing_crew.name = crew_data["name"]
                    changed = True
                if existing_crew.description != crew_data["description"]:
                    existing_crew.description = crew_data["description"]
                    changed = True
                if existing_crew.category != crew_data["category"]:
                    existing_crew.category = crew_data["category"]
                    changed = True
                if not existing_crew.is_active:
                    existing_crew.is_active = True
                    changed = True

                if changed:
                    db.commit()
                    db.refresh(existing_crew)
                    updated_count += 1
                    logger.info(f"Updated crew: {existing_crew.name}")
            else:
                try:
                    new_crew = CrewCreate(**crew_data)
                    created_crew = create_crew(db, new_crew)
                    added_count += 1
                    logger.info(f"Added new crew: {created_crew.name}")
                except Exception as e:
                    logger.error(f"Error creating crew {crew_data['name']}: {e}")
        
        # Deactivate crews not found on filesystem
        db_crews = db.query(Crew).all()
        discovered_folder_names = {c["folder_name"] for c in discovered_crews}
        
        for db_crew in db_crews:
            if db_crew.folder_name not in discovered_folder_names and db_crew.is_active:
                db_crew.is_active = False
                db.commit()
                db.refresh(db_crew)
                updated_count += 1
                logger.info(f"Deactivated crew: {db_crew.name}")

        return {"added": added_count, "updated": updated_count, "total": len(discovered_crews)}