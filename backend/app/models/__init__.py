# backend/app/models/__init__.py
"""
Configuration des modèles SQLAlchemy
Importe tous les modèles pour assurer leur enregistrement
"""

# Importer tous les modèles dans l'ordre de dépendance
from .user import User
from .crew import Crew
from .team_instance import TeamInstance

# Exporter tous les modèles
__all__ = ["User", "Crew", "TeamInstance"]