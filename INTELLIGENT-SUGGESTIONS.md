# Intelligent Suggestion System

## Overview

The C4 diagram generator now includes an **intelligent suggestion system** that uses Claude AI to help users transform incomplete or unclear descriptions into complete C4-ready descriptions.

## How It Works

### Flow Diagram

```
User enters description
    ↓
Validation checks
    ↓
❌ Incomplete/unclear?
    ↓
System automatically generates 3 suggestions using Claude
    ↓
User reviews options
    ↓
User selects one (or edits manually)
    ↓
✅ Generate diagram with approved version
```

## When Suggestions Are Offered

Suggestions are automatically generated when:
- ✅ Input has sufficient length (15+ words)
- ✅ Input is not gibberish (has meaningful terms)
- ❌ BUT missing required C4 elements (users, functionality, etc.)

Suggestions are NOT generated for:
- ❌ Too short input (< 15 words)
- ❌ Gibberish input
- ✅ Already valid input

## Example

### User Input (Incomplete)
```
Solution Overview: As part of AWS 2.0 account vending happens at the App Family 
level. Which means each App Family gets one set of SDLC accounts, with corresponding 
VPCs, and roles associated. These SDLC accounts are shared by multiple Application 
which fall into the App Family. Which also means, each application deployed is these 
accounts could potentially share the data. Data could be in databases, S3 buckets 
of file systems, Cache etc. At this time, only data sharing is the concern, not 
the network, or other resources.
```

**Issues Detected:**
- ❌ No clear system being built
- ❌ No users identified
- ❌ No functionality described

### System Response (3 Suggestions)

**Option 1: Data Isolation Enforcement System**
```
Implement a data isolation enforcement mechanism for AWS 2.0 where IAM policies 
and resource-based policies automatically deny unauthorized applications from 
accessing data in shared App Family SDLC accounts. Platform engineers configure 
application-specific IAM roles with explicit deny statements, and the system uses 
AWS IAM policy conditions, resource tags, and VPC endpoints to enforce that 
applications can only access their designated databases, S3 buckets, file systems, 
and caches. The mechanism integrates with AWS Organizations for policy inheritance, 
AWS Config for compliance monitoring, and CloudTrail for access denial logging.
```

**Option 2: Data Access Governance Platform**
```
Design a data access governance platform for AWS 2.0 account vending where compliance 
officers and application owners can track and audit data sharing across applications 
within App Family SDLC accounts. Users can view which applications access shared 
databases, S3 buckets, file systems, and caches, generate compliance reports, and 
set data access policies. The platform integrates with AWS IAM, CloudTrail, and 
AWS Organizations to provide visibility into data access patterns.
```

**Option 3: Multi-Tenant Data Isolation Service**
```
Create a multi-tenant data isolation service for AWS 2.0 where application teams 
can deploy applications to shared App Family SDLC accounts while maintaining data 
separation. The service automatically provisions isolated databases, S3 buckets, 
file systems, and cache instances for each application, manages IAM roles and 
policies to prevent cross-application data access, and integrates with AWS KMS 
for encryption key management.
```

### User Action
1. Reviews the 3 options
2. Selects the one that best matches their intent
3. System automatically generates diagram with selected version

## API Endpoints

### POST `/api/diagrams/suggest-improvements`

**Request:**
```json
{
  "input_text": "Your incomplete description...",
  "diagram_type": "context"
}
```

**Response (Success - 200):**
```json
{
  "original_text": "Your incomplete description...",
  "validation_issues": [
    "Insufficient information for C4 Context diagram",
    "Who will use this system?"
  ],
  "suggestions": [
    {
      "title": "Data Isolation Enforcement System",
      "description": "A system to prevent unauthorized data access",
      "improved_text": "Complete description with all C4 elements..."
    },
    {
      "title": "Data Access Governance Platform",
      "description": "A platform to track and audit data sharing",
      "improved_text": "Complete description with all C4 elements..."
    },
    {
      "title": "Multi-Tenant Data Isolation Service",
      "description": "A service to provision isolated resources",
      "improved_text": "Complete description with all C4 elements..."
    }
  ]
}
```

