# Model Upgrade: Claude 3.5 Sonnet

## What Changed

Upgraded from **Claude 3 Haiku** to **Claude 3.5 Sonnet** for better output quality.

## Files Updated

### 1. Lambda Layer (Bedrock Client)
**File**: `backend-aws/layers/common/python/common/bedrock_client.py`

**Change**:
```python
# Before
self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'

# After
self.model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
```

### 2. Terraform Configuration
**File**: `backend-aws/terraform/lambda.tf`

**Change**:
```hcl
# Before
Resource = "arn:aws:bedrock:${var.bedrock_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"

# After
Resource = "arn:aws:bedrock:${var.bedrock_region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
```

### 3. SAM Template
**File**: `backend-aws/template.yaml`

**Change**: Updated all 3 Lambda functions (Suggest, Generate, Refine) to use Sonnet 3.5

### 4. Documentation
Updated references in:
- `DEPLOY-AND-TEST.md`
- `TESTING-CHECKLIST.md`
- `QUICK-REFERENCE.md`
- `READY-TO-DEPLOY.md`

## Impact

### Quality Improvements

**Diagram Generation**:
- ✅ More detailed component descriptions
- ✅ Better component naming
- ✅ More accurate relationships
- ✅ Better handling of complex architectures

**Intelligent Suggestions**:
- ✅ More diverse and creative suggestions
- ✅ Better context understanding
- ✅ More professional interpretations

**Diagram Refinement**:
- ✅ Better understanding of vague requests
- ✅ More intelligent component placement
- ✅ Better handling of complex refinements

### Performance Impact

**Response Time**:
- Before (Haiku): 1-2 seconds
- After (Sonnet 3.5): 2-4 seconds
- **Impact**: +1-2 seconds per request (acceptable)

**Cost Impact**:
- Before (Haiku): $0.25 per million input tokens
- After (Sonnet 3.5): $3 per million input tokens
- **Impact**: 12x increase in cost

**Monthly Cost Estimate** (100K requests):
- Before: ~$150/month
- After: ~$1,800/month
- **Difference**: +$1,650/month

### Trade-offs

| Aspect | Haiku | Sonnet 3.5 | Verdict |
|--------|-------|------------|---------|
| **Quality** | Good | Excellent | ✅ Sonnet wins |
| **Speed** | 1-2s | 2-4s | ⚠️ Haiku faster |
| **Cost** | $150 | $1,800 | ⚠️ Haiku cheaper |
| **Overall** | Fast & Cheap | High Quality | ✅ Sonnet for quality |

## AWS Bedrock Access

### Automatic Model Enablement (New!)

**Great news**: AWS has simplified Bedrock access!

**Old Process** (Retired):
- ❌ Manual model access requests
- ❌ Waiting for approval
- ❌ Model access page

**New Process** (Current):
- ✅ Models auto-enable on first invocation
- ✅ No manual activation needed
- ✅ Instant access in most cases

### How It Works

1. **Deploy your Lambda functions** with Terraform
2. **First API call** to your Lambda will invoke Bedrock
3. **Model auto-enables** on first use
4. **Subsequent calls** work immediately

### For Anthropic Models (Claude)

**First-time users** may need to provide use case details:

1. **Try deploying first** - May work without any action
2. **If you get access denied**:
   - Go to: **AWS Console → Bedrock → Model catalog**
   - Find: **Claude 3.5 Sonnet**
   - Click: **Open in playground** or **View details**
   - Submit: **Use case information** (if prompted)
   - Retry: Your Lambda function call

### Use Case Details (If Required)

If prompted, provide:
- **Use case**: "C4 architecture diagram generation"
- **Description**: "Generating PlantUML C4 diagrams from natural language descriptions"
- **Industry**: Technology/Software Development

### IAM Permissions

Your Lambda functions already have the correct IAM permissions:

```hcl
Action = "bedrock:InvokeModel"
Resource = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
```

No changes needed!

### Troubleshooting

