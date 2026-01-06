# Enhanced Validation System

## Overview

The C4 diagram generator now has intelligent validation that ensures inputs contain sufficient information for generating meaningful C4 Level 1 (Context) diagrams.

## Validation Rules

### 1. Minimum Word Count: 15 Words
**Rationale**: C4 Context diagrams require describing a system, its users, and what it does. This needs at least a sentence or two.

**Example Rejection**:
```
Input: "Build a web app for users"
Error: "Input too short (7 words). Need at least 15 words for meaningful C4 diagram."
```

### 2. Gibberish Detection
**Rationale**: Random characters or meaningless text cannot produce valid diagrams.

**How it works**: Counts meaningful technical/business terms. Needs at least 3 terms from:
- Actions: build, create, develop, make, design, implement
- Systems: system, application, app, service, platform, tool, software
- Users: user, customer, admin, client, employee, staff
- Tech terms: data, database, server, cloud, storage, api, authentication
- Business terms: business, workflow, process, report, analytics
- Integration: integrate, connect, sync, transfer, import, export

**Example Rejection**:
```
Input: "asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv"
Error: "Input appears to be gibberish or lacks technical/business context"
```

### 3. C4 Level 1 Requirements

A C4 Context diagram requires:

#### Required: THE SYSTEM
Must identify what system/application is being built.

**Indicators**: build, create, develop, system, application, app, service, platform, web, mobile, api, dashboard

**Example Rejection**:
```
Input: "there are many people who want to do things every day"
Error: "Cannot identify what system/application you want to build"
Question: "What type of system are you building? (e.g., web app, mobile app, API service)"
```

#### Required: USERS/ACTORS
Must identify who will use the system.

**Indicators**: user, customer, admin, client, employee, staff, developer, manager

**Example Question**:
```
Input: "Build a web application that processes data from multiple sources and generates reports..."
Error: "Insufficient information for C4 Context diagram"
Question: "Who will use this system? (e.g., customers, employees, administrators)"
```

#### Recommended: FUNCTIONALITY
Should describe what the system does.

**Indicators**: upload, download, store, process, manage, track, send, receive, display, create, update, search

**Example Warning**:
```
Warning: "No clear functionality described"
Question: "What will users do with this system? What are the main features?"
```

#### Optional: EXTERNAL SYSTEMS
Helpful to mention integrations.

**Indicators**: integrate, connect, api, database, storage, s3, aws, google, stripe, email

**Example Warning**:
```
Warning: "No external systems or integrations mentioned"
Suggestion: "Consider mentioning: databases, cloud storage, third-party APIs, or external services"
```

## Question-Asking Flow

When validation fails due to missing information (not gibberish), the system:

1. **Identifies what's missing** (users, functionality, etc.)
2. **Asks specific questions** to guide the user
3. **Provides suggestions** on what to add
4. **Returns helpful error messages** instead of just rejecting

### Example Flow

**User Input**:
```
Build a web application that processes data from multiple sources, stores it in a database, and generates reports. The system integrates with external APIs for data collection.
```

**System Response**:
```
❌ Insufficient information for C4 Context diagram

❓ Please provide more information:
1. Who will use this system? (e.g., customers, employees, administrators)

💡 Suggestions:
• Add information about who will interact with the system
```

**User Revised Input**:
```
Build a web application where business analysts can process data from multiple sources, store it in a database, and generate reports. The system integrates with external APIs for data collection.
```

**System Response**: ✅ Generates diagram

## Error Message Format

### Frontend Display
```
❌ Errors (red text)
❓ Questions (numbered list)
💡 Suggestions (helpful tips)
```

### API Response
```json
{
  "detail": {
    "message": "Validation failed",
    "errors": [
      "Insufficient information for C4 Context diagram"
    ],
    "questions": [
      "Who will use this system? (e.g., customers, employees, administrators)",
      "What will users do with this system? What are the main features?"
    ],
    "suggestions": [
      "Add information about who will interact with the system",
      "Describe what users can do with the system"
    ]
  }
}
```

## Benefits

1. **Prevents Gibberish**: No more random text generating meaningless diagrams
2. **Ensures Quality**: Diagrams have all necessary C4 Level 1 elements
3. **Guides Users**: Questions help users provide complete information
4. **Educational**: Users learn what makes a good C4 Context diagram
5. **Saves Time**: Catches issues before calling expensive AI API

## Testing

See `VALIDATION-TESTS.md` for comprehensive test cases covering:
- Valid inputs (complete descriptions)
- Invalid inputs (too short, gibberish, no system)
- Incomplete inputs (missing users, functionality)
- Edge cases

## Implementation

- **Backend**: `backend/app/main.py` - `validate_input()` function
- **Frontend**: `frontend/src/services/AIService.js` - Error formatting with questions
- **API**: Returns `questions` array in validation response

## Future Enhancements

Potential improvements:
1. **NLP-based validation** - Use ML to better understand intent
2. **Context extraction** - Automatically extract system, users, external systems
3. **Interactive refinement** - Multi-turn conversation to gather complete info
4. **Template suggestions** - Offer templates based on detected system type
5. **Learning from feedback** - Improve validation based on user corrections
