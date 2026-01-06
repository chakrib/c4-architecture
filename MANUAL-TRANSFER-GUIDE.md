# Manual Transfer Guide - Essential Files Only

This guide lists ONLY the files you need to manually recreate on your work laptop.

---

## 🎯 Quick Summary

**Total Essential Files**: 23 files
- **Frontend**: 4 files
- **Backend AWS (Terraform)**: 19 files

**Skip Entirely**:
- `backend/` folder (old FastAPI backend - not used)
- All `.md` documentation files (except this guide)
- `node_modules/`, `venv/`, `.terraform/` folders
- `.git/` folder

---

## 📁 Directory Structure to Create

```
c4-diagram-generator/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── DiagramGenerator.jsx
│   │   └── services/
│   │       └── AIService.js
│   ├── .env
│   └── package.json
│
└── backend-aws/
    ├── terraform/
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   ├── lambda.tf
    │   ├── api_gateway.tf
    │   ├── dynamodb.tf
    │   ├── dev.tfvars
    │   ├── modules/
    │   │   └── cors/
    │   │       ├── main.tf
    │   │       ├── variables.tf
    │   │       └── outputs.tf
    │   └── scripts/
    │       └── build-layer.sh
    │
    ├── functions/
    │   ├── validate/
    │   │   └── app.py
    │   ├── suggest/
    │   │   └── app.py
    │   ├── generate/
    │   │   └── app.py
    │   └── refine/
    │       └── app.py
    │
    └── layers/
        └── common/
            └── python/
                └── common/
                    ├── __init__.py
                    ├── bedrock_client.py
                    └── validation.py
```

---

## 🔴 CRITICAL FILES (Must Transfer Exactly)

### 1. Frontend Configuration

#### `frontend/.env`
```env
VITE_BACKEND_URL=https://6y47pptuyi.execute-api.us-east-1.amazonaws.com/dev
VITE_OPENAI_API_KEY=
VITE_ANTHROPIC_API_KEY=
```
**Note**: Replace the API endpoint with YOUR deployed endpoint after running Terraform

---

#### `frontend/src/services/AIService.js`
**Key Changes from Original**:
- Line 3: `this.backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'`
- Lines 78-88: Updated error handling to support both Lambda and FastAPI formats

**Critical Section** (lines 78-88):
```javascript
if (!response.ok) {
  const error = await response.json()
  
  // Handle both FastAPI format (error.detail.errors) and Lambda format (error.errors)
  const errors = error.errors || (error.detail && error.detail.errors)
  const questions = error.questions || (error.detail && error.detail.questions)
  const suggestions = error.suggestions || (error.detail && error.detail.suggestions)
  
  if (errors) {
    // Format validation errors with questions if present
    let errorMessage = errors.join('\n')
    
    if (questions && questions.length > 0) {
      errorMessage += '\n\n❓ Please provide more information:\n' + 
        questions.map((q, i) => `${i + 1}. ${q}`).join('\n')
    }
    
    if (suggestions && suggestions.length > 0) {
      errorMessage += '\n\n💡 Suggestions:\n' + suggestions.join('\n')
    }
    
    throw new Error(errorMessage)
  }
  throw new Error(error.message || error.detail || 'Failed to generate diagram')
}
```

---

#### `frontend/src/components/DiagramGenerator.jsx`
**Key Change from Original**:
- Lines 56-68: Updated to trigger suggestions for "Input too short" errors

**Critical Section** (lines 56-68):
```javascript
} catch (err) {
  // Check if we should offer suggestions
  const errorMsg = err.message || ''
  
  // Auto-fetch suggestions for any validation error (not gibberish)
  if (errorMsg.includes('Input too short') || 
      errorMsg.includes('Insufficient information') || 
      errorMsg.includes('provide more information') ||
      errorMsg.includes('Need at least')) {
    // Show error and auto-fetch suggestions
    setError(errorMsg)
    handleGetSuggestions()
  } else {
    setError(errorMsg || 'Failed to generate diagram. Please check your API key configuration.')
  }
} finally {
  setLoading(false)
}
```

---

### 2. Terraform Infrastructure (Backend AWS)

#### `backend-aws/terraform/lambda.tf`
**Key Change from Original**:
- Lines 40-52: Added AWS Marketplace permissions to Bedrock policy

**Critical Section** (lines 40-52):
```hcl
resource "aws_iam_role_policy" "bedrock_access" {
  name = "${var.project_name}-bedrock-access-${var.environment}"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "arn:aws:bedrock:${var.bedrock_region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
      },
      {
        Effect = "Allow"
        Action = [
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Subscribe"
        ]
        Resource = "*"
      }
    ]
  })
}
```

---

#### `backend-aws/terraform/api_gateway.tf`
**Key Changes from Original**:
- Lines 220-250: Added IAM role for API Gateway CloudWatch logging
- Line 210: Added dependency on `aws_api_gateway_account.main`

**Critical Sections**:

**Lines 220-250** (CloudWatch IAM Role):
```hcl
# IAM Role for API Gateway CloudWatch Logging
resource "aws_iam_role" "api_gateway_cloudwatch" {
  name = "${var.project_name}-api-gateway-cloudwatch-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
}

# Attach AWS managed policy for API Gateway to push logs to CloudWatch
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  role       = aws_iam_role.api_gateway_cloudwatch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# API Gateway Account settings (sets CloudWatch role for the account)
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}
```

**Line 210** (Stage dependency):
```hcl
resource "aws_api_gateway_stage" "main" {
  # ... other config ...
  
  depends_on = [
    aws_api_gateway_account.main
  ]
}
```

---

#### `backend-aws/terraform/scripts/build-layer.sh`
**Key Change from Original**:
- Lines 18-25: Updated pip install to build for Linux x86_64

