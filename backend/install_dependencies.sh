#!/bin/bash

echo "🚀 Installation des dépendances par étapes..."

# Nettoyage du cache pip
echo "🧹 Nettoyage du cache pip..."
pip cache purge

# Mise à jour de pip
echo "⬆️ Mise à jour de pip..."
python -m pip install --upgrade pip

# Installation des dépendances FastAPI d'abord
echo "📦 Installation des dépendances FastAPI..."
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23
pip install aiosqlite==0.19.0
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]
pip install python-multipart==0.0.6
pip install pydantic==2.5.0
pip install email-validator==2.1.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0

# Installation de CrewAI avec une approche spécifique
echo "🤖 Installation de CrewAI et ses dépendances..."

# D'abord les dépendances langchain
pip install langchain-core==0.1.52
pip install langchain-community==0.0.38
pip install langchain==0.1.17

# Puis CrewAI avec --no-deps pour éviter les conflits
pip install --no-deps crewai==0.28.8

# Puis les outils CrewAI
pip install crewai-tools==0.1.0
pip install langchain-huggingface==0.0.3

# Installation des dépendances manquantes de CrewAI
pip install openai
pip install tiktoken
pip install instructor
pip install jsonref
pip install chromadb

echo "✅ Installation terminée!"
echo "🔍 Vérification de l'installation de CrewAI..."
python -c "import crewai; print('✅ CrewAI importé avec succès!')"