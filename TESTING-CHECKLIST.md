# AWS Backend Testing Checklist

Use this checklist to verify the AWS backend works identically to the FastAPI backend.

## Pre-Deployment Checklist

- [ ] AWS CLI configured (`aws configure`)
- [ ] Terraform installed (`terraform --version`)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] AWS Bedrock access (Claude 3.5 Sonnet - Auto-enabled)
  - **Note**: Models now auto-enable on first use
  - First-time Anthropic users may need to submit use case details
  - If access denied, visit AWS Console → Bedrock → Model catalog

## Deployment Checklist

- [ ] Navigate to `backend-aws/terraform`
- [ ] Run `./scripts/deploy.sh -e dev`
- [ ] Deployment completes successfully
- [ ] API endpoint displayed
- [ ] Save API endpoint for frontend

## Frontend Configuration Checklist

- [ ] Get API endpoint: `terraform output api_endpoint`
- [ ] Update `frontend/.env` with API endpoint
- [ ] Restart frontend: `npm run dev`
- [ ] Frontend loads without errors
- [ ] No CORS errors in browser console

## Feature Testing Checklist

### 1. Enhanced Validation

- [ ] **Valid input (15+ words)**: Passes validation
- [ ] **Too short (< 15 words)**: Shows error "minimum 15 words"
- [ ] **Gibberish (< 3 terms)**: Shows error "appears to be gibberish"
- [ ] **Missing system info**: Shows clarifying questions
- [ ] **Complete valid input**: Passes and ready to generate

### 2. Intelligent Suggestions

- [ ] **Incomplete input**: Triggers suggestions automatically
- [ ] **3 suggestions displayed**: Shows 3 diverse interpretations
- [ ] **Click suggestion**: Populates input and generates diagram
- [ ] **Suggestions are diverse**: Each has different interpretation
- [ ] **Complex scenario**: Handles detailed descriptions

### 3. Diagram Generation

- [ ] **Basic generation**: Creates diagram successfully
- [ ] **PlantUML code**: Displays correctly
- [ ] **Rendered diagram**: Shows visual diagram
- [ ] **Components included**: All expected components present
- [ ] **Relationships shown**: Connections between components
- [ ] **Complex system**: Handles multiple components

### 4. Interactive Refinement

- [ ] **Add component**: Successfully adds new component
- [ ] **Remove component**: Successfully removes component
- [ ] **Edit labels**: Successfully updates labels
- [ ] **Version tracking**: Version number increments
- [ ] **Undo button**: Works correctly
- [ ] **Redo button**: Works correctly
- [ ] **Multiple refinements**: Can chain multiple changes
- [ ] **Change feedback**: Displays what changed

## API Endpoint Testing

### Direct API Tests (using curl)

- [ ] **Validate endpoint**: Returns correct response
  ```bash
  curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
    -H "Content-Type: application/json" \
    -d '{"description": "Build a web app with auth and database"}'
  ```

- [ ] **Suggest endpoint**: Returns 3 suggestions
  ```bash
  curl -X POST "${API_ENDPOINT}/api/diagrams/suggest-improvements" \
    -H "Content-Type: application/json" \
    -d '{"description": "web app"}'
  ```

- [ ] **Generate endpoint**: Returns PlantUML diagram
  ```bash
  curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
    -H "Content-Type: application/json" \
    -d '{"description": "Build a web app with auth and database"}'
  ```

- [ ] **Refine endpoint**: Returns refined diagram
  ```bash
  curl -X POST "${API_ENDPOINT}/api/diagrams/refine" \
    -H "Content-Type: application/json" \
    -d '{"current_diagram": "...", "refinement_request": "Add a database"}'
  ```

## AWS Resources Verification

- [ ] **Lambda functions**: All 4 functions deployed
  ```bash
  aws lambda list-functions --query 'Functions[?contains(FunctionName, `c4-diagram-generator`)].FunctionName'
  ```

- [ ] **API Gateway**: Accessible and responding
  ```bash
  terraform output api_gateway_id
  ```

- [ ] **CloudWatch Logs**: Logs appearing for requests
  ```bash
  aws logs tail /aws/lambda/$(terraform output -raw validate_function_name) --follow
  ```

- [ ] **DynamoDB**: Table created (if enabled)
  ```bash
  terraform output dynamodb_table_name
  ```

## Performance Testing

- [ ] **Cold start**: First request completes (1-2 seconds acceptable)
- [ ] **Warm requests**: Subsequent requests fast (200-500ms)
- [ ] **Bedrock calls**: Claude responses (2-3 seconds expected)
- [ ] **No timeouts**: All requests complete successfully

## Feature Parity with FastAPI

Compare responses from FastAPI and AWS backends:

- [ ] **Validation logic**: Identical responses
- [ ] **Suggestion quality**: Similar suggestions
- [ ] **Diagram structure**: Same PlantUML format
- [ ] **Refinement behavior**: Same refinement results
- [ ] **Error handling**: Same error messages

## Browser Testing

- [ ] **Chrome**: All features work
- [ ] **Firefox**: All features work
- [ ] **Safari**: All features work
- [ ] **Edge**: All features work
- [ ] **No console errors**: Clean console
- [ ] **No CORS errors**: CORS working correctly

## Edge Cases Testing

- [ ] **Empty input**: Handled correctly
- [ ] **Very long input**: Handled correctly
- [ ] **Special characters**: Handled correctly
- [ ] **Multiple rapid requests**: No errors
- [ ] **Network interruption**: Graceful error handling

## Monitoring and Logging

- [ ] **CloudWatch Logs**: Logs visible for all functions
- [ ] **X-Ray Traces**: Traces appearing (if enabled)
- [ ] **Error logs**: Errors logged correctly
- [ ] **Request/Response logs**: Complete logging

## Security Testing

- [ ] **CORS**: Only allowed origins accepted
- [ ] **HTTPS**: All requests over HTTPS
- [ ] **No exposed secrets**: No API keys in responses
- [ ] **IAM permissions**: Least privilege working

## Cost Verification

- [ ] **AWS Cost Explorer**: Check current costs
- [ ] **Lambda invocations**: Count matches expectations
- [ ] **Bedrock usage**: Token usage reasonable
- [ ] **DynamoDB usage**: Read/write units reasonable

## Documentation Verification

- [ ] **API endpoint documented**: Saved for team
- [ ] **Environment variables**: Documented
- [ ] **Deployment process**: Documented
- [ ] **Troubleshooting steps**: Documented

## Final Verification

- [ ] **All features working**: 100% feature parity
- [ ] **No errors**: Clean execution
- [ ] **Performance acceptable**: Response times good
- [ ] **Frontend happy**: No changes needed to frontend code
- [ ] **Team notified**: API endpoint shared

## Issues Found

Document any issues discovered during testing:

| Issue | Severity | Status | Notes |
|-------|----------|--------|-------|
|       |          |        |       |
|       |          |        |       |
|       |          |        |       |

## Sign-off

- [ ] **Tested by**: _______________
- [ ] **Date**: _______________
- [ ] **All tests passed**: Yes / No
- [ ] **Ready for production**: Yes / No

## Notes

Additional observations or comments:

---

**Status**: 
- ⏳ Not Started
- 🔄 In Progress
- ✅ Complete
- ❌ Failed

**Overall Status**: _____________
