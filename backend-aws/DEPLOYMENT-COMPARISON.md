# Deployment Methods - Quick Comparison

## At a Glance

| Feature | SAM/CloudFormation | Terraform |
|---------|-------------------|-----------|
| **Setup Time** | 5 minutes | 10 minutes |
| **Commands** | 2 (`sam build`, `sam deploy`) | 3 (`build-layer.sh`, `terraform init`, `terraform apply`) |
| **Local Testing** | ✅ Excellent (`sam local`) | ❌ Limited |
| **Preview Changes** | ❌ No | ✅ Yes (`terraform plan`) |
| **Multi-Cloud** | ❌ AWS only | ✅ AWS, Azure, GCP, 100+ |
| **State Management** | AWS-managed (opaque) | Flexible (S3, local, cloud) |
| **Modularity** | Limited | ✅ Excellent |
| **Community** | AWS-focused | ✅ Large multi-cloud |
| **Learning Curve** | Easy | Moderate |
| **Production Ready** | ✅ Yes | ✅ Yes |
| **Cost** | Free | Free |
| **Deployed Resources** | Identical | Identical |
| **Monthly Cost** | $5-50 | $5-50 |

## Command Comparison

### Initial Deployment

**SAM**:
```bash
cd backend-aws
sam build
sam deploy --guided
```

**Terraform**:
```bash
cd backend-aws/terraform
./scripts/build-layer.sh
terraform init
terraform plan -var-file=dev.tfvars
terraform apply -var-file=dev.tfvars
```

### Update Deployment

**SAM**:
```bash
sam build
sam deploy
```

**Terraform**:
```bash
./scripts/build-layer.sh  # Only if dependencies changed
terraform apply -var-file=dev.tfvars
```

### Get API Endpoint

**SAM**:
```bash
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

**Terraform**:
```bash
terraform output api_endpoint
```

### View Logs

**SAM**:
```bash
sam logs --tail
sam logs -n GenerateFunction --tail
```

**Terraform**:
```bash
aws logs tail /aws/lambda/$(terraform output -raw validate_function_name) --follow
```

### Delete Resources

**SAM**:
```bash
sam delete
```

**Terraform**:
```bash
terraform destroy -var-file=dev.tfvars
```

## File Structure Comparison

### SAM

```
backend-aws/
├── template.yaml          # All infrastructure
├── samconfig.toml         # SAM configuration
└── functions/             # Lambda code
    ├── validate/
    ├── suggest/
    ├── generate/
    └── refine/
```

**Total: 2 config files**

### Terraform

```
backend-aws/terraform/
├── main.tf               # Provider config
├── variables.tf          # Input variables
├── outputs.tf            # Output values
├── lambda.tf             # Lambda resources
├── api_gateway.tf        # API Gateway
├── dynamodb.tf           # DynamoDB
├── dev.tfvars            # Dev environment
├── prod.tfvars           # Prod environment
├── modules/              # Reusable modules
│   └── cors/
└── scripts/              # Deployment scripts
    ├── build-layer.sh
    └── deploy.sh
```

**Total: 9+ config files**

## Syntax Comparison

### Lambda Function

**SAM (YAML)**:
```yaml
ValidateFunction:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: functions/validate/
    Handler: app.lambda_handler
    Runtime: python3.11
    Timeout: 30
    MemorySize: 512
    Events:
      ValidateApi:
        Type: Api
        Properties:
          Path: /api/diagrams/validate
          Method: POST
