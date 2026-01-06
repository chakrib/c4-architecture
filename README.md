# C4 Enterprise Diagram Platform

Enterprise-grade C4 architecture diagram generation platform with intelligent learning capabilities.

## Architecture

```
c4-enterprise-platform/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── ml/          # Machine learning components
│   ├── tests/
│   └── requirements.txt
│
├── frontend/            # React frontend (migrated from c4-diagram-generator)
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── pages/
│   └── package.json
│
└── infrastructure/      # Deployment configs
    ├── docker/
    └── kubernetes/
```

## Features

### Core Capabilities
- ✅ Secure API key management (server-side only)
- ✅ User authentication & authorization
- ✅ Rate limiting & usage tracking
- ✅ Diagram generation with Claude AI
- ✅ Diagram storage & version history

### Intelligent Learning System
- 🧠 Semantic validation using ML embeddings
- 🧠 Feedback-based learning
- 🧠 Gap analysis with actionable suggestions
- 🧠 Pattern recognition & auto-completion
- 🧠 Continuous improvement from user interactions

### Enterprise Features
- 🏢 Multi-tenant support (teams/departments)
- 🏢 SSO/SAML integration
- 🏢 Usage analytics & reporting
- 🏢 Cost tracking per team
- 🏢 Audit logging

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with pgvector
- **Cache**: Redis
- **ML**: sentence-transformers, scikit-learn
- **AI**: Anthropic Claude API

### Frontend
- **Framework**: React 18 + Vite
- **UI**: Modern component library
- **Diagrams**: Mermaid.js
- **State**: React Query for server state

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Kubernetes (optional)
- **Cloud**: AWS/GCP/Azure compatible

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/c4platform
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=your_key_here
SECRET_KEY=your_secret_key
```

## API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Development Roadmap

- [x] Project structure
- [ ] Backend API implementation
- [ ] ML learning system
- [ ] Frontend migration
- [ ] Authentication system
- [ ] Deployment configuration
# c4-architecture
