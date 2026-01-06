# Deployment Guide

## Quick Deploy

```bash
# 1. Build
sam build

# 2. Deploy
sam deploy --guided

# 3. Get API endpoint
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

## Detailed Steps

### 1. Prerequisites

- AWS CLI configured
- SAM CLI installed
- Python 3.11+
- Bedrock access enabled

### 2. Build

```bash
cd backend-aws
sam build
```

This will:
- Install dependencies
- Package Lambda functions
- Create deployment artifacts

### 3. Deploy

```bash
sam deploy --guided
```

Answer prompts:
- **Stack name**: `c4-diagram-generator`
- **Region**: `us-east-1` (or your preferred region)
- **Parameter Environment**: `dev` (or `staging`, `prod`)
- **Parameter BedrockRegion**: `us-east-1`
- **Parameter EnableDynamoDB**: `true` (or `false`)
- **Confirm changes**: `Y`
- **Allow IAM role creation**: `Y`
- **Save arguments**: `Y`

### 4. Verify Deployment

```bash
# Get API endpoint
export API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Test health
curl $API_ENDPOINT/api/diagrams/validate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Build a web application where users can upload files"}'
```

## Environment-Specific Deployments

### Development
```bash
sam deploy --parameter-overrides Environment=dev
```

### Staging
```bash
sam deploy \
  --parameter-overrides Environment=staging \
  --config-env staging
```

### Production
```bash
sam deploy \
  --parameter-overrides Environment=prod \
  --config-env prod
```

## Update Deployment

```bash
# Make code changes
# ...

# Build and deploy
sam build && sam deploy
```

## Rollback

```bash
# List stack events
aws cloudformation describe-stack-events \
  --stack-name c4-diagram-generator

# Rollback to previous version
aws cloudformation cancel-update-stack \
  --stack-name c4-diagram-generator
```

## Delete Stack

```bash
sam delete --stack-name c4-diagram-generator
```

## Monitoring

### View Logs
```bash
# All functions
sam logs --tail

# Specific function
sam logs -n GenerateFunction --tail

# Filter by time
sam logs -n GenerateFunction --start-time '10min ago'
```

### CloudWatch Dashboard
```bash
# Open CloudWatch console
aws cloudwatch get-dashboard \
  --dashboard-name c4-diagram-generator
```

## Cost Optimization

### Enable X-Ray Tracing
Already enabled in template.yaml for performance monitoring

### Set Up Alarms
```bash
# Create alarm for errors
aws cloudwatch put-metric-alarm \
  --alarm-name c4-generator-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## Troubleshooting

### Build Fails
```bash
# Clean and rebuild
sam build --use-container
```

### Deploy Fails
```bash
# Check IAM permissions
aws sts get-caller-identity

# Validate template
sam validate
```

### Function Errors
```bash
# View recent logs
sam logs -n GenerateFunction --tail

# Invoke locally
sam local invoke GenerateFunction -e events/generate.json
```

## Next Steps

1. Set up CI/CD pipeline
2. Configure custom domain
3. Add WAF rules
4. Enable API caching
5. Set up monitoring dashboards
