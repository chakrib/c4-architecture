# Terraform Infrastructure - Complete Summary

## Overview

The C4 Diagram Generator backend has been converted from AWS SAM (CloudFormation) to Terraform, providing a more flexible and industry-standard infrastructure-as-code solution.

## What Was Created

### Directory Structure

```
backend-aws/terraform/
├── main.tf                    # Provider configuration and data sources
├── variables.tf               # Input variables with validation
├── outputs.tf                 # Output values (API endpoint, ARNs, etc.)
├── lambda.tf                  # Lambda functions, layer, IAM roles
├── api_gateway.tf            # API Gateway REST API configuration
├── dynamodb.tf               # DynamoDB table (optional)
├── dev.tfvars                # Development environment variables
├── prod.tfvars               # Production environment variables
├── terraform.tfvars.example  # Example variables file
├── .gitignore                # Terraform-specific gitignore
├── README.md                 # Comprehensive documentation
├── MIGRATION.md              # SAM to Terraform migration guide
├── modules/
│   └── cors/                 # Reusable CORS module
│       └── main.tf
└── scripts/
    ├── build-layer.sh        # Build Lambda layer script
    └── deploy.sh             # Complete deployment script
```

## Key Features

### 1. Complete Infrastructure Definition

All AWS resources defined in Terraform:
- ✅ API Gateway REST API with 4 endpoints
- ✅ 4 Lambda functions (validate, suggest, generate, refine)
- ✅ Lambda layer with shared dependencies
- ✅ DynamoDB table (optional, controlled by variable)
- ✅ CloudWatch log groups for all functions
- ✅ IAM roles and policies
- ✅ CORS configuration via reusable module
- ✅ X-Ray tracing enabled

### 2. Environment Management

Multiple ways to manage environments:

**Option 1: Variable Files**
```bash
terraform apply -var-file=dev.tfvars
terraform apply -var-file=prod.tfvars
```

**Option 2: Workspaces**
```bash
terraform workspace new dev
terraform workspace new prod
terraform workspace select dev
```

**Option 3: Custom tfvars**
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform apply
```

### 3. Automated Deployment

Two deployment methods:

**Method 1: Manual Steps**
```bash
cd backend-aws/terraform
./scripts/build-layer.sh
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

**Method 2: Automated Script**
```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
./scripts/deploy.sh -e prod -y  # Auto-approve
```

### 4. Modular Design

Reusable CORS module:
```hcl
module "cors_validate" {
  source = "./modules/cors"
  
  api_id          = aws_api_gateway_rest_api.main.id
  api_resource_id = aws_api_gateway_resource.validate.id
  allowed_origins = var.cors_allowed_origins
}
```

Can be extended with more modules (monitoring, security, etc.)

## Configuration Variables

### Core Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_region` | string | `us-east-1` | AWS region for resources |
| `environment` | string | `dev` | Environment (dev/staging/prod) |
| `bedrock_region` | string | `us-east-1` | Bedrock service region |
| `enable_dynamodb` | bool | `true` | Enable DynamoDB table |
| `lambda_timeout` | number | `30` | Lambda timeout (seconds) |
| `lambda_memory_size` | number | `512` | Lambda memory (MB) |
| `log_retention_days` | number | `7` | CloudWatch log retention |
| `project_name` | string | `c4-diagram-generator` | Project name prefix |
| `cors_allowed_origins` | list(string) | `["*"]` | CORS allowed origins |

### Environment-Specific Configurations

**Development (dev.tfvars)**
- Lower memory (512MB)
- Shorter timeout (30s)
- Short log retention (7 days)
- Open CORS (`*`)

**Production (prod.tfvars)**
- Higher memory (1024MB)
- Longer timeout (60s)
- Longer log retention (30 days)
- Restricted CORS (specific domains)

## Outputs

After deployment, Terraform provides:

