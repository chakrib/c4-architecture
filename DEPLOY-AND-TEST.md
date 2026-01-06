# Deploy AWS Backend and Test Application

## Goal

Deploy the AWS serverless backend and connect the existing frontend to verify all features work identically to the FastAPI backend.

## Prerequisites

Before starting, ensure you have:

1. ✅ **AWS CLI** configured with credentials
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and region
   ```

2. ✅ **Terraform** installed
   ```bash
   terraform --version
   # Should show v1.0 or higher
   ```

3. ✅ **Python 3.11+** installed
   ```bash
   python3 --version
   ```

4. ✅ **AWS Bedrock Access** - Claude 3.5 Sonnet (Auto-enabled)
   - **Good news**: Bedrock models are now automatically enabled on first use!
   - **For Anthropic models**: First-time users may need to submit use case details
   - **No manual activation needed**: Models activate when first invoked
   - **Note**: If you get an access error, you may need to provide use case information via AWS Console

## Step 1: Deploy AWS Backend with Terraform

### Option A: Automated Deployment (Recommended)

```bash
cd backend-aws/terraform

# Build Lambda layer and deploy
./scripts/deploy.sh -e dev
```

This script will:
1. Build the Lambda layer with dependencies
2. Initialize Terraform
3. Show you the deployment plan
4. Ask for confirmation
5. Deploy all AWS resources
6. Display the API endpoint

### Option B: Manual Deployment

```bash
cd backend-aws/terraform

# 1. Build Lambda layer
./scripts/build-layer.sh

# 2. Initialize Terraform
terraform init

# 3. Review the plan
terraform plan -var-file=dev.tfvars

# 4. Deploy
terraform apply -var-file=dev.tfvars

# 5. Get API endpoint
terraform output api_endpoint
```

### Expected Output

After successful deployment, you should see:

```
Apply complete! Resources: 25 added, 0 changed, 0 destroyed.

Outputs:

api_endpoint = "https://xxxxx.execute-api.us-east-1.amazonaws.com/dev"
validate_function_name = "c4-diagram-generator-validate-dev"
generate_function_name = "c4-diagram-generator-generate-dev"
...
```

**Save the API endpoint** - you'll need it for the frontend!

## Step 2: Update Frontend Configuration

### Get the API Endpoint

```bash
cd backend-aws/terraform
API_ENDPOINT=$(terraform output -raw api_endpoint)
echo "API Endpoint: $API_ENDPOINT"
```

### Update Frontend Environment

```bash
cd ../../frontend

# Create or update .env file
cat > .env << EOF
VITE_API_BASE_URL=$API_ENDPOINT
EOF

# Verify the file
cat .env
```

Should show:
```
VITE_API_BASE_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/dev
```

### Restart Frontend

```bash
# Stop the current frontend if running (Ctrl+C)

# Install dependencies (if not already done)
npm install

# Start the frontend
npm run dev
```

The frontend should start on `http://localhost:5173` or `http://localhost:5174`.

## Step 3: Test All Features

Open your browser to `http://localhost:5173` (or the port shown).

### Test 1: Enhanced Validation ✅

**Test Case 1.1: Valid Input**
```
Input: "Build a web application with user authentication, database storage, and REST API for managing customer orders"

Expected:
✅ Validation passes
✅ No error messages
✅ Ready to generate diagram
```

**Test Case 1.2: Too Short (< 15 words)**
```
Input: "Build a web app"

Expected:
❌ Validation fails
❌ Error: "Please provide more details (minimum 15 words)"
```

**Test Case 1.3: Gibberish (< 3 meaningful terms)**
```
Input: "asdf qwer zxcv tyui fghj vbnm klop yuio hjkl bnmq wert asdf yuio"

Expected:
❌ Validation fails
❌ Error: "Input appears to be gibberish"
```

