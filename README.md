# Divert.ai - AI Teams & Workflow Automation Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-in%20development-orange.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)

> **AI-powered automation platform combining CrewAI multi-agent teams with N8N workflow orchestration**

## 🚀 Project Overview

Divert.ai is a comprehensive SaaS platform that empowers users to create, manage, and execute AI-driven automation workflows. The platform seamlessly integrates **CrewAI** for multi-agent AI teams with **N8N** for visual workflow automation, providing a unified interface for complex business process automation.

### Key Features

- **🤖 AI Teams Management**: Create and orchestrate CrewAI multi-agent teams
- **⚡ Workflow Automation**: Visual workflow creation and execution via N8N integration
- **🔐 Secure Integrations**: Encrypted credential management for external services
- **👥 User-Centric Design**: Personal workflow cloning and team management
- **📊 Execution Tracking**: Comprehensive monitoring and analytics
- **🔄 Real-time Sync**: Automatic synchronization between services

## 🛠 Technology Stack

### Backend (Custom Implementation)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: JWT-based security
- **AI Integration**: CrewAI for multi-agent orchestration
- **Workflow Engine**: N8N REST API integration
- **Security**: Fernet encryption for credentials

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom component library
- **State Management**: React hooks and context
- **Note**: Landing page generated with Lovable using advanced prompts and configurations

### Infrastructure
- **API Documentation**: FastAPI automatic OpenAPI/Swagger
- **CORS**: Configured for local development
- **Environment**: Docker-ready configuration
- **Database**: SQLite with foreign key constraints

## 📁 Project Structure

```
divert-startup3/
├── backend/                 # Custom FastAPI backend
│   ├── app/
│   │   ├── routers/        # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── core/           # Security & config
│   │   └── database/       # Database configuration
│   └── requirements.txt
├── frontend2/              # React frontend
│   ├── src/
│   │   ├── pages/         # Application pages
│   │   ├── components/    # Reusable components
│   │   └── utils/         # Utility functions
│   └── package.json
└── README.md
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- N8N instance (local or cloud)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configure environment variables
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend2
npm install
npm start
```

### Environment Configuration
```env
DATABASE_URL=sqlite:///./divert_ai.db
CREDENTIAL_ENCRYPTION_KEY=your-encryption-key
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your-n8n-api-key
JWT_SECRET_KEY=your-jwt-secret
```

## 🎯 Core Functionality

### Workflow Management
- **Template Store**: Browse and clone pre-built workflow templates
- **Personal Cloning**: Create private copies of workflows with user-specific credentials
- **Execution Control**: Start, stop, and monitor workflow executions
- **Credential Security**: Encrypted storage of API keys and authentication tokens

### AI Teams (CrewAI)
- **Agent Orchestration**: Multi-agent team creation and management
- **Task Automation**: Complex business process automation
- **Team Instances**: Personal team configurations and execution tracking

### User Experience
- **Dashboard**: Centralized view of teams and workflows
- **My Teams**: Personal workspace for cloned workflows and AI teams
- **Integration Hub**: Manage external service connections
- **Execution History**: Track and analyze automation performance

## 🔐 Security Features

- JWT-based authentication system
- Fernet encryption for sensitive credentials
- User-isolated workflow instances
- Secure API key management
- CORS protection and input validation

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication

### Workflows
- `GET /workflows` - List available workflows
- `POST /workflows/{id}/execute` - Execute workflow
- `POST /templates/{name}/clone` - Clone workflow template

### Teams
- `GET /my-teams` - User's teams and workflows
- `DELETE /my-teams/{id}/delete-cloned-workflow` - Remove cloned workflow

### Integrations
- `GET /integrations` - Available integrations
- `POST /credentials/{service}` - Store service credentials

## 🚀 Development Status

**Current Phase**: Active Development

This project is actively being developed as a comprehensive automation platform. We welcome collaboration from developers interested in:

- AI/ML integration and optimization
- Workflow automation and orchestration
- Frontend/backend scalability improvements
- Security enhancements and testing
- DevOps and deployment strategies

## 🤝 Contributing

We're seeking talented developers and collaborators to help build the future of AI-powered automation. Whether you're interested in:

- **Backend Development**: API design, database optimization, service integration
- **Frontend Engineering**: React components, user experience, responsive design
- **AI/ML Engineering**: CrewAI optimization, agent design, workflow intelligence
- **DevOps**: Deployment, scaling, monitoring, and infrastructure

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request with detailed description

## 🎯 Business Vision

Divert.ai aims to democratize AI-powered automation by providing an intuitive platform where users can:
- Create sophisticated AI agent teams without coding
- Automate complex business processes visually
- Integrate multiple services seamlessly
- Scale automation across organizations

## 📞 Contact & Collaboration

For partnership opportunities, technical discussions, or contribution inquiries, please reach out through:
- GitHub Issues for technical questions
- Pull Requests for code contributions
- Discussions for feature requests and ideas

---

**Built with ❤️ by developers passionate about AI automation**

*This project represents the intersection of cutting-edge AI technology and practical business automation, designed to empower users with tools that were previously only accessible to large enterprises.*
