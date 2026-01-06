#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
AUTO_APPROVE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    -y|--yes)
      AUTO_APPROVE=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  -e, --environment ENV    Environment to deploy (dev, staging, prod). Default: dev"
      echo "  -y, --yes               Auto-approve Terraform apply"
      echo "  -h, --help              Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                      # Deploy to dev environment"
      echo "  $0 -e prod              # Deploy to prod environment"
      echo "  $0 -e dev -y            # Deploy to dev with auto-approve"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
  echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'. Must be dev, staging, or prod.${NC}"
  exit 1
fi

echo -e "${GREEN}=== C4 Diagram Generator - Terraform Deployment ===${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
  echo -e "${RED}Error: Terraform is not installed${NC}"
  exit 1
fi

if ! command -v aws &> /dev/null; then
  echo -e "${RED}Error: AWS CLI is not installed${NC}"
  exit 1
fi

if ! command -v python3 &> /dev/null; then
  echo -e "${RED}Error: Python 3 is not installed${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Navigate to terraform directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"
cd "$TERRAFORM_DIR"

# Build Lambda layer
echo "Building Lambda layer..."
./scripts/build-layer.sh
echo ""

# Initialize Terraform
echo "Initializing Terraform..."
terraform init
echo ""

# Select or create workspace
echo "Setting up Terraform workspace..."
if terraform workspace list | grep -q "$ENVIRONMENT"; then
  terraform workspace select "$ENVIRONMENT"
else
  terraform workspace new "$ENVIRONMENT"
fi
echo ""

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate
echo -e "${GREEN}✓ Configuration is valid${NC}"
echo ""

# Plan deployment
echo "Planning deployment..."
PLAN_FILE="tfplan-$ENVIRONMENT"
terraform plan -var-file="${ENVIRONMENT}.tfvars" -out="$PLAN_FILE"
echo ""

# Apply deployment
if [ "$AUTO_APPROVE" = true ]; then
  echo "Applying deployment (auto-approved)..."
  terraform apply "$PLAN_FILE"
else
  echo -e "${YELLOW}Review the plan above.${NC}"
  read -p "Do you want to apply these changes? (yes/no): " CONFIRM
  if [ "$CONFIRM" = "yes" ]; then
    terraform apply "$PLAN_FILE"
  else
    echo -e "${RED}Deployment cancelled${NC}"
    rm -f "$PLAN_FILE"
    exit 0
  fi
fi

# Cleanup plan file
rm -f "$PLAN_FILE"

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "API Endpoint:"
terraform output -raw api_endpoint
echo ""
echo ""
echo "To test the API:"
echo "  export API_ENDPOINT=\$(terraform output -raw api_endpoint)"
echo "  curl -X POST \"\${API_ENDPOINT}/api/diagrams/validate\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"description\": \"Build a web app with authentication and database\"}'"
echo ""
echo "To view logs:"
echo "  aws logs tail /aws/lambda/\$(terraform output -raw validate_function_name) --follow"
echo ""
echo "To destroy resources:"
echo "  terraform destroy -var-file=${ENVIRONMENT}.tfvars"
echo ""
