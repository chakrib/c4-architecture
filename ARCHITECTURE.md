# C4 Enterprise Platform - Architecture Documentation

## Overview

Enterprise-grade platform for generating C4 architecture diagrams with intelligent learning capabilities. Built for organization-wide deployment with hundreds of users.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│  • Diagram generation UI                                    │
│  • Real-time validation feedback                            │
│  • Diagram history & management                             │
│  • User feedback collection                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
┌────────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend                            │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           API Layer (FastAPI)                        │  │
│  │  • Authentication & Authorization (JWT)              │  │
│  │  • Rate Limiting & Quota Management                  │  │
│  │  • Request Validation                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Service Layer                              │  │
│  │  • DiagramService: AI-powered generation             │  │
│  │  • ValidationService: Multi-stage validation         │  │
│  │  • FeedbackService: User feedback processing         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           ML/AI Layer                                │  │
│  │  • SemanticValidator: Embedding-based validation     │  │
│  │  • GapAnalyzer: Intelligent suggestions              │  │
│  │  • LearningSystem: Continuous improvement            │  │
│  │  • PatternRecognizer: Architecture pattern detection │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌────────▼────────┐
│  PostgreSQL    │       │   Redis Cache   │
│  + pgvector    │       │                 │
│                │       │  • Session data │
│  • Users       │       │  • Rate limits  │
│  • Diagrams    │       │  • ML cache     │
│  • Feedback    │       └─────────────────┘
│  • Patterns    │
│  • Embeddings  │
└────────────────┘

External Services:
┌─────────────────┐
│  Anthropic API  │
│  (Claude)       │
│  • Diagram gen  │
└─────────────────┘
```

## Key Components

### 1. Intelligent Validation System

**Multi-Stage Validation Pipeline:**

```python
Input Text
    ↓
┌─────────────────────────────────────┐
│ Stage 1: Basic Validation           │
│ • Length check                      │
│ • Content type detection            │
│ • Block non-technical content       │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Stage 2: Rule-Based Validation      │
│ • System identification             │
│ • Component detection               │
│ • Actor/user presence               │
│ • Relationship detection            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Stage 3: Semantic Validation (ML)   │
│ • Generate embeddings               │
│ • Compare with validated examples   │
│ • Calculate similarity scores       │
│ • Pattern recognition               │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Stage 4: Gap Analysis               │
│ • Identify missing information      │
│ • Generate actionable suggestions   │
│ • Provide similar examples          │
└──────────────┬──────────────────────┘
               ↓
         Validation Result
```

### 2. Learning System

**Continuous Improvement Loop:**

```
User Input → Validation → Generation → User Feedback
                                            ↓
                                    ┌───────────────┐
                                    │ Learning Loop │
                                    └───────┬───────┘
                                            ↓
                        ┌───────────────────────────────┐
                        │ 1. Store validated example    │
                        │ 2. Generate embedding         │
                        │ 3. Update pattern database    │
                        │ 4. Adjust confidence scores   │
                        │ 5. Trigger retraining (async) │
                        └───────────────────────────────┘
```

**Learning Mechanisms:**

1. **Embedding-Based Similarity**
   - Uses sentence-transformers (all-MiniLM-L6-v2)
   - Stores embeddings in pgvector for fast similarity search
   - Finds similar validated examples

2. **Pattern Recognition**
   - Identifies common architecture patterns
   - Learns keywords and characteristics
   - Suggests pattern-specific components

3. **Feedback Integration**
   - User approvals strengthen validation
   - Corrections update validation rules
   - Quality ratings improve generation

### 3. Gap Analysis Engine

**Intelligent Suggestion Generation:**

```python
Input: "Transfer files from S3 to SFTP"

Gap Analysis:
├─ Missing: Users/Actors
│  └─ Suggestion: "Who initiates the transfer? 
│                  (e.g., 'Users upload files' or 
│                  'Automated scheduler triggers')"
│
├─ Missing: Trigger mechanism
│  └─ Suggestion: "What triggers the transfer? 
│                  (event, schedule, manual?)"
│
└─ Pattern Recognized: file_transfer
   └─ Suggestions:
      • "Mention source storage details"
      • "Specify destination configuration"
      • "Describe transformation steps"
```

### 4. Security Architecture

**Authentication & Authorization:**

```
User Request
    ↓
┌─────────────────────┐
│ JWT Token           │
│ Validation          │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ User Lookup         │
│ (from database)     │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ Permission Check    │
│ • Team membership   │
│ • Quota limits      │
│ • Rate limits       │
└──────┬──────────────┘
       ↓
   Authorized Request
```

**Security Features:**

- JWT-based authentication
- Password hashing (bcrypt)
- API key stored server-side only
- Rate limiting per user/team
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)

### 5. Data Model

**Core Entities:**

```sql
users
├─ id, email, username, hashed_password
├─ team_id (FK → teams)
└─ is_active, is_superuser

