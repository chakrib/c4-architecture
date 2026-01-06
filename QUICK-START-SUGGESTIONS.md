# Quick Start - Intelligent Suggestions

## Try It Now!

### 1. Start the Servers

```bash
# Terminal 1: Backend
cd backend
./venv/bin/python app/main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Open Browser
Navigate to: **http://localhost:5173**

### 3. Test with Incomplete Input

Copy and paste this incomplete description:

```
Solution Overview: As part of AWS 2.0 account vending happens at the App Family level. Which means each App Family gets one set of SDLC accounts, with corresponding VPCs, and roles associated. These SDLC accounts are shared by multiple Application which fall into the App Family. Which also means, each application deployed is these accounts could potentially share the data. Data could be in databases, S3 buckets of file systems, Cache etc. At this time, only data sharing is the concern, not the network, or other resources.
```

### 4. Click "Generate Diagram"

The system will:
1. ✅ Detect that input is incomplete
2. 🤔 Automatically analyze it with Claude
3. 💡 Show you 3 improved versions

### 5. Select a Suggestion

Click on any of the 3 options or click "Use This Version" button.

The system will:
1. ✅ Update your input with the selected version
2. ✅ Automatically generate the diagram
3. 🎉 Display your C4 diagram!

## What You'll See

### Step 1: Incomplete Input Detected
```
❌ Insufficient information for C4 Context diagram

❓ Please provide more information:
1. Who will use this system?
2. What will users do with this system?

💡 Would you like me to suggest improved versions?
```

### Step 2: Suggestions Appear
```
💡 Suggested Improvements

Based on your input, here are some interpretations that would work well for C4 diagrams:

┌─────────────────────────────────────────────────────────┐
│ Option 1: Data Isolation Enforcement System            │
│ A system to prevent unauthorized data access           │
│                                                         │
│ Implement a data isolation enforcement mechanism...    │
│                                                         │
│ [Use This Version]                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Option 2: Data Access Governance Platform              │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Option 3: Multi-Tenant Data Isolation Service          │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### Step 3: Diagram Generated
After selecting an option, you'll see a beautiful C4 diagram with:
- 👤 Users/Actors
- 🔷 Your System
- 📦 External Systems
- Clear relationships and data flows

## More Examples to Try

### Example 1: Process Description
```
We have a process where data needs to be validated before being stored in the database.
```

**Result**: System suggests tool/service interpretations

### Example 2: Business Context
```
Our company needs to manage customer orders from multiple channels and ensure inventory is updated correctly.
```

**Result**: System suggests order management system variations

### Example 3: Technical Context
```
Using AWS Lambda functions to process events from SQS queues and store results in DynamoDB.
```

**Result**: System suggests event processing architecture options

## Tips

1. **Be descriptive** - More context = better suggestions
2. **Include domain terms** - AWS, databases, APIs, etc.
3. **Mention the problem** - What are you trying to solve?
4. **Don't worry about structure** - The AI will restructure it for you

## Troubleshooting

### No suggestions appear
- Check that input is 15+ words
- Ensure it's not gibberish
- Check backend console for errors

### Suggestions don't match intent
- Try adding more context to your original input
- Click "Cancel" and edit manually
- Select the closest option and refine it

### Backend error
```bash
# Check backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

## What's Next?

After seeing suggestions work:
1. ✅ Try your own descriptions
2. ✅ Experiment with different domains
3. ✅ See how the AI interprets various inputs
4. ✅ Learn what makes good C4 descriptions

## Status

🟢 **READY TO USE** - The intelligent suggestion system is fully functional!
