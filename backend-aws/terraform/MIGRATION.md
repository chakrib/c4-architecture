# Migration Guide: SAM/CloudFormation to Terraform

This guide helps you migrate from AWS SAM (CloudFormation) to Terraform for the C4 Diagram Generator backend.

## Why Migrate to Terraform?

### Advantages of Terraform

1. **Multi-Cloud Support**: Terraform works with AWS, Azure, GCP, and 100+ providers
2. **Better State Management**: More flexible state backends (S3, Terraform Cloud, etc.)
3. **Mature Ecosystem**: Larger community, more modules, better tooling
4. **Declarative Syntax**: HCL is more readable than CloudFormation YAML
5. **Plan Before Apply**: See exactly what will change before applying
6. **Modular Design**: Easier to reuse and share infrastructure code
7. **Industry Standard**: More widely adopted in enterprise environments

### When to Use SAM vs Terraform

**Use SAM if:**
- You're AWS-only and don't plan to use other clouds
- You want tight integration with AWS serverless services
- You prefer AWS-native tooling
- Your team is already familiar with CloudFormation

**Use Terraform if:**
- You want multi-cloud or cloud-agnostic infrastructure
- You need better state management and collaboration
- You want more flexible and modular infrastructure code
- Your team prefers Terraform's workflow and tooling

## Migration Steps

### Step 1: Backup Current Deployment

Before migrating, document your current SAM deployment:

```bash
# Get current stack outputs
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs' \
  --output json > sam-outputs.json

# Get current API endpoint
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

Save this information for comparison after Terraform deployment.

### Step 2: Review Terraform Configuration

Compare the SAM template with Terraform configuration:

| SAM Resource | Terraform Resource | File |
|--------------|-------------------|------|
| `AWS::Serverless::Api` | `aws_api_gateway_rest_api` | `api_gateway.tf` |
| `AWS::Serverless::Function` | `aws_lambda_function` | `lambda.tf` |
| `AWS::Serverless::LayerVersion` | `aws_lambda_layer_version` | `lambda.tf` |
| `AWS::DynamoDB::Table` | `aws_dynamodb_table` | `dynamodb.tf` |
| `AWS::Logs::LogGroup` | `aws_cloudwatch_log_group` | `lambda.tf` |

### Step 3: Prepare Terraform Environment

```bash
# Navigate to terraform directory
cd backend-aws/terraform

# Copy and customize variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings

# Or use environment-specific files
# dev.tfvars and prod.tfvars are already configured
```

### Step 4: Build Lambda Layer

```bash
# Build the Lambda layer
./scripts/build-layer.sh
```

This creates `../layers/common.zip` with all dependencies.

### Step 5: Initialize Terraform

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate
```

### Step 6: Plan Deployment

```bash
# Plan for dev environment
terraform plan -var-file=dev.tfvars

# Review the plan carefully
# Ensure all resources will be created as expected
```

### Step 7: Delete SAM Stack (Optional)

**Option A: Clean Migration (Recommended)**

Delete the SAM stack before deploying with Terraform:

```bash
# Delete SAM stack
sam delete --stack-name c4-diagram-generator

# Or use CloudFormation CLI
aws cloudformation delete-stack --stack-name c4-diagram-generator

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name c4-diagram-generator
```

**Option B: Import Existing Resources**

If you want to import existing resources into Terraform (advanced):

```bash
# Import API Gateway
terraform import aws_api_gateway_rest_api.main <api-id>

# Import Lambda functions
terraform import aws_lambda_function.validate <function-name>

# Import DynamoDB table
terraform import aws_dynamodb_table.diagram_history[0] <table-name>

# ... repeat for all resources
```

**Note**: Importing is complex and error-prone. Clean migration is recommended.

### Step 8: Deploy with Terraform

```bash
# Deploy to dev environment
terraform apply -var-file=dev.tfvars

# Or use the deployment script
./scripts/deploy.sh -e dev
```

