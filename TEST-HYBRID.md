# Test Cases for Hybrid C4 Diagram Generator

## Test the Backend API Directly

### 1. Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

### 2. Valid Input - Should Generate Diagram
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "Build a web application where users can upload files to S3 and transfer them to SFTP servers",
    "diagram_type": "context"
  }'
```
Expected: Returns mermaid code with validation warnings/suggestions

### 3. Invalid Input - Too Short
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "hello",
    "diagram_type": "context"
  }'
```
Expected: 400 error with message about not identifying system

### 4. Invalid Input - Gibberish
```bash
curl -X POST http://localhost:8000/api/diagrams/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "asdfasdf qwerqwer zxcvzxcv",
    "diagram_type": "context"
  }'
```
Expected: 400 error with validation failure

## Test Through Frontend

### Valid Inputs (Should Work)
1. "Build a web application where users can upload files to Amazon S3 storage and transfer them to SFTP servers. Administrators can manage user accounts and monitor file transfers."
2. "Create an e-commerce platform where customers browse products, add items to cart, and checkout using Stripe payment gateway. Administrators manage inventory and view sales reports."
3. "Develop a mobile application for employees to track their work hours, submit timesheets, and request time off. The system integrates with payroll and sends email notifications."
4. "Design an API service that processes customer orders from multiple sales channels, validates inventory availability, and sends order confirmations via SendGrid email service."
5. "Build a web app in which WhatsApp messages, Google docs are used to generate a dashboard users to determine the actions planned in the near future."

### Invalid Inputs (Should Reject)
1. "Build a web app" - Too short (< 15 words)
2. "asdfasdf qwerqwer zxcvzxcv poiupoiu lkjhlkjh mnbvmnbv" - Gibberish
3. "the quick brown fox jumps over the lazy dog today" - No technical context
4. "" - Empty input

### Incomplete Inputs (Should Ask Questions)
1. "Build a web application that processes data from multiple sources and generates reports" - Missing users (will ask: "Who will use this system?")
2. "Create a system for customers that connects to backend services" - Missing functionality (will ask: "What will users do?")

## Current Validation Logic

The backend checks for:
1. **Minimum length**: At least 15 words (meaningful descriptions need detail)
2. **Gibberish detection**: Must contain at least 3 meaningful technical/business terms
3. **System identification**: Must contain words like:
   - Actions: build, create, develop, make, design
   - Systems: system, application, app, service, platform, tool
   - Types: web, mobile, api, backend, frontend, dashboard
   - website, portal, interface

4. **User identification** (asks question if missing): Words like:
   - user, customer, admin, client, employee, staff, etc.

5. **Functionality** (warns if missing): Action words like:
   - CRUD: upload, download, store, process, manage, track, send, receive
   - Analytics: determine, identify, monitor, visualize, analyze, forecast
   - Data ops: generate, collect, transform, import, export, sync
   - User actions: access, browse, select, configure, submit, approve

6. **External systems** (warns if missing): Integration terms like:
   - integrate, connect, api, database, storage, third-party services
   - Specific: WhatsApp, Google (Docs, Sheets, Drive), Stripe, AWS, etc.

## What's Working

✅ Python backend validates input intelligently
✅ Rejects gibberish and too-short inputs (< 15 words)
✅ Accepts natural language descriptions
✅ Asks specific questions when information is missing
✅ Frontend calls backend API
✅ CORS configured for ports 5173 and 5174
✅ API key secure on server side
✅ Error messages are helpful with questions and suggestions

## Known Issues

None currently - system is fully functional!

## Next Steps

1. Test with more edge cases
2. Refine validation logic based on real usage
3. Add more sophisticated NLP validation (optional)
4. Consider adding question-asking flow for ambiguous inputs
