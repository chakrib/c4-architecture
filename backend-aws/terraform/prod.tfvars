# Production environment configuration
environment    = "prod"
aws_region     = "us-east-1"
bedrock_region = "us-east-1"

enable_dynamodb    = true
lambda_timeout     = 60
lambda_memory_size = 1024
log_retention_days = 30

# Update with your actual production domain
cors_allowed_origins = ["https://yourdomain.com"]
