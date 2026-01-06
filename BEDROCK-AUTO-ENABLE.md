# AWS Bedrock Auto-Enable Update

## What Changed

AWS has **retired the Model Access page** and now **automatically enables** Bedrock models on first use!

## Old Process (Retired)

❌ **Manual Steps Required**:
1. Go to AWS Console → Bedrock → Model access
2. Request access to specific models
3. Wait for approval
4. Then use the model

## New Process (Current)

✅ **Automatic Enablement**:
1. Deploy your Lambda functions
2. Make your first API call
3. Model auto-enables on first invocation
4. Subsequent calls work immediately

**No manual activation needed!**

## What This Means for You

### Good News

✅ **Faster deployment** - No waiting for model approval
✅ **Simpler process** - Just deploy and use
✅ **Instant access** - Models activate automatically
✅ **No manual steps** - Everything happens automatically

### For Anthropic Models (Claude)

**First-time users** may need to provide use case details:

- **Most cases**: Works automatically
- **Some cases**: May need to submit use case via Model catalog
- **Rare cases**: May need AWS support for approval

### What You Need to Do

**Nothing different!** Just deploy as planned:

```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
```

The model will auto-enable when your Lambda function first calls Bedrock.

## If You Get Access Denied

**Error**: `AccessDeniedException: Could not access model`

**Solution**:

### Step 1: Try Again
Sometimes the first invocation triggers enablement. Wait 1-2 minutes and retry.

### Step 2: Submit Use Case (If Needed)
1. Go to: **AWS Console → Bedrock → Model catalog**
2. Search: **Claude 3.5 Sonnet**
3. Click: **View details** or **Open in playground**
4. If prompted: Submit use case information
   - **Use case**: C4 architecture diagram generation
   - **Description**: Generating PlantUML diagrams from natural language
   - **Industry**: Technology/Software Development

### Step 3: Verify IAM Permissions
Check your Lambda function has correct permissions:

```bash
cd backend-aws/terraform
terraform state show aws_iam_role_policy.bedrock_access
```

Should show:
```hcl
Action = "bedrock:InvokeModel"
Resource = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
```

### Step 4: Check CloudWatch Logs
View detailed error messages:

```bash
FUNCTION_NAME=$(terraform output -raw generate_function_name)
aws logs tail /aws/lambda/$FUNCTION_NAME --follow
```

## Documentation Updates

Updated all documentation to reflect auto-enablement:

- ✅ `DEPLOY-AND-TEST.md` - Updated prerequisites
- ✅ `TESTING-CHECKLIST.md` - Updated checklist
- ✅ `QUICK-REFERENCE.md` - Updated troubleshooting
- ✅ `READY-TO-DEPLOY.md` - Updated prerequisites
- ✅ `MODEL-UPGRADE-SONNET.md` - Updated Bedrock access section

## Key Points

### What Stayed the Same

✅ IAM permissions still required
✅ Model IDs unchanged
✅ API calls unchanged
✅ Deployment process unchanged

### What Changed

✅ No manual model access requests
✅ No waiting for approval
✅ Models activate on first use
✅ Simpler overall process

## Testing

After deployment, test immediately:

```bash
API_ENDPOINT=$(terraform output -raw api_endpoint)

curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'
```

**Expected**:
- **First call**: May take 2-3 seconds (model activation + generation)
- **Subsequent calls**: 2-4 seconds (just generation)
- **If access denied**: Follow troubleshooting steps above

## Regional Availability

Bedrock models are available in most AWS commercial regions:

**Recommended**: `us-east-1` (N. Virginia)
**Also available**: `us-west-2`, `eu-west-1`, `ap-southeast-1`, etc.

Check current availability: [AWS Bedrock Regions](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html)

## Cost Impact

**No change** - Auto-enablement doesn't affect pricing:

- Still pay per token used
- No activation fees
- Same pricing as before

## Summary

🎉 **Great news**: Bedrock access is now simpler!

**Old way**:
1. Request access
2. Wait for approval
3. Deploy
4. Use

**New way**:
1. Deploy
2. Use (auto-enables on first call)

**Bottom line**: Just deploy and test. The model will activate automatically when first used!

---

**Ready to deploy**: `cd backend-aws/terraform && ./scripts/deploy.sh -e dev`
