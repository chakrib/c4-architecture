# Quick Deploy Guide

Choose your deployment method and follow the steps below.

## Prerequisites (Both Methods)

1. **AWS CLI** configured with credentials
   ```bash
   aws configure
   ```

2. **AWS Bedrock Access** - Enable Claude 3 Haiku in AWS Console
   - Go to: AWS Console → Bedrock → Model access
   - Request access to Claude 3 Haiku

3. **Python 3.11+** installed
   ```bash
   python3 --version
   ```

## Option 1: SAM/CloudFormation (Fastest)

**Time: 5 minutes**

### Install SAM CLI

```bash
# macOS
brew install aws-sam-cli

# Or follow: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
```

### Deploy

```bash
cd backend-aws

# Build
sam build

# Deploy (first time - interactive)
sam deploy --guided

# Deploy (subsequent times)
sam deploy
```

### Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

### Test

```bash
API_ENDPOINT="<your-endpoint-from-above>"

curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'
```

### Delete (if needed)

```bash
sam delete
```

---

## Option 2: Terraform (Recommended for Production)

**Time: 10 minutes**

### Install Terraform

```bash
# macOS
brew install terraform

# Or download from: https://www.terraform.io/downloads
```

### Deploy

```bash
cd backend-aws/terraform

# Build Lambda layer
./scripts/build-layer.sh

# Deploy to dev (interactive)
./scripts/deploy.sh -e dev

# Or deploy to prod
./scripts/deploy.sh -e prod

# Or deploy with auto-approve
./scripts/deploy.sh -e dev -y
```

### Get API Endpoint

```bash
terraform output api_endpoint
```

### Test

```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)

curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'
```

### Delete (if needed)

```bash
terraform destroy -var-file=dev.tfvars
```

---

## Update Frontend

After deployment, update your frontend configuration:

```bash
# Get API endpoint (SAM)
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text

# Or get API endpoint (Terraform)
cd backend-aws/terraform
terraform output api_endpoint

# Update frontend/.env
cd ../../frontend
echo "VITE_API_BASE_URL=<your-api-endpoint>" > .env

# Restart frontend
npm run dev
```

---

## Complete Test Suite

Test all four endpoints:

```bash
# Set API endpoint
API_ENDPOINT="<your-endpoint>"

# 1. Validate
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with authentication and database"}'

# 2. Suggest
curl -X POST "${API_ENDPOINT}/api/diagrams/suggest-improvements" \
  -H "Content-Type: application/json" \
  -d '{"description": "web app"}'

# 3. Generate
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with authentication and database"}'

# 4. Refine
curl -X POST "${API_ENDPOINT}/api/diagrams/refine" \
  -H "Content-Type: application/json" \
  -d '{
    "current_diagram": "@startuml\n!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\nPerson(user, \"User\")\nSystem(webapp, \"Web App\")\nRel(user, webapp, \"Uses\")\n@enduml",
    "refinement_request": "Add a database"
  }'
```

---

## Troubleshooting

### Bedrock Access Denied

**Problem**: Lambda returns "Access Denied" for Bedrock

**Solution**:
1. Go to AWS Console → Bedrock → Model access
2. Request access to Claude 3 Haiku
3. Wait for approval (usually instant)
4. Redeploy

### Lambda Timeout

**Problem**: Lambda times out after 30 seconds

**Solution**:

**SAM**: Edit `template.yaml`
```yaml
Globals:
  Function:
    Timeout: 60  # Increase to 60 seconds
```

**Terraform**: Edit `terraform/variables.tf`
```hcl
variable "lambda_timeout" {
  default = 60  # Increase to 60 seconds
}
```

Then redeploy.

### CORS Errors

**Problem**: Frontend gets CORS errors

**Solution**: Verify CORS is enabled in API Gateway

**SAM**: Check `template.yaml`
```yaml
Cors:
  AllowOrigin: "'*'"
  AllowMethods: "'GET,POST,OPTIONS'"
  AllowHeaders: "'Content-Type,Authorization'"
```

**Terraform**: Check `terraform/variables.tf`
```hcl
cors_allowed_origins = ["*"]
```

### Cold Start Delays

**Problem**: First request takes 2-3 seconds

**Solution**: This is normal for Lambda cold starts. Subsequent requests will be faster (200-500ms).

To reduce cold starts:
- Use provisioned concurrency (costs more)
- Keep functions warm with scheduled pings
- Accept 1-2 second cold starts (acceptable for this use case)

---

## Monitoring

### View Logs

**SAM**:
```bash
sam logs --tail
sam logs -n GenerateFunction --tail
```

**Terraform**:
```bash
# Get function name
terraform output validate_function_name

# View logs
aws logs tail /aws/lambda/$(terraform output -raw validate_function_name) --follow
```

### CloudWatch Console

1. Go to AWS Console → CloudWatch → Log groups
2. Find `/aws/lambda/<function-name>`
3. View logs in real-time

---

## Cost Monitoring

### Set Up Budget Alert

```bash
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json
```

**budget.json**:
```json
{
  "BudgetName": "C4DiagramGenerator",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

### View Current Costs

```bash
# View costs for last 30 days
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

---

## Next Steps

After successful deployment:

1. ✅ Test all endpoints
2. ✅ Update frontend configuration
3. ✅ Set up CloudWatch alarms
4. ✅ Configure budget alerts
5. ✅ Add custom domain (optional)
6. ✅ Set up CI/CD (optional)

---

## Quick Reference

### SAM Commands

```bash
sam build                    # Build application
sam deploy                   # Deploy to AWS
sam deploy --guided          # Interactive deployment
sam logs --tail              # View logs
sam local start-api          # Test locally
sam delete                   # Delete stack
sam validate                 # Validate template
```

### Terraform Commands

```bash
terraform init               # Initialize
terraform plan               # Preview changes
terraform apply              # Deploy
terraform destroy            # Delete resources
terraform output             # View outputs
terraform validate           # Validate config
terraform fmt                # Format code
terraform state list         # List resources
```

---

## Support

### Documentation
- **SAM**: [GETTING-STARTED.md](GETTING-STARTED.md)
- **Terraform**: [terraform/README.md](terraform/README.md)
- **Comparison**: [SAM-VS-TERRAFORM.md](SAM-VS-TERRAFORM.md)

### Common Issues
1. Check CloudWatch logs first
2. Verify AWS credentials
3. Confirm Bedrock access
4. Review IAM permissions
5. Test locally (SAM only)

### Getting Help
- AWS SAM: https://docs.aws.amazon.com/serverless-application-model/
- Terraform: https://registry.terraform.io/providers/hashicorp/aws/
- AWS Bedrock: https://docs.aws.amazon.com/bedrock/

---

**Choose your deployment method and get started!** 🚀