**Critical Section** (lines 18-25):
```bash
echo "Installing Python dependencies..."
# Install for Linux x86_64 architecture (Lambda runtime)
# Only install pydantic (boto3/botocore are pre-installed in Lambda Python 3.11 runtime)
pip3 install pydantic==2.10.3 \
  -t "$BUILD_DIR/python" \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  --no-cache-dir
```

---

## 📋 Files to Copy Exactly (No Changes)

These files should be copied character-for-character from the original:

### Terraform Core Files
1. `backend-aws/terraform/main.tf`
2. `backend-aws/terraform/variables.tf`
3. `backend-aws/terraform/outputs.tf`
4. `backend-aws/terraform/dynamodb.tf`
5. `backend-aws/terraform/dev.tfvars`

### Terraform CORS Module
6. `backend-aws/terraform/modules/cors/main.tf`
7. `backend-aws/terraform/modules/cors/variables.tf`
8. `backend-aws/terraform/modules/cors/outputs.tf`

### Lambda Functions
9. `backend-aws/functions/validate/app.py`
10. `backend-aws/functions/suggest/app.py`
11. `backend-aws/functions/generate/app.py`
12. `backend-aws/functions/refine/app.py`

### Lambda Layer (Common Utilities)
13. `backend-aws/layers/common/python/common/__init__.py`
14. `backend-aws/layers/common/python/common/bedrock_client.py`
15. `backend-aws/layers/common/python/common/validation.py`

### Frontend Package Config
16. `frontend/package.json`

---

## 🟡 Files You Can Skip

**Documentation** (all `.md` files except this guide):
- All documentation is for reference only
- Not needed for deployment

**Generated/Build Artifacts**:
- `node_modules/` - Will be regenerated by `npm install`
- `backend-aws/.terraform/` - Will be regenerated by `terraform init`
- `backend-aws/layers/common.zip` - Will be built by `build-layer.sh`
- `venv/` - Not needed (old backend)

**Old Backend**:
- Entire `backend/` folder - Not used (we use AWS Lambda now)

---

## 🚀 Deployment Steps on Work Laptop

### 1. Install Prerequisites
```bash
# Install Node.js (for frontend)
# Install Python 3.11 (for Lambda layer build)
# Install Terraform
# Install AWS CLI and configure credentials
```

### 2. Build Lambda Layer
```bash
cd backend-aws/terraform/scripts
bash build-layer.sh
```

### 3. Deploy Infrastructure
```bash
cd backend-aws/terraform
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

### 4. Get API Endpoint
```bash
terraform output api_endpoint
# Copy this URL
```

### 5. Update Frontend Config
Edit `frontend/.env`:
```env
VITE_BACKEND_URL=<paste-your-api-endpoint-here>
```

### 6. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 7. Run Frontend
```bash
npm run dev
```

---

## 📝 File Size Reference

To help you estimate typing time:

**Small Files** (<100 lines):
- `frontend/.env` - 3 lines
- `backend-aws/terraform/dev.tfvars` - ~20 lines
- All `__init__.py` files - 1 line each

**Medium Files** (100-300 lines):
- `backend-aws/terraform/main.tf` - ~50 lines
- `backend-aws/terraform/variables.tf` - ~80 lines
- `backend-aws/terraform/outputs.tf` - ~40 lines
- `backend-aws/terraform/dynamodb.tf` - ~30 lines
- `backend-aws/terraform/scripts/build-layer.sh` - ~60 lines
- Each Lambda function - ~150 lines each
- `bedrock_client.py` - ~80 lines
- `validation.py` - ~250 lines

**Large Files** (300+ lines):
- `backend-aws/terraform/lambda.tf` - ~300 lines
- `backend-aws/terraform/api_gateway.tf` - ~250 lines
- `frontend/src/services/AIService.js` - ~130 lines
- `frontend/src/components/DiagramGenerator.jsx` - ~400 lines
- `frontend/package.json` - ~50 lines

**Total Lines to Type**: ~2,500 lines

---

## 💡 Pro Tips

1. **Start with Terraform files** - Get infrastructure working first
2. **Use the "Critical Sections" above** - These are the ONLY changes from original
3. **Test after each major section** - Don't wait until everything is typed
4. **Frontend can wait** - Deploy backend first, test with curl
5. **Copy-paste from this guide** - For the critical sections, you can type from this document

---

## ✅ Verification Checklist

After typing everything:

- [ ] Lambda layer builds successfully (4.2MB)
- [ ] Terraform init works
- [ ] Terraform plan shows ~30 resources
- [ ] Terraform apply succeeds
- [ ] API endpoint is accessible
- [ ] Frontend .env has correct endpoint
- [ ] npm install works
- [ ] npm run dev starts frontend
- [ ] Can generate diagrams

---

## 🆘 If Something Doesn't Work

1. **Lambda layer too large**: Check `build-layer.sh` has the `--platform manylinux2014_x86_64` flags
2. **API Gateway logging error**: Check `api_gateway.tf` has the IAM role and account resources
3. **Bedrock access denied**: Check `lambda.tf` has marketplace permissions
4. **Frontend shows "Failed to fetch"**: Check `.env` has correct API endpoint
5. **Validation errors not showing**: Check `AIService.js` has the dual format error handling

---

## 📞 Quick Reference

**Your Deployed API Endpoint**:
```
https://6y47pptuyi.execute-api.us-east-1.amazonaws.com/dev
```
(This will be different on your work laptop after deployment)

**Model Used**: Claude 3.5 Sonnet (`anthropic.claude-3-5-sonnet-20240620-v1:0`)

**Region**: us-east-1

---

Good luck with the manual transfer! Focus on the 3 files with changes first (marked 🔴 CRITICAL), then copy the rest exactly.
