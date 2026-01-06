# Validation Test Cases

## New Validation Rules

1. **Minimum 15 words** - Rejects inputs shorter than 15 words
2. **Gibberish detection** - Rejects inputs with fewer than 3 meaningful technical/business terms
3. **C4 Level 1 requirements**:
   - Must identify the SYSTEM being built
   - Must identify USERS/ACTORS (asks question if missing)
   - Should describe FUNCTIONALITY (warns if missing)
   - Should mention EXTERNAL SYSTEMS (warns if missing)

## Test Cases

### ✅ Valid Inputs (Should Generate Diagram)

#### Test 1: Complete Description
```
Build a web application where users can upload files to Amazon S3 storage and transfer them to SFTP servers. Administrators can manage user accounts and monitor file transfers through a dashboard.
```
**Expected**: Generates diagram (has system, users, functionality, external systems)

#### Test 2: E-commerce Platform
```
Create an e-commerce platform where customers browse products, add items to cart, and checkout using Stripe payment gateway. Administrators manage inventory and view sales reports through admin panel.
```
**Expected**: Generates diagram (complete C4 Level 1 info)

#### Test 3: Mobile App
```
Develop a mobile application for employees to track their work hours, submit timesheets, and request time off. The system integrates with the company's payroll system and sends notifications via email.
```
**Expected**: Generates diagram (complete C4 Level 1 info)

#### Test 4: API Service
```
Design an API service that processes customer orders from multiple sales channels, validates inventory availability, and sends order confirmations via SendGrid. The service connects to our inventory database and payment processor.
```
**Expected**: Generates diagram (complete C4 Level 1 info)

---

### ❌ Invalid Inputs (Should Reject)

#### Test 5: Too Short (< 15 words)
```
Build a web app for users
```
**Expected**: 
- Error: "Input too short (7 words). Need at least 15 words for meaningful C4 diagram."
- Suggestions about what to include

#### Test 6: Gibberish
```
asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv tyuityu ghfgghfg rtyrty fghfgh dfsdfsd werwer
```
**Expected**: 
- Error: "Input appears to be gibberish or lacks technical/business context"
- Example of valid input

#### Test 7: Nonsense Sentence
```
the quick brown fox jumps over the lazy dog and runs through the forest very fast today
```
**Expected**: 
- Error: "Input appears to be gibberish or lacks technical/business context"
- Fewer than 3 meaningful technical terms

#### Test 8: No System Identified
```
there are many people who want to do things and they need help with various tasks every day
```
**Expected**: 
- Error: "Cannot identify what system/application you want to build"
- Question: "What type of system are you building?"

---

### ⚠️ Incomplete Inputs (Should Ask Questions)

#### Test 9: Missing Users
```
Build a web application that processes data from multiple sources, stores it in a database, and generates reports. The system integrates with external APIs for data collection.
```
**Expected**: 
- Error: "Insufficient information for C4 Context diagram"
- Question: "Who will use this system? (e.g., customers, employees, administrators)"

#### Test 10: Missing Functionality
```
Create a mobile application for customers that connects to our backend system and external payment services for processing transactions securely.
```
**Expected**: 
- Error: "Insufficient information for C4 Context diagram"
- Question: "What will users do with this system? What are the main features?"

#### Test 11: Minimal but Valid
```
Develop a system where users upload documents to cloud storage and share them with team members through a web interface.
```
**Expected**: 
- Generates diagram (has system, users, basic functionality)
- May have warnings about external systems

---

## Testing via cURL

### Valid Input Test
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web application where users can upload files to Amazon S3 storage and transfer them to SFTP servers. Administrators can manage user accounts and monitor file transfers through a dashboard.",
    "diagram_type": "context"
  }'
```

### Too Short Test
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web app for users",
    "diagram_type": "context"
  }'
```

### Gibberish Test
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv tyuityu ghfgghfg rtyrty fghfgh dfsdfsd werwer",
    "diagram_type": "context"
  }'
```

### Missing Users Test
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web application that processes data from multiple sources, stores it in a database, and generates reports. The system integrates with external APIs for data collection.",
    "diagram_type": "context"
  }'
```

---

## Validation Logic Summary

### Rejection Criteria (is_valid=false)
1. Empty input
2. Less than 15 words
3. Fewer than 3 meaningful technical/business terms (gibberish)
4. No system/application identified
5. Missing critical C4 Level 1 information (users, functionality)

### Warning Criteria (is_valid=true with warnings)
1. No external systems mentioned
2. Limited functionality description

### Question Flow
When validation fails due to missing information (not gibberish), the system:
1. Returns specific questions about what's missing
2. Provides suggestions on what to add
3. Helps user provide complete C4 Level 1 information

---

## Expected Error Message Format

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

---

## Frontend Display

The frontend now displays:
- ❌ **Errors** in red
- ❓ **Questions** as numbered list
- 💡 **Suggestions** as helpful tips

This guides users to provide complete information for C4 diagram generation.