**Response (Error - 400):**
```json
{
  "detail": {
    "message": "Cannot generate suggestions for this input",
    "errors": ["Input too short (4 words). Need at least 15 words"],
    "suggestions": ["Please provide more details..."]
  }
}
```

## Frontend UI

### Suggestion Display

When suggestions are available, the UI shows:

```
┌─────────────────────────────────────────────────────────┐
│ 💡 Suggested Improvements                               │
│                                                          │
│ Based on your input, here are some interpretations:     │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Option 1: Data Isolation Enforcement System        │ │
│ │ A system to prevent unauthorized data access       │ │
│ │                                                     │ │
│ │ Implement a data isolation enforcement mechanism...│ │
│ │                                                     │ │
│ │ [Use This Version]                                 │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Option 2: Data Access Governance Platform          │ │
│ │ ...                                                 │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Option 3: Multi-Tenant Data Isolation Service      │ │
│ │ ...                                                 │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [Cancel - I'll Edit Manually]                           │
└─────────────────────────────────────────────────────────┘
```

### User Interactions

1. **Click on a suggestion card** - Selects that option
2. **Click "Use This Version"** - Confirms selection and generates diagram
3. **Click "Cancel"** - Dismisses suggestions, user can edit manually

## Implementation Details

### Backend (`backend/app/main.py`)

**New Function:**
```python
def generate_improvement_suggestions(original_text: str, validation_result: ValidationResult) -> list[SuggestionOption]
```

- Uses Claude (Haiku model) to analyze input
- Generates 3 diverse interpretations
- Each suggestion includes: title, description, improved_text
- Returns empty list if API call fails

**New Endpoint:**
```python
@app.post("/api/diagrams/suggest-improvements", response_model=SuggestionResponse)
async def suggest_improvements(request: DiagramRequest)
```

- Validates input first
- Rejects if already valid or if gibberish
- Calls `generate_improvement_suggestions()`
- Returns structured suggestions

### Frontend (`frontend/src/`)

**AIService.js:**
```javascript
async getSuggestions(context)
```

**DiagramGenerator.jsx:**
- New state: `suggestions`, `loadingSuggestions`
- New handlers: `handleGetSuggestions()`, `handleSelectSuggestion()`
- Auto-fetches suggestions when validation fails
- Displays suggestions in interactive cards
- Auto-generates diagram when user selects a suggestion

## Benefits

1. **Reduces Friction** - Users don't need to understand C4 requirements upfront
2. **Educational** - Users learn what makes a good C4 description by seeing examples
3. **Saves Time** - No back-and-forth asking questions
4. **Intelligent** - LLM understands context and generates relevant options
5. **Flexible** - Users can still edit manually if they prefer

## Testing

### Manual Test

1. Start backend: `cd backend && ./venv/bin/python app/main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Enter incomplete description (like the AWS example above)
4. Click "Generate Diagram"
5. System automatically shows suggestions
6. Select one and see diagram generated

### API Test

```bash
cd backend
chmod +x test_suggestions.py
./venv/bin/python test_suggestions.py
```

### cURL Test

```bash
curl -X POST http://localhost:8000/api/diagrams/suggest-improvements \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Solution Overview: As part of AWS 2.0 account vending...",
    "diagram_type": "context"
  }' | jq
```

## Configuration

No additional configuration needed! The system uses:
- Same Anthropic API key from `.env`
- Same Claude model (Haiku) for cost efficiency
- Automatic fallback if suggestion generation fails

## Future Enhancements

Potential improvements:
1. **User feedback loop** - Learn which suggestions users prefer
2. **Custom suggestion count** - Let users request more/fewer options
3. **Suggestion refinement** - Allow users to ask for variations
4. **Template library** - Pre-built suggestions for common patterns
5. **Multi-turn conversation** - Interactive refinement of suggestions

## Status

🟢 **COMPLETE** - Intelligent suggestion system is fully implemented and ready to use!