```

**Terraform (HCL)**:
```hcl
resource "aws_lambda_function" "validate" {
  filename         = data.archive_file.validate_function.output_path
  function_name    = "${var.project_name}-validate-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.validate_function.output_base64sha256
  runtime         = "python3.11"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
}
```

**Analysis**:
- SAM: More concise, implicit API Gateway
- Terraform: More explicit, better variable support

## Environment Management

### SAM

**Option 1: Parameters**
```bash
sam deploy --parameter-overrides Environment=dev
sam deploy --parameter-overrides Environment=prod
```

**Option 2: Config Files**
```bash
sam deploy --config-file samconfig-dev.toml
sam deploy --config-file samconfig-prod.toml
```

### Terraform

**Option 1: Variable Files** (Recommended)
```bash
terraform apply -var-file=dev.tfvars
terraform apply -var-file=prod.tfvars
```

**Option 2: Workspaces**
```bash
terraform workspace new dev
terraform workspace select dev
terraform apply
```

**Option 3: Separate Directories**
```bash
cd environments/dev && terraform apply
cd environments/prod && terraform apply
```

## State Management

### SAM/CloudFormation

**Storage**: AWS CloudFormation service
**Visibility**: Opaque (can't inspect directly)
**Locking**: Automatic (AWS-managed)
**Collaboration**: Good for single team
**Backup**: Automatic (AWS-managed)

**Pros**:
- ✅ No state file to manage
- ✅ AWS handles everything
- ✅ Automatic backups

**Cons**:
- ❌ Can't inspect state
- ❌ Limited manipulation
- ❌ Harder to share across teams

### Terraform

**Storage**: Local by default, can use S3/Terraform Cloud
**Visibility**: Transparent (can inspect)
**Locking**: Optional (DynamoDB for S3 backend)
**Collaboration**: Excellent with remote backend
**Backup**: Manual or automated

**Pros**:
- ✅ Transparent state
- ✅ Flexible backends
- ✅ Better team collaboration
- ✅ State manipulation commands

**Cons**:
- ❌ Must manage state file
- ❌ Need to set up remote backend
- ❌ State locking requires setup

## Local Testing

### SAM

```bash
# Start API locally
sam local start-api

# Invoke function locally
sam local invoke ValidateFunction -e events/validate.json

# Generate test events
sam local generate-event apigateway aws-proxy
```

**Winner: SAM** - Excellent local testing

### Terraform

```bash
# No built-in local testing
# Must use mocking frameworks or deploy to AWS
```

**Winner: SAM** - Terraform lacks local Lambda testing

## Preview Changes

### SAM

```bash
# No preview capability
# Must deploy to see changes
sam deploy
```

**Winner: Terraform** - SAM has no preview

### Terraform

```bash
# Preview changes before applying
terraform plan -var-file=dev.tfvars

# Shows:
# + Resources to create
# ~ Resources to modify
# - Resources to delete
```

**Winner: Terraform** - Excellent preview capability

## Cost Breakdown

Both deploy **identical AWS resources**, so costs are **identical**:

| Service | Cost | Notes |
|---------|------|-------|
| **API Gateway** | $3.50/million requests | REST API |
| **Lambda** | $0.20/million requests | 512MB, 30s avg |
| **Bedrock** | $0.25/million tokens | Claude 3 Haiku |
| **DynamoDB** | $1.25/million writes | On-demand |
| **CloudWatch** | $0.50/GB | Logs |

**Estimated Monthly Costs**:
- Low traffic (10K requests): $5-10
- Medium traffic (100K requests): $20-30
- High traffic (1M requests): $50-100

**No cost difference between SAM and Terraform!**

## Use Case Recommendations

### Use SAM if:

✅ **Scenario 1: Quick Prototype**
- Need to deploy fast
- Testing serverless architecture
- Don't need multi-cloud

✅ **Scenario 2: AWS-Only Project**
- Committed to AWS
- No plans for other clouds
- Want AWS-native tooling

✅ **Scenario 3: Local Testing Important**
- Need to test Lambda locally
- Frequent local development
- Want `sam local` capabilities

✅ **Scenario 4: Small Team**
- Single team project
- Simple state management needs
- AWS-focused developers

### Use Terraform if:

✅ **Scenario 1: Enterprise Environment**
- Need industry-standard IaC
- Better state management required
- Team collaboration important

✅ **Scenario 2: Multi-Cloud Strategy**
- Using multiple cloud providers
- Want cloud-agnostic IaC
- Future-proofing infrastructure

✅ **Scenario 3: Complex Infrastructure**
- Need modular design
- Want reusable components
- Scaling infrastructure

✅ **Scenario 4: Production Deployment**
- Need preview before deploy
- Want better change management
- Require audit trail

✅ **Scenario 5: Team Expertise**
- Team knows Terraform
- Want transferable skills
- Industry-standard tooling

## Migration Path

### From SAM to Terraform

**Time: 30 minutes**

```bash
# 1. Delete SAM stack
sam delete --stack-name c4-diagram-generator

