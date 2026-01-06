# C4 Diagram Generator

AI-powered C4 architecture diagram generator using Django Ninja backend and React frontend.

## Features

- ✅ **Intelligent Validation**: Validates input for C4 diagram requirements
- ✅ **AI-Powered Generation**: Uses Anthropic Claude to generate Mermaid diagrams
- ✅ **Smart Suggestions**: Provides AI-generated alternatives for incomplete inputs
- ✅ **Diagram Refinement**: Modify diagrams with natural language instructions
- ✅ **Version History**: Undo/redo diagram changes
- ✅ **Export**: Download Mermaid code

## Tech Stack

**Backend:**
- Django 5.0.1
- Django Ninja 1.1.0 (FastAPI-style API framework)
- Anthropic Claude API (claude-3-haiku-20240307)
- Python 3.10+

**Frontend:**
- React 18
- Vite
- Mermaid.js for diagram rendering

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd c4-enterprise-platform
   ```

2. **Configure API Key**
   
   Edit `backend-django/.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   ```

3. **Start the Application**
   ```bash
   ./start.sh
   ```

   This will:
   - Install backend dependencies (if needed)
   - Install frontend dependencies (if needed)
   - Start Django backend on http://localhost:8001
   - Start React frontend on http://localhost:5173

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8001/api
   - API Documentation: http://localhost:8001/api/docs

## Usage

### Generate a Diagram

1. Enter a system description in the text area
2. Click "Generate Diagram"
3. View the generated C4 diagram

**Example Input:**
```
Build a web application where users can upload documents to Amazon S3, 
store metadata in PostgreSQL database, and send email notifications via 
SendGrid API when uploads complete. Administrators can view all uploads 
through an admin dashboard.
```

### Get AI Suggestions

If your input is incomplete, the system will automatically offer AI-generated suggestions with complete descriptions.

### Refine Diagrams

After generating a diagram, use the refinement section to modify it:
- "Remove the S3 bucket"
- "Add a Redis cache between the API and database"
- "Change the user label to 'External Customers'"

## Project Structure

```
c4-enterprise-platform/
├── backend-django/          # Django Ninja Backend
│   ├── c4platform/          # Django project settings
│   ├── diagrams/            # Main app (API, validation, AI service)
│   ├── venv/                # Python virtual environment
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                 # Environment variables (API key)
│   └── README.md
│
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   └── services/        # API service layer
│   ├── package.json
│   └── .env                 # Backend URL configuration
│
├── start.sh                 # Unified startup script
└── README.md                # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | API root |
| `/api/health` | GET | Health check |
| `/api/diagrams/validate` | POST | Validate input text |
| `/api/diagrams/generate` | POST | Generate C4 diagram |
| `/api/diagrams/suggest-improvements` | POST | Get AI suggestions |
| `/api/diagrams/refine` | POST | Refine existing diagram |
| `/api/docs` | GET | Interactive API documentation |

## Configuration

### Backend Configuration

`backend-django/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
SECRET_KEY=django-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Configuration

`frontend/.env`:
```env
VITE_BACKEND_URL=http://localhost:8001
```

## Development

### Backend Only

```bash
cd backend-django
source venv/bin/activate
python manage.py runserver 8001
```

### Frontend Only

```bash
cd frontend
npm run dev
```

### Run Tests

```bash
# Backend tests (when implemented)
cd backend-django
python manage.py test

# Frontend tests (when implemented)
cd frontend
npm test
```

## Validation Rules

The system validates input for C4 Level 1 (Context) diagrams:

1. **Minimum Length**: At least 15 words
2. **System Identification**: Must describe what system is being built
3. **Users/Actors**: Must identify who will use the system
4. **Functionality**: Should describe what the system does
5. **External Systems**: Should mention integrations (optional but recommended)

## Troubleshooting

### Port Already in Use

The `start.sh` script automatically kills processes on ports 8001 and 5173. If you still have issues:

```bash
# Kill backend
lsof -ti:8001 | xargs kill -9

# Kill frontend
lsof -ti:5173 | xargs kill -9
```

### Backend Won't Start

Check logs:
```bash
cat backend.log
```

Common issues:
- Missing Anthropic API key in `.env`
- Python dependencies not installed
- Wrong Python version (need 3.10+)

### Frontend Won't Start

Check logs:
```bash
cat frontend.log
```

Common issues:
- Node modules not installed
- Wrong backend URL in `frontend/.env`

### API Key Errors

Verify your Anthropic API key:
1. Check it exists in `backend-django/.env`
2. Verify it's valid at https://console.anthropic.com/
3. Ensure it has sufficient credits

## Production Deployment

### Backend

1. Set `DEBUG=False` in `.env`
2. Generate a strong `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Update `CORS_ALLOWED_ORIGINS` with your frontend URL
5. Use Gunicorn:

```bash
cd backend-django
gunicorn c4platform.wsgi:application --bind 0.0.0.0:8001 --workers 4
```

### Frontend

1. Update `VITE_BACKEND_URL` in `.env` to your production backend URL
2. Build for production:

```bash
cd frontend
npm run build
```

3. Serve the `dist/` folder with nginx or similar

## Architecture

```
┌─────────────────────────────────────────┐
│  React Frontend (Port 5173)             │
│  - User Interface                       │
│  - Diagram Visualization                │
│  - Input Forms                          │
└──────────────┬──────────────────────────┘
               │ HTTP Requests
               ▼
┌─────────────────────────────────────────┐
│  Django Ninja Backend (Port 8001)       │
│  - API Endpoints                        │
│  - Input Validation                     │
│  - Anthropic Integration                │
└──────────────┬──────────────────────────┘
               │ API Calls
               ▼
┌─────────────────────────────────────────┐
│  Anthropic Claude API                   │
│  - Diagram Generation                   │
│  - Suggestions                          │
│  - Refinements                          │
└─────────────────────────────────────────┘
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
