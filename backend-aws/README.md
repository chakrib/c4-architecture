# AWS Serverless Backend

This directory contains the AWS serverless implementation of the C4 Diagram Generator backend using:
- **AWS Lambda** for compute
- **API Gateway** for REST API
- **AWS Bedrock** for Claude AI access
- **DynamoDB** for persistence (optional)
- **SAM (Serverless Application Model)** for infrastructure

## Architecture

```
CloudFront → API Gateway → Lambda Functions → AWS Bedrock (Claude)
                                ↓
                           DynamoDB (optional)
```

## Directory Structure

```
backend-aws/
├── README.md                    # This file
├── template.yaml                # SAM template (IaC)
├── samconfig.toml              # SAM configuration
├── requirements.txt            # Python dependencies
├── functions/                  # Lambda functions
│   ├── validate/              # Validation function
│   ├── suggest/               # Suggestion function
│   ├── generate/              # Generation function
│   └── refine/                # Refinement function
├── layers/                    # Lambda layers
│   └── common/                # Shared code
├── infrastructure/            # Additional IaC
│   ├── terraform/            # Terraform (alternative)
│   └── cloudformation/       # CloudFormation (alternative)
├── tests/                    # Unit and integration tests
├── scripts/                  # Deployment scripts
└── docs/                     # Documentation
    ├── DEPLOYMENT.md
    ├── MIGRATION.md
    └── ARCHITECTURE.md
```

## Quick Start

### Prerequisites
- AWS CLI configured
- SAM CLI installed
- Python 3.11+
- AWS account with Bedrock access

### Deploy

```bash
# Build
sam build

# Deploy
sam deploy --guided

# Test
sam local start-api
```

## Features

- ✅ Serverless Lambda functions
- ✅ API Gateway REST API
- ✅ AWS Bedrock integration
- ✅ DynamoDB for persistence
- ✅ CloudWatch logging
- ✅ IAM security
- ✅ Infrastructure as Code (SAM)
- ✅ Local testing support

## Cost Estimate

**Low traffic** (< 10K requests/month): ~$5-20/month
**Medium traffic** (100K requests/month): ~$50-150/month

## Next Steps

1. Review `docs/MIGRATION.md` for migration guide
2. Review `docs/ARCHITECTURE.md` for detailed architecture
3. Deploy using `sam deploy --guided`
4. Update frontend to point to new API Gateway URL