### Step 9: Verify Deployment

```bash
# Get API endpoint
API_ENDPOINT=$(terraform output -raw api_endpoint)
echo "API Endpoint: $API_ENDPOINT"

# Test validation endpoint
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'

# Test generation endpoint
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web application with user authentication, database storage, and REST API"}'
```

### Step 10: Update Frontend Configuration

Update your frontend to use the new API endpoint:

```bash
# Get the new endpoint
terraform output api_endpoint

# Update frontend/.env
# VITE_API_BASE_URL=<new-api-endpoint>
```

### Step 11: Test All Endpoints

Test all four endpoints:

1. **Validate**: `/api/diagrams/validate`
2. **Suggest**: `/api/diagrams/suggest-improvements`
3. **Generate**: `/api/diagrams/generate`
4. **Refine**: `/api/diagrams/refine`

### Step 12: Monitor CloudWatch Logs

```bash
# Get function names
terraform output validate_function_name
terraform output generate_function_name

# Tail logs
aws logs tail /aws/lambda/$(terraform output -raw validate_function_name) --follow
```

## Configuration Comparison

### SAM Parameters vs Terraform Variables

| SAM Parameter | Terraform Variable | Default |
|---------------|-------------------|---------|
| `Environment` | `environment` | `dev` |
| `BedrockRegion` | `bedrock_region` | `us-east-1` |
| `EnableDynamoDB` | `enable_dynamodb` | `true` |
| N/A | `lambda_timeout` | `30` |
| N/A | `lambda_memory_size` | `512` |
| N/A | `log_retention_days` | `7` |

### SAM Globals vs Terraform Defaults

SAM uses `Globals` section for common Lambda settings. In Terraform, these are defined as variables with defaults.

**SAM:**
```yaml
Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.11
```

**Terraform:**
```hcl
variable "lambda_timeout" {
  default = 30
}

variable "lambda_memory_size" {
  default = 512
}

# Applied to each function
resource "aws_lambda_function" "validate" {
  timeout     = var.lambda_timeout
  memory_size = var.lambda_memory_size
  runtime     = "python3.11"
}
```

## Key Differences

### 1. Resource Naming

**SAM**: Uses logical IDs and CloudFormation generates physical names
```yaml
ValidateFunction:
  Type: AWS::Serverless::Function
```

**Terraform**: Explicit naming with interpolation
```hcl
resource "aws_lambda_function" "validate" {
  function_name = "${var.project_name}-validate-${var.environment}"
}
```

### 2. API Gateway Integration

**SAM**: Implicit API Gateway creation via `Events`
```yaml
Events:
  ValidateApi:
    Type: Api
    Properties:
      Path: /api/diagrams/validate
      Method: POST
```

**Terraform**: Explicit resource creation
```hcl
resource "aws_api_gateway_resource" "validate" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.diagrams.id
  path_part   = "validate"
}

resource "aws_api_gateway_method" "validate_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.validate.id
  http_method   = "POST"
  authorization = "NONE"
}
```

### 3. CORS Configuration

**SAM**: Simple CORS configuration
```yaml
Cors:
  AllowMethods: "'GET,POST,OPTIONS'"
  AllowHeaders: "'Content-Type,Authorization'"
  AllowOrigin: "'*'"
```

**Terraform**: Explicit OPTIONS method and integration
```hcl
module "cors_validate" {
  source = "./modules/cors"
  
  api_id          = aws_api_gateway_rest_api.main.id
  api_resource_id = aws_api_gateway_resource.validate.id
  allowed_origins = var.cors_allowed_origins
}
```

### 4. Conditional Resources

**SAM**: Uses CloudFormation conditions
```yaml
Conditions:
  UseDynamoDB: !Equals [!Ref EnableDynamoDB, 'true']

Resources:
  DiagramHistoryTable:
    Type: AWS::DynamoDB::Table
    Condition: UseDynamoDB
```