# 2. Deploy with Terraform
cd backend-aws/terraform
./scripts/deploy.sh -e dev

# 3. Update frontend
terraform output api_endpoint
# Update frontend/.env
```

### From Terraform to SAM

**Time: 30 minutes**

```bash
# 1. Destroy Terraform resources
terraform destroy -var-file=dev.tfvars

# 2. Deploy with SAM
cd backend-aws
sam build
sam deploy --guided

# 3. Update frontend
aws cloudformation describe-stacks \
  --stack-name c4-diagram-generator \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
# Update frontend/.env
```

## Decision Matrix

| Criteria | Weight | SAM Score | Terraform Score | Winner |
|----------|--------|-----------|-----------------|--------|
| **Setup Speed** | High | 10/10 | 7/10 | SAM |
| **Local Testing** | Medium | 10/10 | 3/10 | SAM |
| **Preview Changes** | High | 0/10 | 10/10 | Terraform |
| **Multi-Cloud** | Low | 0/10 | 10/10 | Terraform |
| **State Management** | High | 6/10 | 9/10 | Terraform |
| **Modularity** | Medium | 5/10 | 10/10 | Terraform |
| **Community** | Medium | 7/10 | 10/10 | Terraform |
| **Production Features** | High | 7/10 | 10/10 | Terraform |
| **Learning Curve** | Medium | 9/10 | 6/10 | SAM |
| **Cost** | High | 10/10 | 10/10 | Tie |

**Overall Winner: Depends on your needs**

- **Quick prototype, AWS-only**: SAM
- **Production, enterprise, multi-cloud**: Terraform

## Real-World Scenarios

### Scenario 1: Startup MVP

**Recommendation: SAM**

Why:
- Need to deploy fast
- AWS-only for now
- Small team
- Cost-conscious
- Want local testing

**Deploy**:
```bash
sam build && sam deploy --guided
```

### Scenario 2: Enterprise Production

**Recommendation: Terraform**

Why:
- Need preview before deploy
- Multiple environments
- Team collaboration
- Industry-standard tooling
- Better state management

**Deploy**:
```bash
cd terraform && ./scripts/deploy.sh -e prod
```

### Scenario 3: Multi-Cloud Strategy

**Recommendation: Terraform**

Why:
- Using AWS + Azure/GCP
- Want cloud-agnostic IaC
- Future-proofing
- Consistent tooling

**Deploy**:
```bash
cd terraform && terraform apply -var-file=prod.tfvars
```

### Scenario 4: Learning Project

**Recommendation: SAM**

Why:
- Easier to learn
- Faster setup
- Good local testing
- AWS-focused

**Deploy**:
```bash
sam build && sam deploy --guided
```

## Summary

### Both Are Great!

✅ **SAM**: Perfect for AWS-only serverless projects
✅ **Terraform**: Perfect for enterprise and multi-cloud

### Key Differences

| Aspect | SAM | Terraform |
|--------|-----|-----------|
| **Best For** | AWS serverless | Enterprise IaC |
| **Setup** | Faster | Slower |
| **Preview** | No | Yes |
| **Local Test** | Yes | No |
| **Multi-Cloud** | No | Yes |
| **State** | AWS-managed | Flexible |
| **Cost** | Same | Same |

### Our Recommendation

**For this project: Terraform**

Reasons:
1. Industry-standard tooling
2. Better for production
3. More flexible
4. Better state management
5. Easier to extend

**But SAM is also excellent if:**
- You're AWS-only
- You want faster setup
- You need local testing

### Both Options Available

You have **both** implementations:
- `backend-aws/template.yaml` - SAM
- `backend-aws/terraform/` - Terraform

Choose based on your needs!

## Quick Start

### SAM (5 minutes)

```bash
cd backend-aws
sam build
sam deploy --guided
```

### Terraform (10 minutes)

```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
```

**See `QUICK-DEPLOY.md` for detailed instructions!** 🚀
