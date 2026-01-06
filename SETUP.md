# C4 Enterprise Platform - Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional, for containerized setup)

## Quick Start with Docker (Recommended)

### 1. Clone and Configure

```bash
cd c4-enterprise-platform

# Create environment file
cp backend/.env.example backend/.env

# Edit backend/.env and add your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### 3. Initialize Database

```bash
# Run database initialization
docker-compose exec backend python init_db.py
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Login**: username=`admin`, password=`admin123` (change this!)

## Manual Setup (Without Docker)

### 1. Install PostgreSQL with pgvector

```bash
# macOS
brew install postgresql@16
brew install pgvector

# Start PostgreSQL
brew services start postgresql@16

# Create database
createdb c4platform

# Enable pgvector extension
psql c4platform -c "CREATE EXTENSION vector;"
```

### 2. Install Redis

```bash
# macOS
brew install redis
brew services start redis
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python init_db.py

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173

## Configuration

### Backend Environment Variables

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/c4platform

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Service
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Security (generate a secure key!)
SECRET_KEY=your-secret-key-min-32-chars-long

# Application
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# ML Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.75

# Feature Flags
ENABLE_LEARNING=True
ENABLE_FEEDBACK=True
ENABLE_ANALYTICS=True
```

### Generate Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Testing the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

Save the `access_token` from the response.

### 3. Generate a Diagram

```bash
curl -X POST "http://localhost:8000/api/diagrams/generate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a file transfer system that monitors S3 for new files and automatically transfers them to an on-premises SFTP server. Users upload files through a web interface.",
    "diagram_type": "context",
    "save_diagram": true,
    "title": "S3 to SFTP Transfer System"
  }'
```

## Database Management

### View Tables

```bash
psql c4platform

\dt  # List tables
SELECT * FROM users;
SELECT * FROM diagrams;
SELECT * FROM validated_inputs;
```

### Reset Database

```bash
# Drop and recreate
dropdb c4platform
createdb c4platform
psql c4platform -c "CREATE EXTENSION vector;"

# Reinitialize
python backend/init_db.py
```

## Troubleshooting

### pgvector Extension Not Found

```bash
# Install pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

# Enable in database
psql c4platform -c "CREATE EXTENSION vector;"
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Kill the process
kill -9 <PID>
```

### Python Dependencies Issues

```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Docker Issues

```bash
# Clean up and restart
docker-compose down -v
docker-compose up --build
```

## Production Deployment

### Security Checklist

- [ ] Change default admin password
- [ ] Generate secure SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_ORIGINS
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging

### Recommended Stack

- **Backend**: AWS ECS Fargate / GCP Cloud Run / Azure Container Apps
- **Database**: AWS RDS PostgreSQL / GCP Cloud SQL / Azure Database
- **Cache**: AWS ElastiCache / GCP Memorystore / Azure Cache for Redis
- **Frontend**: Vercel / Netlify / AWS S3 + CloudFront

## Next Steps

1. ✅ Complete setup
2. 📝 Test diagram generation
3. 🧠 Submit feedback to train the system
4. 👥 Add team members
5. 📊 Monitor usage analytics
6. 🚀 Deploy to production

## Support

For issues or questions:
- Check API docs: http://localhost:8000/docs
- Review logs: `docker-compose logs -f`
- Database queries: `psql c4platform`
