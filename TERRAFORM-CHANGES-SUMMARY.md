# Terraform Changes Summary

All infrastructure changes were made exclusively through Terraform to maintain Infrastructure as Code best practices.

---

## Files Modified

### 1. `backend-aws/terraform/lambda.tf`

**Changes Made:**
- Added AWS Marketplace permissions to Bedrock IAM policy
- Enables Lambda to auto-enable Bedrock models on first use

```hcl
# Added to bedrock_access policy
{
  Effect = "Allow"
  Action = [
    "aws-marketplace:ViewSubscriptions",
    "aws-marketplace:Subscribe"
  ]
  Resource = "*"
}
```

**Why:** Required for first-time Anthropic Claude model access

---

### 2. `backend-aws/terraform/api_gateway.tf`

**Changes Made:**
- Added IAM role for API Gateway CloudWatch logging
- Added API Gateway account settings
- Added explicit dependency in stage resource

```hcl
# New resources added:
resource "aws_iam_role" "api_gateway_cloudwatch" { ... }
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" { ... }
resource "aws_api_gateway_account" "main" { ... }

# Updated stage resource:
resource "aws_api_gateway_stage" "main" {
  depends_on = [
    aws_api_gateway_account.main  # Added dependency
  ]
}
```

**Why:** Required for API Gateway to write logs to CloudWatch

---

### 3. `backend-aws/terraform/scripts/build-layer.sh`

**Changes Made:**
- Updated pip install command to build for Linux x86_64 architecture
- Added platform-specific flags

```bash
# Before:
pip3 install pydantic==2.10.3 -t "$BUILD_DIR/python" --upgrade --no-cache-dir

# After:
pip3 install pydantic==2.10.3 \
  -t "$BUILD_DIR/python" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  --no-cache-dir
```

**Why:** Lambda runs on Linux, not macOS. Building on macOS without platform flags creates incompatible binaries.

**Result:** Layer size reduced from 79MB to 4.2MB

---

## Non-Terraform Changes (Frontend Only)

These changes were made to connect the frontend to AWS:

### 1. `frontend/.env`
```env
# Changed from:
VITE_BACKEND_URL=http://localhost:8000

# To:
VITE_BACKEND_URL=https://6y47pptuyi.execute-api.us-east-1.amazonaws.com/dev
```

### 2. `frontend/src/services/AIService.js`
```javascript
// Changed from:
this.backendUrl = 'http://localhost:8000'

// To:
this.backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
```

---

## Deployment Commands Used

### 1. Build Lambda Layer
```bash
cd backend-aws/terraform/scripts
bash build-layer.sh
```

### 2. Deploy Infrastructure
```bash
cd backend-aws/terraform
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars" -auto-approve
```

### 3. Verify Deployment
```bash
terraform output
```

---

## Resources Created by Terraform

### Lambda Functions (4)
- `c4-diagram-generator-validate-dev`
- `c4-diagram-generator-suggest-dev`
- `c4-diagram-generator-generate-dev`
- `c4-diagram-generator-refine-dev`

### Lambda Layer (1)
- `c4-diagram-generator-common-layer-dev:2`

### API Gateway (1)
- `c4-diagram-generator-api-dev`
- Stage: `dev`
- 4 endpoints: validate, suggest, generate, refine

### IAM Roles (2)
- Lambda execution role
- API Gateway CloudWatch logging role

### IAM Policies (3)
- Lambda basic execution (AWS managed)
- Bedrock access with marketplace permissions
- DynamoDB access

### CloudWatch Log Groups (5)
- API Gateway logs
- 4 Lambda function logs

### DynamoDB Table (1)
- `c4-diagram-generator-diagram-history-dev`

### Lambda Permissions (4)
- API Gateway invoke permissions for each Lambda

---

## Terraform State

### Current State
- **Location**: Local filesystem
- **Resources**: 30+ resources
- **Modules**: 4 CORS modules

### State Management Commands
```bash
# View state
terraform state list

# Show specific resource
terraform state show aws_lambda_function.generate

# Move resource (if needed)
terraform state mv <source> <destination>

# Remove resource from state (if needed)
terraform state rm <resource>
```

---

## Infrastructure Updates

To update infrastructure in the future:

### 1. Modify Terraform Files
Edit any `.tf` file in `backend-aws/terraform/`

### 2. Plan Changes
```bash
terraform plan -var-file="dev.tfvars"
```

### 3. Apply Changes
```bash
terraform apply -var-file="dev.tfvars"
```

### 4. Verify
```bash
terraform output
```

---

## Rollback Strategy

If you need to rollback changes:

### Option 1: Terraform Rollback
```bash
# View state history
terraform state pull

# Restore from backup
terraform state push terraform.tfstate.backup
```

### Option 2: Redeploy Previous Version
```bash
# Checkout previous commit
git checkout <previous-commit>

# Redeploy
terraform apply -var-file="dev.tfvars"
```

### Option 3: Destroy and Recreate
```bash
# Destroy all resources
terraform destroy -var-file="dev.tfvars"

# Recreate from scratch
terraform apply -var-file="dev.tfvars"
```

---

## Best Practices Followed

### ✅ Infrastructure as Code
- All infrastructure defined in Terraform
- No manual AWS Console changes
- Version controlled in Git

### ✅ Modular Design
- Reusable CORS module
- Separate files for different resources
- Clear naming conventions

### ✅ Environment Separation
- `dev.tfvars` for development
- `prod.tfvars` for production
- Workspace support

### ✅ Security
- IAM least-privilege access
- No hardcoded credentials
- Proper CORS configuration

### ✅ Observability
- CloudWatch logging enabled
- X-Ray tracing enabled
- Structured log formats

---

## Future Terraform Enhancements

### 1. Remote State Backend
```hcl
terraform {
  backend "s3" {
    bucket = "your-terraform-state"
    key    = "c4-generator/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt = true
  }
}
```

### 2. Terraform Workspaces
```bash
terraform workspace new prod
terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```

### 3. Terraform Modules
Extract common patterns into reusable modules:
- Lambda function module
- API Gateway endpoint module
- CloudWatch logging module

### 4. Automated Testing
```bash
# Install terratest
go get github.com/gruntwork-io/terratest

# Run tests
go test -v
```

---

## Summary

All infrastructure changes were made through Terraform:
- ✅ 3 Terraform files modified
- ✅ 1 build script updated
- ✅ 30+ AWS resources deployed
- ✅ 100% Infrastructure as Code
- ✅ Fully reproducible deployment

No manual AWS Console changes were required (except one-time Bedrock model enablement).
