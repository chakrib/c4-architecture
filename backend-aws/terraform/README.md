# C4 Diagram Generator - Terraform Infrastructure

This directory contains Terraform configuration for deploying the C4 Diagram Generator serverless backend to AWS.

## Architecture

The infrastructure includes:
- **API Gateway**: REST API with CORS support
- **Lambda Functions**: 4 functions (validate, suggest, generate, refine)
- **Lambda Layer**: Shared Python dependencies
- **DynamoDB**: Optional table for diagram history
- **CloudWatch**: Log groups for all functions
- **IAM**: Roles and policies for Lambda execution

## Prerequisites

1. **Terraform**: Install Terraform >= 1.0
   ```bash
   # macOS
   brew install terraform
   
   # Or download from https://www.terraform.io/downloads
   ```

2. **AWS CLI**: Configure AWS credentials
   ```bash
   aws configure
   ```

3. **AWS Bedrock Access**: Ensure your AWS account has access to Bedrock in your region
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude 3 Haiku model

4. **Python 3.11**: Required for building Lambda layer
   ```bash
   python3 --version  # Should be 3.11+
   ```

## Project Structure

```
terraform/
├── main.tf                    # Provider and core configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── lambda.tf                  # Lambda functions and layer
├── api_gateway.tf            # API Gateway configuration
├── dynamodb.tf               # DynamoDB table (optional)
├── dev.tfvars                # Development environment vars
├── prod.tfvars               # Production environment vars
├── terraform.tfvars.example  # Example variables file
├── modules/
│   └── cors/                 # CORS module for API Gateway
│       └── main.tf
└── scripts/
    ├── build-layer.sh        # Build Lambda layer
    └── deploy.sh             # Complete deployment script
```

## Quick Start

### 1. Prepare Lambda Layer

First, build the Lambda layer with dependencies:

```bash
cd backend-aws/terraform
./scripts/build-layer.sh
```

This creates `../layers/common.zip` with all Python dependencies.

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review Configuration

Copy and customize the variables file:

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings
```

Or use environment-specific files:
- `dev.tfvars` - Development environment
- `prod.tfvars` - Production environment

### 4. Plan Deployment

```bash
# Using dev environment
terraform plan -var-file=dev.tfvars

# Or using custom tfvars
terraform plan
```

### 5. Deploy Infrastructure

```bash
# Deploy to dev
terraform apply -var-file=dev.tfvars

# Deploy to prod
terraform apply -var-file=prod.tfvars
```

### 6. Get API Endpoint

After deployment, Terraform outputs the API endpoint:

```bash
terraform output api_endpoint
```

Use this URL in your frontend configuration.

## Configuration Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region for resources | `us-east-1` |
| `environment` | Environment name (dev/staging/prod) | `dev` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `bedrock_region` | AWS region for Bedrock | `us-east-1` |
| `enable_dynamodb` | Enable DynamoDB for history | `true` |
| `lambda_timeout` | Lambda timeout in seconds | `30` |
| `lambda_memory_size` | Lambda memory in MB | `512` |
| `log_retention_days` | CloudWatch log retention | `7` |
| `project_name` | Project name for resources | `c4-diagram-generator` |
| `cors_allowed_origins` | CORS allowed origins | `["*"]` |

## Environment-Specific Deployments

### Development

```bash
terraform workspace new dev
terraform apply -var-file=dev.tfvars
```

### Production

```bash
terraform workspace new prod
terraform apply -var-file=prod.tfvars
```

## Updating Lambda Functions

When you update Lambda function code:

```bash
# Rebuild layer if dependencies changed
./scripts/build-layer.sh

# Apply changes
terraform apply -var-file=dev.tfvars
```

Terraform automatically detects code changes via SHA256 hashing.

## Outputs

After deployment, Terraform provides these outputs:

```bash
# Get all outputs
terraform output