```bash
# Get all outputs
terraform output

# Specific outputs
terraform output api_endpoint           # https://xxx.execute-api.us-east-1.amazonaws.com/dev
terraform output validate_function_name # c4-diagram-generator-validate-dev
terraform output dynamodb_table_name    # c4-diagram-generator-diagram-history-dev
terraform output region                 # us-east-1
terraform output account_id             # 123456789012
```

## Deployment Workflow

### Initial Deployment

```bash
# 1. Navigate to terraform directory
cd backend-aws/terraform

# 2. Build Lambda layer
./scripts/build-layer.sh

# 3. Initialize Terraform
terraform init

# 4. Review plan
terraform plan -var-file=dev.tfvars

# 5. Deploy
terraform apply -var-file=dev.tfvars

# 6. Get API endpoint
terraform output api_endpoint
```

### Update Deployment

```bash
# 1. Make code changes to Lambda functions

# 2. Rebuild layer if dependencies changed
./scripts/build-layer.sh

# 3. Apply changes (Terraform auto-detects code changes)
terraform apply -var-file=dev.tfvars
```

### Destroy Resources

```bash
terraform destroy -var-file=dev.tfvars
```

## Testing the Deployment

### Quick Test

```bash
# Get API endpoint
API_ENDPOINT=$(terraform output -raw api_endpoint)

# Test validation
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'
```

### Complete Test Suite

```bash
# 1. Validate endpoint
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'

# 2. Suggest endpoint
curl -X POST "${API_ENDPOINT}/api/diagrams/suggest-improvements" \
  -H "Content-Type: application/json" \
  -d '{"description": "web app"}'

# 3. Generate endpoint
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'

# 4. Refine endpoint
curl -X POST "${API_ENDPOINT}/api/diagrams/refine" \
  -H "Content-Type: application/json" \
  -d '{"current_diagram": "...", "refinement_request": "Add a cache layer"}'
```

## Advantages Over SAM

### 1. Multi-Cloud Support
- Terraform works with AWS, Azure, GCP, and 100+ providers
- SAM is AWS-only

### 2. Better State Management
- Flexible state backends (S3, Terraform Cloud, etc.)
- Team collaboration with state locking
- SAM state is opaque (managed by CloudFormation)

### 3. Mature Ecosystem
- Larger community and more resources
- More modules and examples
- Better IDE support and tooling

### 4. Declarative Syntax
- HCL is more readable than CloudFormation YAML
- Better variable interpolation
- Cleaner conditional logic

### 5. Plan Before Apply
- See exactly what will change before applying
- Prevents accidental resource deletion
- Better for production deployments

### 6. Modular Design
- Easy to create reusable modules
- Better code organization
- Easier to share infrastructure patterns

## Migration from SAM

If you previously used SAM, follow these steps:

### 1. Delete SAM Stack

```bash
sam delete --stack-name c4-diagram-generator
```

### 2. Deploy with Terraform

```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
```

### 3. Update Frontend

```bash
# Get new API endpoint
terraform output api_endpoint

# Update frontend/.env
# VITE_API_BASE_URL=<new-endpoint>
```

See `MIGRATION.md` for detailed migration guide.

## Cost Comparison

**No cost difference between SAM and Terraform!**

Both deploy the same AWS resources:
- API Gateway: ~$3.50/million requests
- Lambda: ~$0.20/million requests (512MB, 30s avg)
- DynamoDB: ~$1.25/million writes (on-demand)
- CloudWatch: ~$0.50/GB

**Estimated costs:**
- Development: $5-10/month (low traffic)
- Production: $20-50/month (moderate traffic)

## Security Features

### Built-in Security

1. **IAM Least Privilege**: Lambda roles have minimal permissions
2. **CORS Configuration**: Configurable allowed origins
3. **X-Ray Tracing**: Enabled for debugging and monitoring
4. **CloudWatch Logs**: All functions log to CloudWatch
5. **Encryption**: DynamoDB encryption at rest enabled

### Production Hardening

For production, consider adding:

1. **API Gateway API Key**
   ```hcl
   resource "aws_api_gateway_api_key" "main" {
     name = "${var.project_name}-api-key-${var.environment}"
   }
   ```

