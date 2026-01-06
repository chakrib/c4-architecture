# Migration Guide: FastAPI to AWS Serverless

This guide walks you through migrating from the current FastAPI backend to AWS serverless architecture.

## Overview

**From:**
- FastAPI application
- Anthropic API (direct)
- Local/VM hosting

**To:**
- AWS Lambda functions
- AWS Bedrock (Claude)
- API Gateway
- Serverless infrastructure

## Prerequisites

### 1. AWS Account Setup
- AWS account with admin access
- AWS CLI installed and configured
- AWS SAM CLI installed

### 2. Enable AWS Bedrock
```bash
# Request access to Claude models in AWS Bedrock
# Go to: AWS Console → Bedrock → Model access
# Enable: Claude 3 Haiku
```

### 3. Install Tools
```bash
# AWS CLI
pip install awscli

# SAM CLI
pip install aws-sam-cli

# Configure AWS credentials
aws configure
```

## Migration Steps

### Step 1: Test Locally (1-2 hours)

```bash
cd backend-aws

# Build
sam build

# Start local API
sam local start-api

# Test endpoints
curl http://localhost:3000/api/diagrams/validate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Build a web app..."}'
```

### Step 2: Deploy to AWS (30 minutes)

```bash
# Deploy with guided prompts
sam deploy --guided

# Follow prompts:
# - Stack name: c4-diagram-generator
# - Region: us-east-1
# - Confirm changes: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to config: Y
```

**Output:**
```
CloudFormation outputs:
ApiEndpoint: https://xxxxx.execute-api.us-east-1.amazonaws.com/dev
```

### Step 3: Update Frontend (15 minutes)

Update `frontend/.env`:
```env
# Old
VITE_BACKEND_URL=http://localhost:8000

# New
VITE_BACKEND_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/dev
```

Rebuild and deploy frontend:
```bash
cd frontend
npm run build

# Deploy to S3 (if using S3 hosting)
aws s3 sync dist/ s3://your-frontend-bucket/
```

### Step 4: Test End-to-End (30 minutes)

1. Open frontend in browser
2. Test diagram generation
3. Test suggestions
4. Test refinement
5. Verify all features work

### Step 5: Monitor and Optimize (Ongoing)

```bash
# View logs
sam logs -n GenerateFunction --tail

# View metrics in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=c4-diagram-generator-GenerateFunction \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Code Changes Required

### Minimal Changes

The Lambda functions are designed to be compatible with your existing logic. Main changes:

1. **API calls**: Anthropic SDK → Bedrock SDK
2. **Authentication**: API key → IAM roles
3. **Deployment**: Local server → Lambda functions

### No Changes Needed

- ✅ Validation logic (same)
- ✅ Prompt engineering (same)
- ✅ Frontend code (just update URL)
- ✅ Business logic (same)

## Rollback Plan

If issues arise, you can quickly rollback:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name c4-diagram-generator

# Revert frontend .env
VITE_BACKEND_URL=http://localhost:8000

# Restart FastAPI backend
cd backend
./venv/bin/python app/main.py
```

## Cost Comparison

### Before (FastAPI + Anthropic)
```
Anthropic API: ~$0.25 per 1M input tokens
Server: $5-50/month
Total: ~$10-100/month
```

### After (AWS Serverless)
```
Bedrock: ~$0.25 per 1M input tokens (same)
Lambda: $0.20 per 1M requests
API Gateway: $3.50 per 1M requests
Total: ~$5-50/month (50-70% savings for low traffic)
```

## Troubleshooting

### Issue: Bedrock access denied
**Solution:** Enable Claude models in Bedrock console

### Issue: Lambda timeout
**Solution:** Increase timeout in template.yaml (currently 60s)

### Issue: CORS errors
**Solution:** Check API Gateway CORS settings in template.yaml

### Issue: Cold starts
**Solution:** 
- Use provisioned concurrency (costs more)
- Or accept 1-2 second cold start (acceptable for this use case)

## Next Steps

After successful migration:

1. ✅ Set up CloudWatch alarms
2. ✅ Configure auto-scaling (if needed)
3. ✅ Add DynamoDB for persistence
4. ✅ Set up CI/CD pipeline
5. ✅ Configure custom domain
6. ✅ Add WAF for security

## Support

If you encounter issues:
1. Check CloudWatch logs
2. Review SAM deployment output
3. Verify IAM permissions
4. Test locally with `sam local`

## Timeline

**Total migration time: 3-5 hours**
- Setup: 1 hour
- Deployment: 1 hour
- Testing: 1-2 hours
- Optimization: 1 hour
