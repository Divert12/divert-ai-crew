# 🚀 Divert.ai – Plateforme d'automatisation avec IA & Workflows

> **Automatise tes tâches avec des équipes d'agents IA (CrewAI) et des workflows visuels (n8n)**

---

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)  
![En cours](https://img.shields.io/badge/statut-en%20développement-orange.svg)

---

## 🧠 C’est quoi Divert.ai ?

Divert.ai est une application web tout-en-un qui te permet, via une interface simple et accessible à tous, d’ajouter des workflows automatisés ou des agents IA intelligents (CrewAI) à ton tableau de bord.
En quelques clics, tu peux bénéficier d’une automatisation instantanée ou lancer des tâches complexes sans aucune compétence technique.

L’objectif : automatiser des tâches complexes sans code.

---

## 🔑 Fonctionnalités principales

- 🤖 Ajouter ton équipe d’agents IA a Ton tableau de bord 
- ⚙️ Automatise des tâches avec des workflows 
- 🔐 Gère tes clés et connexions de manière sécurisée  
- 📊 Suis les exécutions en temps réel  
- 🔁 Clone des workflows et adapte-les à tes besoins

---

## 🧱 Stack utilisée

- **Backend** : FastAPI (Python), SQLite, CrewAI, n8n
- **Frontend** : React + Tailwind CSS
- **Sécurité** : JWT, chiffrement Fernet

---

## 📁 Structure du projet

divert-startup3/
├── backend/       # API FastAPI
├── frontend2/     # Interface React
└── README.md

````

---

## ⚙️ Installation rapide

### Prérequis

- Python 3.11+
- Node.js 18+
- Une instance de n8n (locale ou cloud)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
````

### Frontend

```bash
cd frontend2
npm install
npm start
```

### Exemple de `.env`

```env
DATABASE_URL=sqlite:///./divert_ai.db
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=ton-api-key
JWT_SECRET_KEY=ton-secret
```

---

## 👨‍💻 Ce que tu peux faire

### Agents IA

* Ajouter, gérer et exécuter des équipes d’agents intelligents

### Workflows

* Cloner des templates
* Lancer et arrêter des exécutions
* Suivre ce qui se passe étape par étape

### Interface

* Dashboard simple et clair
* Historique des exécutions
* Gestion sécurisée des credentials

---

## 🔐 Sécurité

* Authentification via JWT
* Credentials chiffrés
* API sécurisée et isolée par utilisateur

---

## 🛠 Endpoints utiles

```http
POST /auth/register            # Créer un compte
POST /auth/login               # Connexion utilisateur
GET  /workflows                # Voir les workflows dispo
POST /workflows/:id/execute    # Lancer un workflow
POST /templates/:name/clone    # Cloner un modèle
GET  /my-teams                 # Voir tes équipes
```

---

## 🧪 Statut actuel

Le projet est en développement.
On bosse sur l’UX, les intégrations IA, la sécurité et les déploiements.

---

## 🤝 Rejoins-nous

Tu veux contribuer ? On cherche :

* Des devs backend (FastAPI, CrewAI, n8n)
* Des devs frontend (React)
* Des curieux de l’IA et de l’automatisation
* Des gens à l’aise avec Docker et le déploiement

---

## 💡 Notre objectif

Rendre l’automatisation par l’IA accessible à tous, sans code, avec une interface simple et puissante.

---

## 📬 Contact

Besoin d’aide, envie de proposer une idée ou de contribuer ?
→ Ouvre une issue ou une PR sur GitHub.

---

**Fait avec ❤️ par des passionnés d’IA & d’automatisation**