**Test Case 1.4: Missing System Information**
```
Input: "users can login and view data from external systems"

Expected:
❌ Validation fails
❌ Shows questions to clarify what system is being built
```

**Test Case 1.5: Complete Valid Input**
```
Input: "Build a web app in which WhatsApp messages, Google docs are used to generate a dashboard users to determine the actions planned in the near future"

Expected:
✅ Validation passes
✅ Recognizes: WhatsApp, Google Docs as external systems
✅ Recognizes: dashboard, determine as functionality indicators
✅ Ready to generate
```

### Test 2: Intelligent Suggestions ✅

**Test Case 2.1: Incomplete Input Triggers Suggestions**
```
Input: "web app for users"

Expected:
❌ Validation fails (too vague)
✅ System automatically generates 3 diverse suggestions
✅ Suggestions displayed as clickable cards
✅ Each suggestion has different interpretation
```

**Test Case 2.2: Select a Suggestion**
```
1. Enter: "web app for users"
2. Wait for suggestions to appear
3. Click on one of the suggestion cards

Expected:
✅ Selected suggestion populates the input field
✅ Diagram generation starts automatically
✅ C4 diagram is generated based on the suggestion
```

**Test Case 2.3: Complex Scenario**
```
Input: "Solution Overview: AWS 2.0 account vending happens at the App Family level. Each App Family gets one set of SDLC accounts with corresponding VPCs and roles. These SDLC accounts are shared by multiple applications which fall into the App Family."

Expected:
✅ Validation passes (sufficient detail)
✅ Diagram generated showing AWS account structure
✅ Shows App Family, SDLC accounts, applications
```

### Test 3: Diagram Generation ✅

**Test Case 3.1: Basic Generation**
```
Input: "Build a web application with user authentication, PostgreSQL database, and REST API"

Expected:
✅ Diagram generates successfully
✅ Shows PlantUML code
✅ Shows rendered diagram
✅ Includes: User, Web App, Database, API
✅ Shows relationships between components
```

**Test Case 3.2: Complex System**
```
Input: "Build an e-commerce platform with user authentication, product catalog, shopping cart, payment processing via Stripe, order management, email notifications via SendGrid, and admin dashboard"

Expected:
✅ Diagram generates successfully
✅ Shows all major components
✅ Shows external systems (Stripe, SendGrid)
✅ Shows relationships and data flow
```

### Test 4: Interactive Refinement ✅

**Test Case 4.1: Add Component**
```
1. Generate a diagram (any valid input)
2. In refinement box, enter: "Add a Redis cache between the web app and database"
3. Click "Refine Diagram"

Expected:
✅ New version created
✅ Redis cache component added
✅ Positioned between web app and database
✅ Version indicator shows "Version 2"
✅ Undo button enabled
```

**Test Case 4.2: Remove Component**
```
1. Generate a diagram with multiple components
2. Enter: "Remove the email service"
3. Click "Refine Diagram"

Expected:
✅ Email service removed from diagram
✅ Related connections removed
✅ Version incremented
✅ Change feedback displayed
```

**Test Case 4.3: Edit Labels**
```
1. Generate a diagram
2. Enter: "Change 'Web App' to 'Customer Portal'"
3. Click "Refine Diagram"

Expected:
✅ Label updated in diagram
✅ Version incremented
✅ Undo available
```

**Test Case 4.4: Undo/Redo**
```
1. Generate a diagram
2. Make a refinement (e.g., add cache)
3. Click "Undo" button
4. Click "Redo" button

Expected:
✅ Undo: Returns to previous version
✅ Redo: Returns to refined version
✅ Version indicator updates correctly
✅ Diagram updates correctly
```

**Test Case 4.5: Multiple Refinements**
```
1. Generate a diagram
2. Add a cache (Version 2)
3. Add a load balancer (Version 3)
4. Remove a component (Version 4)
5. Use Undo to go back to Version 2

Expected:
✅ Each refinement creates new version
✅ Version history maintained
✅ Can navigate through versions
✅ Diagram updates correctly at each step
```