teams
├─ id, name, description
└─ api_quota_per_month

diagrams
├─ id, title, description
├─ input_text, mermaid_code
├─ diagram_type, version
├─ user_id (FK → users)
└─ parent_id (FK → diagrams) [versioning]

validated_inputs
├─ id, input_text
├─ embedding (vector[384])  ← pgvector
├─ validation_score
├─ user_feedback, pattern_type
└─ user_id (FK → users)

user_feedback
├─ id, feedback_type
├─ diagram_id (FK → diagrams)
├─ feedback_text, quality_rating
└─ user_id (FK → users)

learned_patterns
├─ id, pattern_name
├─ keywords[], example_inputs[]
├─ confidence_score, usage_count
└─ last_updated

usage_logs
├─ id, user_id, team_id
├─ action, tokens_used, cost_estimate
└─ success, error_message
```

## ML/AI Components

### 1. Semantic Validator

**Technology:** sentence-transformers (all-MiniLM-L6-v2)

**Purpose:** 
- Generate 384-dimensional embeddings for text
- Find semantically similar validated examples
- Determine if input is likely valid based on similarity

**Process:**
```python
1. Encode input text → embedding vector
2. Query pgvector for similar embeddings
3. Calculate cosine similarity
4. Return top-k similar examples with scores
```

### 2. Gap Analyzer

**Purpose:**
- Identify missing information
- Generate context-aware suggestions
- Provide actionable guidance

**Analysis Categories:**
- Missing components (systems, services)
- Missing actors (users, roles)
- Missing relationships (interactions)
- Ambiguous terms (needs clarification)

### 3. Pattern Recognizer

**Learned Patterns:**
- file_transfer
- api_integration
- event_driven
- microservices
- data_pipeline

**Pattern Learning:**
- Extracts keywords from validated inputs
- Builds confidence scores based on usage
- Suggests pattern-specific components

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Login (get JWT)
- `GET /api/auth/me` - Get current user

### Diagrams
- `POST /api/diagrams/generate` - Generate diagram
- `GET /api/diagrams/` - List user's diagrams
- `GET /api/diagrams/{id}` - Get specific diagram
- `DELETE /api/diagrams/{id}` - Delete diagram

### Feedback & Learning
- `POST /api/feedback/` - Submit feedback
- `GET /api/feedback/stats` - Learning statistics

## Performance Considerations

### Caching Strategy

1. **Redis Cache:**
   - Session data
   - Rate limit counters
   - Frequently accessed patterns

2. **Database Indexes:**
   - User email, username
   - Diagram user_id, created_at
   - ValidatedInput embedding (pgvector index)

3. **Query Optimization:**
   - Pagination for list endpoints
   - Lazy loading relationships
   - Connection pooling

### Scalability

**Horizontal Scaling:**
- Stateless backend (can run multiple instances)
- Load balancer distributes requests
- Shared PostgreSQL and Redis

**Vertical Scaling:**
- Increase database resources for ML queries
- More Redis memory for caching
- Larger backend instances for AI calls

## Monitoring & Analytics

### Usage Tracking

```python
usage_logs table tracks:
- API calls per user/team
- Tokens consumed
- Cost estimates
- Success/failure rates
- Error messages
```

### Learning Metrics

```python
- Total validated inputs
- Valid vs invalid ratio
- Learned patterns count
- High-confidence patterns
- Learning rate over time
```

## Deployment Architecture

### Recommended Production Setup

```
┌─────────────────────────────────────────────┐
│           Load Balancer (ALB/NLB)           │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐           ┌────▼───┐
│Backend │           │Backend │
│Instance│           │Instance│
│  (ECS) │           │  (ECS) │
└───┬────┘           └────┬───┘
    │                     │
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌───────▼──────┐
│ PostgreSQL │    │ Redis Cluster│
│   (RDS)    │    │ (ElastiCache)│
└────────────┘    └──────────────┘
```

### Cost Optimization

1. **AI API Costs:**
   - Cache similar requests
   - Use cheaper models when possible
   - Implement request deduplication

2. **Database:**
   - Regular vacuum and analyze
   - Archive old diagrams
   - Optimize vector indexes

3. **Compute:**
   - Auto-scaling based on load
   - Spot instances for non-critical tasks
   - Serverless options (Lambda/Cloud Run)

## Future Enhancements

1. **Advanced ML:**
   - Fine-tuned models for validation
   - Custom diagram generation models
   - Automated diagram improvement

2. **Collaboration:**
   - Real-time collaborative editing
   - Diagram comments and reviews
   - Team templates and standards

3. **Integration:**
   - Export to Confluence, Notion
   - Git integration for versioning
   - CI/CD pipeline integration

4. **Analytics:**
   - Diagram quality trends
   - Team usage patterns
   - Cost optimization insights