# Get specific output
terraform output api_endpoint
terraform output validate_function_name
terraform output dynamodb_table_name
```

### Available Outputs

- `api_endpoint` - Full API Gateway URL
- `api_gateway_id` - API Gateway ID
- `dynamodb_table_name` - DynamoDB table name (if enabled)
- `validate_function_name` - Validate Lambda function name
- `suggest_function_name` - Suggest Lambda function name
- `generate_function_name` - Generate Lambda function name
- `refine_function_name` - Refine Lambda function name
- `lambda_layer_arn` - Common Lambda layer ARN
- `region` - Deployed AWS region
- `account_id` - AWS account ID

## Testing the Deployment

### 1. Test Validation Endpoint

```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)

curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'
```

### 2. Test Generation Endpoint

```bash
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'
```

## Cost Estimation

### Development Environment
- API Gateway: ~$3.50/million requests
- Lambda: ~$0.20/million requests (512MB, 30s avg)
- DynamoDB: ~$1.25/million writes (on-demand)
- CloudWatch Logs: ~$0.50/GB
- **Estimated**: $5-10/month for low traffic

### Production Environment
- Same pricing, scales with usage
- **Estimated**: $20-50/month for moderate traffic

## Troubleshooting

### Lambda Layer Build Fails

```bash
# Ensure Python 3.11 is installed
python3.11 --version

# Rebuild layer
cd backend-aws/terraform
./scripts/build-layer.sh
```

### Bedrock Access Denied

1. Go to AWS Console → Bedrock → Model access
2. Request access to Claude 3 Haiku
3. Wait for approval (usually instant)

### API Gateway CORS Issues

Update `cors_allowed_origins` in your tfvars file:

```hcl
cors_allowed_origins = ["https://yourdomain.com"]
```

Then reapply:

```bash
terraform apply -var-file=prod.tfvars
```

### Lambda Function Errors

Check CloudWatch logs:

```bash
# Get function name
terraform output validate_function_name

# View logs
aws logs tail /aws/lambda/c4-diagram-generator-validate-dev --follow
```

## Cleanup

To destroy all resources:

```bash
# Destroy dev environment
terraform destroy -var-file=dev.tfvars

# Destroy prod environment
terraform destroy -var-file=prod.tfvars
```

**Warning**: This will delete all resources including DynamoDB data.

## Migration from SAM/CloudFormation

If you previously deployed using SAM:

1. Delete the SAM stack:
   ```bash
   sam delete --stack-name c4-diagram-generator
   ```

2. Deploy with Terraform:
   ```bash
   terraform apply -var-file=dev.tfvars
   ```

3. Update frontend with new API endpoint:
   ```bash
   terraform output api_endpoint
   ```

## Security Best Practices

### Production Deployment

1. **CORS**: Restrict to specific origins
   ```hcl
   cors_allowed_origins = ["https://yourdomain.com"]
   ```

2. **API Key**: Add API Gateway API key (optional)
   ```hcl
   # Add to api_gateway.tf
   resource "aws_api_gateway_api_key" "main" {
     name = "${var.project_name}-api-key-${var.environment}"
   }
   ```

3. **WAF**: Add AWS WAF for DDoS protection
4. **VPC**: Deploy Lambda in VPC for private resources
5. **Secrets**: Use AWS Secrets Manager for sensitive data

## Advanced Configuration

### Custom Domain

Add a custom domain to API Gateway:

```hcl
resource "aws_api_gateway_domain_name" "main" {
  domain_name              = "api.yourdomain.com"
  regional_certificate_arn = aws_acm_certificate.main.arn
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
```

### VPC Configuration

Deploy Lambda in VPC:

```hcl
resource "aws_lambda_function" "validate" {
  # ... existing config ...
  
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda.id]
  }
}
```

### CloudWatch Alarms

Add monitoring:

```hcl
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Lambda function errors"
  
  dimensions = {
    FunctionName = aws_lambda_function.generate.function_name
  }
}
```

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review Terraform plan output
3. Verify AWS Bedrock access
4. Check IAM permissions

## License

Same as parent project.