**Terraform**: Uses count or for_each
```hcl
resource "aws_dynamodb_table" "diagram_history" {
  count = var.enable_dynamodb ? 1 : 0
  
  name = "${var.project_name}-diagram-history-${var.environment}"
  # ...
}
```

### 5. Outputs

**SAM**: CloudFormation outputs with exports
```yaml
Outputs:
  ApiEndpoint:
    Value: !Sub 'https://${C4DiagramApi}.execute-api.${AWS::Region}.amazonaws.com/${Environment}'
    Export:
      Name: !Sub '${AWS::StackName}-ApiEndpoint'
```

**Terraform**: Simple output values
```hcl
output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_api_gateway_stage.main.invoke_url
}
```

## State Management

### SAM/CloudFormation State

- Managed by AWS CloudFormation service
- Stored in AWS (not visible to users)
- Stack-based (all resources in one stack)

### Terraform State

- Stored locally by default (`terraform.tfstate`)
- Can be stored remotely (S3, Terraform Cloud, etc.)
- More flexible state management

**Recommended: Remote State with S3**

```hcl
# Add to main.tf
terraform {
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "c4-diagram-generator/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

## Rollback Strategy

If you need to rollback to SAM:

1. **Destroy Terraform resources**:
   ```bash
   terraform destroy -var-file=dev.tfvars
   ```

2. **Redeploy with SAM**:
   ```bash
   cd backend-aws
   sam build
   sam deploy --guided
   ```

3. **Update frontend** with SAM API endpoint

## Cost Comparison

Both SAM and Terraform deploy the same AWS resources, so costs are identical:

- API Gateway: ~$3.50/million requests
- Lambda: ~$0.20/million requests
- DynamoDB: ~$1.25/million writes
- CloudWatch: ~$0.50/GB

**No cost difference between SAM and Terraform deployments.**

## Troubleshooting

### Issue: Terraform can't find Lambda layer zip

**Solution**: Build the layer first
```bash
./scripts/build-layer.sh
```

### Issue: API Gateway deployment not updating

**Solution**: Terraform tracks deployment changes via SHA1 hash. If changes aren't detected:
```bash
terraform taint aws_api_gateway_deployment.main
terraform apply -var-file=dev.tfvars
```

### Issue: Lambda function not updating

**Solution**: Terraform uses source code hash. Ensure code changed:
```bash
# Check current hash
terraform state show aws_lambda_function.validate | grep source_code_hash

# Force update
terraform taint aws_lambda_function.validate
terraform apply -var-file=dev.tfvars
```

### Issue: DynamoDB table already exists

**Solution**: Import existing table or delete it first
```bash
# Option 1: Import
terraform import 'aws_dynamodb_table.diagram_history[0]' existing-table-name

# Option 2: Delete (WARNING: loses data)
aws dynamodb delete-table --table-name existing-table-name
```

## Best Practices

1. **Use Remote State**: Store Terraform state in S3 with DynamoDB locking
2. **Use Workspaces**: Separate dev/staging/prod environments
3. **Version Control**: Commit all `.tf` files, exclude `.tfstate` and `.tfvars`
4. **Plan Before Apply**: Always run `terraform plan` first
5. **Use Variables**: Parameterize everything for reusability
6. **Tag Resources**: Use consistent tagging for cost tracking
7. **Enable Logging**: Keep CloudWatch logs for debugging
8. **Backup State**: Regularly backup `terraform.tfstate`

## Next Steps

After successful migration:

1. **Set up CI/CD**: Automate Terraform deployments
2. **Configure Remote State**: Use S3 backend for team collaboration
3. **Add Monitoring**: Set up CloudWatch alarms and dashboards
4. **Implement Security**: Add WAF, API keys, and VPC configuration
5. **Document Changes**: Update team documentation with new workflow

## Support

For migration issues:
1. Check Terraform plan output carefully
2. Review CloudWatch logs for Lambda errors
3. Compare SAM and Terraform resource configurations
4. Test each endpoint after migration

## References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