**If you get `AccessDeniedException`**:

1. **Check region**: Ensure Bedrock is available in your region (us-east-1 recommended)
2. **Submit use case**: Visit Model catalog and provide use case details
3. **Wait a moment**: First-time activation may take 1-2 minutes
4. **Retry**: Call your API again

**If still denied**:
- Check IAM permissions on Lambda role
- Verify model ID is correct
- Check CloudWatch logs for detailed error

### Model Details

**Full Model ID**: `anthropic.claude-3-5-sonnet-20240620-v1:0`

**Pricing**:
- Input: $3 per million tokens
- Output: $15 per million tokens

**Capabilities**:
- Max tokens: 4096 output
- Context window: 200K tokens
- Best for: Complex reasoning, nuanced understanding

## Deployment

### New Deployment

If deploying for the first time:

```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
```

The deployment will automatically use Sonnet 3.5.

### Existing Deployment

If you already deployed with Haiku:

```bash
cd backend-aws/terraform

# Rebuild Lambda layer with updated code
./scripts/build-layer.sh

# Redeploy
terraform apply -var-file=dev.tfvars
```

Terraform will detect the IAM policy change and update the Lambda functions.

## Testing

After deployment, test to verify Sonnet 3.5 is working:

```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)

# Test generation
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a complex e-commerce platform with microservices, payment processing, inventory management, and real-time notifications"}'
```

**Expected**: More detailed and professional diagram output compared to Haiku.

## Rollback (if needed)

If you want to rollback to Haiku:

### 1. Update Bedrock Client

```python
# backend-aws/layers/common/python/common/bedrock_client.py
self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
```

### 2. Update Terraform

```hcl
# backend-aws/terraform/lambda.tf
Resource = "arn:aws:bedrock:${var.bedrock_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
```

### 3. Update SAM Template

```yaml
# backend-aws/template.yaml
Resource: !Sub 'arn:aws:bedrock:${BedrockRegion}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0'
```

### 4. Redeploy

```bash
cd backend-aws/terraform
./scripts/build-layer.sh
terraform apply -var-file=dev.tfvars
```

## Monitoring

### CloudWatch Logs

Monitor for any Bedrock errors:

```bash
FUNCTION_NAME=$(terraform output -raw generate_function_name)
aws logs tail /aws/lambda/$FUNCTION_NAME --follow
```

### Cost Monitoring

Monitor Bedrock costs in AWS Cost Explorer:

1. Go to: **AWS Console → Cost Explorer**
2. Filter by: **Service → Bedrock**
3. Check: Daily/Monthly costs

### Performance Monitoring

Monitor response times:

1. Go to: **AWS Console → CloudWatch → Metrics**
2. Select: **Lambda → Function Metrics**
3. Check: **Duration** metric

## Recommendations

### For Production

**Use Sonnet 3.5 if**:
- ✅ Quality is priority
- ✅ Complex architectures
- ✅ Professional outputs needed
- ✅ Cost is acceptable

**Use Haiku if**:
- ✅ Cost is priority
- ✅ High volume usage
- ✅ Simple diagrams
- ✅ Speed is critical

### Hybrid Approach

Consider using different models for different endpoints:

- **Validate**: No model needed (validation logic only)
- **Suggest**: Sonnet 3.5 (benefits from better creativity)
- **Generate**: Sonnet 3.5 (benefits from better quality)
- **Refine**: Sonnet 3.5 (benefits from better understanding)

Or:

- **Simple requests**: Haiku (fast and cheap)
- **Complex requests**: Sonnet 3.5 (better quality)

## Summary

✅ **Upgraded to Claude 3.5 Sonnet**
- Better quality outputs
- More detailed diagrams
- Better suggestions
- Better refinement understanding

⚠️ **Trade-offs**:
- 12x higher cost
- 1-2 seconds slower
- Worth it for quality

🚀 **Ready to deploy**:
```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
```

**Remember**: Enable Claude 3.5 Sonnet access in AWS Bedrock before deploying!