## Step 4: Verify AWS Resources

### Check Lambda Functions

```bash
cd backend-aws/terraform

# List all Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `c4-diagram-generator`)].FunctionName'

# Should show:
# - c4-diagram-generator-validate-dev
# - c4-diagram-generator-suggest-dev
# - c4-diagram-generator-generate-dev
# - c4-diagram-generator-refine-dev
```

### Check API Gateway

```bash
# Get API Gateway ID
terraform output api_gateway_id

# Test validate endpoint directly
API_ENDPOINT=$(terraform output -raw api_endpoint)

curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'

# Should return: {"valid": true, "message": "Input is valid"}
```

### Check CloudWatch Logs

```bash
# Get function name
FUNCTION_NAME=$(terraform output -raw validate_function_name)

# Tail logs
aws logs tail /aws/lambda/$FUNCTION_NAME --follow

# Make a request from frontend and watch logs appear
```

### Check DynamoDB (if enabled)

```bash
# Get table name
terraform output dynamodb_table_name

# List items (should be empty initially)
TABLE_NAME=$(terraform output -raw dynamodb_table_name)
aws dynamodb scan --table-name $TABLE_NAME
```

## Step 5: Performance Testing

### Test Cold Start

```bash
# Wait 5 minutes for Lambda to go cold
# Then make a request

API_ENDPOINT=$(terraform output -raw api_endpoint)

time curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'

# First request (cold start): 1-2 seconds
# Subsequent requests (warm): 200-500ms
```

### Test All Endpoints

```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)

# 1. Validate
echo "Testing Validate..."
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}' | jq

# 2. Suggest
echo "Testing Suggest..."
curl -X POST "${API_ENDPOINT}/api/diagrams/suggest-improvements" \
  -H "Content-Type: application/json" \
  -d '{"description": "web app"}' | jq

# 3. Generate
echo "Testing Generate..."
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}' | jq

# 4. Refine
echo "Testing Refine..."
curl -X POST "${API_ENDPOINT}/api/diagrams/refine" \
  -H "Content-Type: application/json" \
  -d '{
    "current_diagram": "@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\nPerson(user, \"User\")\nSystem(webapp, \"Web App\")\nRel(user, webapp, \"Uses\")\n@enduml",
    "refinement_request": "Add a database"
  }' | jq
```

## Step 6: Compare with FastAPI Backend

### Side-by-Side Comparison

**Start FastAPI backend** (in another terminal):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Test the same input on both**:

