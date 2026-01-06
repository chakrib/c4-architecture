# Start the Hybrid C4 Diagram Generator

This guide shows you how to run the hybrid architecture with Python backend and React frontend.

## Architecture

```
┌─────────────────────┐
│  React Frontend     │  Port 5173
│  (JavaScript)       │
└──────────┬──────────┘
           │ HTTP API
           ▼
┌─────────────────────┐
│  Python Backend     │  Port 8000
│  (FastAPI)          │
│  - Validation       │
│  - Claude API       │
└─────────────────────┘
```

## Quick Start

### Terminal 1: Start Python Backend

```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the server
./venv/bin/python app/main.py
```

Backend will be available at: **http://localhost:8000**

### Terminal 2: Start React Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run the dev server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## Verify It's Working

1. Open http://localhost:5173 in your browser
2. Enter: "Build a web app with dashboard from WhatsApp and Google Docs"
3. Click "Generate Diagram"
4. You should see a C4 diagram!

## What Changed?

### Before (Pure Frontend):
- Frontend called Anthropic API directly
- Validation in JavaScript
- API key exposed in browser

### Now (Hybrid):
- Frontend calls Python backend
- Validation in Python (smarter, more maintainable)
- API key secure on server
- Ready to add ML/learning features later

## Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Make sure you're in the virtual environment
which python  # Should show path to venv
```

### Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### API key error
```bash
# Make sure .env file exists in backend/
cat backend/.env

# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

## Next Steps

Now that the hybrid architecture is working, you can:

1. ✅ Test diagram generation with various inputs
2. ✅ Validate that gibberish is rejected
3. ✅ Validate that natural descriptions work
4. 🔜 Add more sophisticated validation logic in Python
5. 🔜 Add ML-based validation later
6. 🔜 Add database for storing diagrams (when ready)
7. 🔜 Add authentication (when ready)

## Stop the Servers

**Backend**: Press `Ctrl+C` in Terminal 1
**Frontend**: Press `Ctrl+C` in Terminal 2