2. **AWS WAF** for DDoS protection
3. **VPC Configuration** for Lambda functions
4. **Secrets Manager** for sensitive data
5. **Custom Domain** with ACM certificate

## Monitoring and Logging

### CloudWatch Logs

```bash
# Tail logs for a function
aws logs tail /aws/lambda/$(terraform output -raw validate_function_name) --follow

# View logs in AWS Console
# CloudWatch → Log groups → /aws/lambda/<function-name>
```

### X-Ray Tracing

- Enabled on all Lambda functions
- View traces in AWS X-Ray console
- Helps debug performance issues

### Future Enhancements

Add CloudWatch alarms:
```hcl
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1
      
      - name: Build Lambda layer
        run: cd backend-aws/terraform && ./scripts/build-layer.sh
      
      - name: Terraform Init
        run: cd backend-aws/terraform && terraform init
      
      - name: Terraform Plan
        run: cd backend-aws/terraform && terraform plan -var-file=prod.tfvars
      
      - name: Terraform Apply
        run: cd backend-aws/terraform && terraform apply -var-file=prod.tfvars -auto-approve
```

## Troubleshooting

### Common Issues

**Issue**: Lambda layer not found
```bash
# Solution: Build the layer
./scripts/build-layer.sh
```

**Issue**: Bedrock access denied
```bash
# Solution: Enable Bedrock model access in AWS Console
# AWS Console → Bedrock → Model access → Request access to Claude 3 Haiku
```

**Issue**: API Gateway not updating
```bash
# Solution: Force redeployment
terraform taint aws_api_gateway_deployment.main
terraform apply -var-file=dev.tfvars
```

**Issue**: Lambda function not updating
```bash
# Solution: Terraform uses source code hash
# Ensure code actually changed, or force update:
terraform taint aws_lambda_function.validate
terraform apply -var-file=dev.tfvars
```

## Best Practices

1. ✅ **Use Remote State**: Store state in S3 with DynamoDB locking
2. ✅ **Use Workspaces**: Separate dev/staging/prod environments
3. ✅ **Version Control**: Commit `.tf` files, exclude `.tfstate` and `.tfvars`
4. ✅ **Plan Before Apply**: Always review changes before applying
5. ✅ **Use Variables**: Parameterize everything for reusability
6. ✅ **Tag Resources**: Consistent tagging for cost tracking
7. ✅ **Enable Logging**: Keep CloudWatch logs for debugging
8. ✅ **Backup State**: Regularly backup `terraform.tfstate`
9. ✅ **Use Modules**: Create reusable infrastructure patterns
10. ✅ **Document Changes**: Keep README and docs up to date

## Next Steps

### Immediate

1. ✅ Deploy to dev environment
2. ✅ Test all endpoints
3. ✅ Update frontend with new API endpoint
4. ✅ Monitor CloudWatch logs

### Short-term

1. Set up remote state backend (S3)
2. Configure production environment
3. Add CloudWatch alarms
4. Implement API Gateway API key

### Long-term

1. Set up CI/CD pipeline
2. Add AWS WAF for security
3. Implement custom domain
4. Add monitoring dashboard
5. Configure VPC for Lambda functions

## Documentation

- **README.md**: Complete usage guide
- **MIGRATION.md**: SAM to Terraform migration guide
- **terraform.tfvars.example**: Example configuration
- **dev.tfvars**: Development environment config
- **prod.tfvars**: Production environment config

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review `MIGRATION.md` for migration-specific issues
3. Check CloudWatch logs for Lambda errors
4. Verify AWS Bedrock access in AWS Console
5. Review Terraform plan output carefully

## Summary

The Terraform infrastructure provides:
- ✅ Complete AWS resource definitions
- ✅ Environment-specific configurations
- ✅ Automated deployment scripts
- ✅ Modular and reusable design
- ✅ Comprehensive documentation
- ✅ Production-ready security
- ✅ Cost-effective architecture
- ✅ Easy migration from SAM

**Ready to deploy!** Use `./scripts/deploy.sh -e dev` to get started.
