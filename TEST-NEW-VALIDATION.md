# Test the New Validation System

## Quick Start

1. **Start the backend**:
```bash
cd backend
./venv/bin/python app/main.py
```

2. **Start the frontend** (in another terminal):
```bash
cd frontend
npm run dev
```

3. **Open browser**: http://localhost:5173

## Test Cases to Try

### ✅ Test 1: Perfect Input (Should Generate)
Copy and paste this:
```
Build a web application where users can upload files to Amazon S3 storage and transfer them to SFTP servers. Administrators can manage user accounts and monitor file transfers through a dashboard.
```

**Expected**: ✅ Generates a beautiful C4 diagram

---

### ❌ Test 2: Too Short (Should Reject)
Copy and paste this:
```
Build a web app
```

**Expected**: 
```
❌ Input too short (4 words). Need at least 15 words for meaningful C4 diagram.

💡 Suggestions:
Please provide more details about:
  • What system/application are you building?
  • Who will use it?
  • What does it do?
  • What external systems does it connect to?
```

---

### ❌ Test 3: Gibberish (Should Reject)
Copy and paste this:
```
asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv tyuityu ghfgghfg
```

**Expected**:
```
❌ Input appears to be gibberish or lacks technical/business context

💡 Suggestions:
Please describe a real system or application using clear language
Example: 'Build a web application where users can upload documents...'
```

---

### ❌ Test 4: No System Identified (Should Reject)
Copy and paste this:
```
there are many people who want to do things and they need help with various tasks every single day
```

**Expected**:
```
❌ Cannot identify what system/application you want to build

❓ Please provide more information:
1. What type of system are you building? (e.g., web app, mobile app, API service, platform)

💡 Suggestions:
Please specify the system you want to create
```

---

### ⚠️ Test 5: Missing Users (Should Ask Question)
Copy and paste this:
```
Build a web application that processes data from multiple sources, stores it in a database, and generates reports. The system integrates with external APIs for data collection.
```

**Expected**:
```
❌ Insufficient information for C4 Context diagram

❓ Please provide more information:
1. Who will use this system? (e.g., customers, employees, administrators)

💡 Suggestions:
Add information about who will interact with the system
```

**Fix it by adding users**:
```
Build a web application where business analysts can process data from multiple sources, store it in a database, and generate reports. The system integrates with external APIs for data collection.
```

Now it should generate! ✅

---

### ⚠️ Test 6: Missing Functionality (Should Ask Question)
Copy and paste this:
```
Create a mobile application for customers that connects to our backend system and external payment services for processing transactions securely.
```

**Expected**:
```
❌ Insufficient information for C4 Context diagram

❓ Please provide more information:
1. What will users do with this system? What are the main features?

💡 Suggestions:
Describe what users can do with the system
```

**Fix it by adding functionality**:
```
Create a mobile application where customers can browse products, add items to cart, and checkout securely. The app connects to our backend system and Stripe payment service for processing transactions.
```

Now it should generate! ✅

---

### ✅ Test 7: E-commerce (Should Generate)
Copy and paste this:
```
Create an e-commerce platform where customers browse products, add items to cart, and checkout using Stripe payment gateway. Administrators manage inventory and view sales reports through an admin panel.
```

**Expected**: ✅ Generates diagram with users, system, and external services

---

### ✅ Test 8: Mobile App (Should Generate)
Copy and paste this:
```
Develop a mobile application for employees to track their work hours, submit timesheets, and request time off. The system integrates with the company's payroll system and sends notifications via email.
```

**Expected**: ✅ Generates diagram with employees, mobile app, and integrations

---

### ✅ Test 9: API Service (Should Generate)
Copy and paste this:
```
Design an API service that processes customer orders from multiple sales channels, validates inventory availability, and sends order confirmations via SendGrid. The service connects to our inventory database and Stripe payment processor.
```

**Expected**: ✅ Generates diagram with API service and external systems

---

## Testing via cURL

If you prefer command-line testing:

### Valid Input
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web application where users can upload files to Amazon S3 storage and transfer them to SFTP servers. Administrators can manage user accounts and monitor file transfers through a dashboard.",
    "diagram_type": "context"
  }' | jq
```

### Too Short
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web app",
    "diagram_type": "context"
  }' | jq
```

### Gibberish
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv",
    "diagram_type": "context"
  }' | jq
```

### Missing Users
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web application that processes data from multiple sources, stores it in a database, and generates reports. The system integrates with external APIs for data collection.",
    "diagram_type": "context"
  }' | jq
```

## What to Look For

### Success (200 OK)
- Returns `mermaid_code` field
- Returns `validation` object with warnings/suggestions
- Frontend displays diagram

### Validation Error (400 Bad Request)
- Returns `detail` object with:
  - `errors`: What's wrong
  - `questions`: What information is needed
  - `suggestions`: How to fix it
- Frontend displays formatted error with ❌, ❓, and 💡 icons

## Checklist

- [ ] Test 1: Perfect input generates diagram
- [ ] Test 2: Too short is rejected with helpful message
- [ ] Test 3: Gibberish is rejected
- [ ] Test 4: No system identified is rejected with question
- [ ] Test 5: Missing users asks question
- [ ] Test 6: Missing functionality asks question
- [ ] Test 7-9: Various valid inputs generate diagrams

## Success Criteria

✅ All rejection cases show helpful error messages
✅ All question cases show specific questions
✅ All valid cases generate diagrams
✅ Error messages are clear and actionable
✅ Frontend displays questions with ❓ icon
✅ Frontend displays suggestions with 💡 icon

## Troubleshooting

### Backend not starting
```bash
# Check if port 8000 is in use
lsof -i :8000
kill -9 <PID>

# Restart backend
cd backend
./venv/bin/python app/main.py
```

### Frontend not connecting
```bash
# Check backend health
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### API key error
```bash
# Verify .env file
cat backend/.env | grep ANTHROPIC_API_KEY
```

## Next Steps

After testing:
1. ✅ Verify all test cases work as expected
2. ✅ Try your own custom inputs
3. ✅ Adjust validation thresholds if needed
4. 📝 Document any edge cases you find
5. 🚀 Deploy to production when ready
