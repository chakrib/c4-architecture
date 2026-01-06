# Quick Reference Card

## 🚀 Deploy AWS Backend

```bash
cd backend-aws/terraform
./scripts/deploy.sh -e dev
```

## 🔗 Get API Endpoint

```bash
cd backend-aws/terraform
terraform output api_endpoint
```

## 🎨 Update Frontend

```bash
cd frontend
echo "VITE_API_BASE_URL=<your-api-endpoint>" > .env
npm run dev
```

## 🧪 Test Endpoints

```bash
# Set API endpoint
API_ENDPOINT="<your-endpoint>"

# Test validate
curl -X POST "${API_ENDPOINT}/api/diagrams/validate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'

# Test suggest
curl -X POST "${API_ENDPOINT}/api/diagrams/suggest-improvements" \
  -H "Content-Type: application/json" \
  -d '{"description": "web app"}'

# Test generate
curl -X POST "${API_ENDPOINT}/api/diagrams/generate" \
  -H "Content-Type: application/json" \
  -d '{"description": "Build a web app with auth and database"}'

# Test refine
curl -X POST "${API_ENDPOINT}/api/diagrams/refine" \
  -H "Content-Type: application/json" \
  -d '{"current_diagram": "...", "refinement_request": "Add a database"}'
```

## 📊 View Logs

```bash
cd backend-aws/terraform

# Get function name
FUNCTION_NAME=$(terraform output -raw validate_function_name)

# Tail logs
aws logs tail /aws/lambda/$FUNCTION_NAME --follow
```

## 🗑️ Cleanup

```bash
cd backend-aws/terraform
terraform destroy -var-file=dev.tfvars
```

## 📚 Documentation

- **Deploy & Test**: `DEPLOY-AND-TEST.md`
- **Testing Checklist**: `TESTING-CHECKLIST.md`
- **Terraform Guide**: `backend-aws/terraform/README.md`
- **Quick Deploy**: `backend-aws/QUICK-DEPLOY.md`
- **SAM vs Terraform**: `backend-aws/SAM-VS-TERRAFORM.md`

## 🆘 Troubleshooting

### Bedrock Access Denied
→ Models now auto-enable on first use
→ For Anthropic: May need to submit use case details
→ AWS Console → Bedrock → Model catalog → Claude 3.5 Sonnet

### Lambda Timeout
→ Edit `terraform/variables.tf` → Increase `lambda_timeout` to 60

### CORS Errors
→ Check `frontend/.env` has correct API endpoint

### Cold Start Delays
→ Normal (1-2 seconds first request, then 200-500ms)

## ✅ Success Criteria

- [ ] All 4 Lambda functions deployed
- [ ] API Gateway accessible
- [ ] Frontend connects without errors
- [ ] All features work identically to FastAPI
- [ ] No CORS errors
- [ ] Performance acceptable

## 📞 Support

- **Deployment Issues**: See `DEPLOY-AND-TEST.md`
- **Testing Issues**: See `TESTING-CHECKLIST.md`
- **Terraform Issues**: See `backend-aws/terraform/README.md`
- **CloudWatch Logs**: Check for detailed errors

---

**Quick Start**: `cd backend-aws/terraform && ./scripts/deploy.sh -e dev`
