# Validation Flow Diagram

## Input Processing Flow

```
┌─────────────────────────────────────┐
│   User enters description           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 1: Empty?                   │
│   ❌ Yes → Reject                   │
│   ✅ No → Continue                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 2: < 15 words?              │
│   ❌ Yes → Reject with suggestions  │
│   ✅ No → Continue                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 3: Gibberish?               │
│   (< 3 meaningful terms)            │
│   ❌ Yes → Reject with example      │
│   ✅ No → Continue                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 4: System identified?       │
│   ❌ No → Reject with question      │
│   ✅ Yes → Continue                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 5: Users identified?        │
│   ❌ No → Ask question              │
│   ✅ Yes → Continue                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 6: Functionality described? │
│   ❌ No → Ask question              │
│   ✅ Yes → Continue                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Check 7: External systems?        │
│   ❌ No → Warn (optional)           │
│   ✅ Yes → Continue                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Has questions?                    │
│   ❌ Yes → Return questions to user │
│   ✅ No → Generate diagram          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Call Claude API                   │
│   Generate Mermaid diagram          │
│   Return to user                    │
└─────────────────────────────────────┘
```

## Validation Levels

### 🔴 REJECT (Blocking Errors)
1. Empty input
2. Less than 15 words
3. Gibberish (< 3 meaningful terms)
4. No system identified

### 🟡 ASK QUESTIONS (Missing Required Info)
5. No users/actors identified
6. No functionality described

### 🟢 WARN (Missing Optional Info)
7. No external systems mentioned

## Example Flows

### Flow 1: Perfect Input ✅
```
Input: "Build a web application where users can upload files to Amazon S3 
       storage and transfer them to SFTP servers. Administrators can manage 
       user accounts and monitor file transfers through a dashboard."

Check 1: Not empty ✅
Check 2: 28 words ✅
Check 3: Many meaningful terms ✅
Check 4: System = "web application" ✅
Check 5: Users = "users", "administrators" ✅
Check 6: Functionality = "upload", "transfer", "manage", "monitor" ✅
Check 7: External = "Amazon S3", "SFTP servers" ✅

Result: ✅ Generate diagram
```

### Flow 2: Too Short ❌
```
Input: "Build a web app"

Check 1: Not empty ✅
Check 2: 4 words ❌

Result: ❌ Reject
Error: "Input too short (4 words). Need at least 15 words"
Suggestions: What to include (system, users, functionality, external systems)
```

### Flow 3: Gibberish ❌
```
Input: "asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv"

Check 1: Not empty ✅
Check 2: 6 words ❌ (but would fail next check anyway)
Check 3: 0 meaningful terms ❌

Result: ❌ Reject
Error: "Input appears to be gibberish or lacks technical/business context"
Example: Provided
```

### Flow 4: Missing Users ⚠️
```
Input: "Build a web application that processes data from multiple sources, 
       stores it in a database, and generates reports. The system integrates 
       with external APIs for data collection."

Check 1: Not empty ✅
Check 2: 25 words ✅
Check 3: Many meaningful terms ✅
Check 4: System = "web application" ✅
Check 5: Users = none found ❌
Check 6: Functionality = "processes", "stores", "generates" ✅
Check 7: External = "database", "external APIs" ✅

Result: ⚠️ Ask question
Question: "Who will use this system? (e.g., customers, employees, administrators)"
Suggestion: "Add information about who will interact with the system"
```

### Flow 5: Missing Functionality ⚠️
```
Input: "Build a mobile application for customers that connects to our backend 
       system and external payment services for processing transactions securely."

Check 1: Not empty ✅
Check 2: 19 words ✅
Check 3: Many meaningful terms ✅
Check 4: System = "mobile application" ✅
Check 5: Users = "customers" ✅
Check 6: Functionality = "processing" (weak) ❌
Check 7: External = "backend system", "payment services" ✅

Result: ⚠️ Ask question
Question: "What will users do with this system? What are the main features?"
Suggestion: "Describe what users can do with the system"
```

## Response Format

### Success Response
```json
{
  "mermaid_code": "graph LR\n  User[👤 User]...",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": ["No external systems mentioned"],
    "suggestions": ["Consider mentioning: databases, cloud storage..."],
    "questions": []
  }
}
```

### Error Response (Questions)
```json
{
  "detail": {
    "message": "Validation failed",
    "errors": ["Insufficient information for C4 Context diagram"],
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

### Error Response (Rejection)
```json
{
  "detail": {
    "message": "Validation failed",
    "errors": ["Input too short (4 words). Need at least 15 words"],
    "questions": [],
    "suggestions": [
      "Please provide more details about:",
      "  • What system/application are you building?",
      "  • Who will use it?",
      "  • What does it do?",
      "  • What external systems does it connect to?"
    ]
  }
}
```

## Frontend Display

```
┌─────────────────────────────────────────────────┐
│  ❌ Insufficient information for C4 diagram     │
│                                                  │
│  ❓ Please provide more information:            │
│  1. Who will use this system?                   │
│  2. What will users do with this system?        │
│                                                  │
│  💡 Suggestions:                                │
│  • Add information about who will interact      │
│  • Describe what users can do                   │
└─────────────────────────────────────────────────┘
```

## Key Principles

1. **Fail Fast**: Reject obvious issues early (empty, too short, gibberish)
2. **Be Helpful**: Provide specific questions and suggestions
3. **Guide Users**: Help them understand C4 requirements
4. **Save Costs**: Validate before calling expensive AI API
5. **Be Flexible**: Warnings don't block, only critical issues do