**FastAPI** (http://localhost:8000):
```bash
curl -X POST "http://localhost:8000/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'
```

**AWS** (via API Gateway):
```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'
```

**Expected**: Identical responses from both backends

### Feature Parity Checklist

| Feature | FastAPI | AWS Lambda | Status |
|---------|---------|------------|--------|
| Enhanced Validation | ✅ | ✅ | ✅ Match |
| 15+ words check | ✅ | ✅ | ✅ Match |
| Gibberish detection | ✅ | ✅ | ✅ Match |
| C4 requirements | ✅ | ✅ | ✅ Match |
| Intelligent Suggestions | ✅ | ✅ | ✅ Match |
| 3 diverse suggestions | ✅ | ✅ | ✅ Match |
| Diagram Generation | ✅ | ✅ | ✅ Match |
| Claude 3 Haiku | ✅ | ✅ | ✅ Match |
| PlantUML output | ✅ | ✅ | ✅ Match |
| Interactive Refinement | ✅ | ✅ | ✅ Match |
| Natural language | ✅ | ✅ | ✅ Match |
| Version history | ✅ | ✅ | ✅ Match |
| Undo/Redo | ✅ | ✅ | ✅ Match |

## Troubleshooting

### Issue: Frontend can't connect to AWS

**Check**:
```bash
# 1. Verify API endpoint in frontend/.env
cat frontend/.env

# 2. Check CORS configuration
cd backend-aws/terraform
terraform output api_endpoint

# 3. Test endpoint directly
curl -X POST "$(terraform output -raw api_endpoint)/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "test"}'
```

**Solution**: Ensure CORS is enabled in API Gateway (already configured in Terraform)

### Issue: Bedrock Access Denied

**Error**: `AccessDeniedException: Could not access model`

**Solution**:

AWS Bedrock models are now **automatically enabled** on first use. However, for Anthropic models, first-time users may need to provide use case details:

1. **Try deploying first** - The model may auto-enable on first invocation
2. **If access denied**:
   - Go to AWS Console → Bedrock → Model catalog
   - Find Claude 3.5 Sonnet
   - Open in playground or submit use case details
   - Retry deployment

**Note**: The old "Model access" page has been retired. Models now activate automatically when first invoked.

### Issue: Lambda Timeout

**Error**: `Task timed out after 30.00 seconds`

**Solution**:
```bash
# Edit terraform/variables.tf
# Change lambda_timeout from 30 to 60

# Redeploy
terraform apply -var-file=dev.tfvars
```

### Issue: Cold Start Delays

**Symptom**: First request takes 2-3 seconds

**Solution**: This is normal for Lambda cold starts. Subsequent requests will be faster (200-500ms). For production, consider:
- Provisioned concurrency (costs more)
- Keep functions warm with scheduled pings
- Accept cold starts (acceptable for this use case)

### Issue: Validation Not Working

**Check CloudWatch Logs**:
```bash
FUNCTION_NAME=$(terraform output -raw validate_function_name)
aws logs tail /aws/lambda/$FUNCTION_NAME --follow
```

**Common Issues**:
- Missing validation logic in Lambda layer
- Incorrect environment variables
- Python import errors

### Issue: Suggestions Not Generating

**Check**:
1. Bedrock access enabled
2. Claude 3 Haiku model accessible
3. CloudWatch logs for errors

```bash
FUNCTION_NAME=$(terraform output -raw suggest_function_name)
aws logs tail /aws/lambda/$FUNCTION_NAME --follow
```

## Success Criteria

✅ **Deployment**:
- All 4 Lambda functions deployed
- API Gateway accessible
- CloudWatch logs working

✅ **Frontend Connection**:
- Frontend connects to AWS backend
- No CORS errors
- All API calls successful

✅ **Feature Parity**:
- Enhanced validation works identically
- Intelligent suggestions work identically
- Diagram generation works identically
- Interactive refinement works identically

✅ **Performance**:
- Cold start: 1-2 seconds (acceptable)
- Warm requests: 200-500ms (good)
- Bedrock calls: 2-3 seconds (expected)

## Next Steps After Testing

Once all tests pass:

1. ✅ **Document any differences** (if found)
2. ✅ **Set up monitoring** (CloudWatch alarms)
3. ✅ **Configure production environment** (prod.tfvars)
4. ✅ **Set up CI/CD** (GitHub Actions)
5. ✅ **Add custom domain** (optional)
6. ✅ **Implement API key** (optional)

## Cleanup (if needed)

To remove all AWS resources:

```bash
cd backend-aws/terraform
terraform destroy -var-file=dev.tfvars
```

**Warning**: This will delete all resources including DynamoDB data.

## Summary

This guide walks you through:
1. ✅ Deploying AWS backend with Terraform
2. ✅ Connecting frontend to AWS
3. ✅ Testing all features
4. ✅ Verifying feature parity with FastAPI
5. ✅ Troubleshooting common issues

**Expected Result**: Frontend works identically with AWS backend as it did with FastAPI backend, with the added benefits of serverless scalability and cost optimization.

---

**Ready to deploy and test!** 🚀

Start with: `cd backend-aws/terraform && ./scripts/deploy.sh -e dev`
