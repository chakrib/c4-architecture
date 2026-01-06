# API Gateway REST API
resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "C4 Diagram Generator API"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resources
resource "aws_api_gateway_resource" "api" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "api"
}

resource "aws_api_gateway_resource" "diagrams" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "diagrams"
}

resource "aws_api_gateway_resource" "validate" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.diagrams.id
  path_part   = "validate"
}

resource "aws_api_gateway_resource" "suggest_improvements" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.diagrams.id
  path_part   = "suggest-improvements"
}

resource "aws_api_gateway_resource" "generate" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.diagrams.id
  path_part   = "generate"
}

resource "aws_api_gateway_resource" "refine" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.diagrams.id
  path_part   = "refine"
}

# Validate Endpoint
resource "aws_api_gateway_method" "validate_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.validate.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "validate" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.validate.id
  http_method             = aws_api_gateway_method.validate_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.validate.invoke_arn
}

# Suggest Endpoint
resource "aws_api_gateway_method" "suggest_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.suggest_improvements.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "suggest" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.suggest_improvements.id
  http_method             = aws_api_gateway_method.suggest_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.suggest.invoke_arn
}

# Generate Endpoint
resource "aws_api_gateway_method" "generate_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.generate.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "generate" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.generate.id
  http_method             = aws_api_gateway_method.generate_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.generate.invoke_arn
}

# Refine Endpoint
resource "aws_api_gateway_method" "refine_post" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.refine.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "refine" {
  rest_api_id             = aws_api_gateway_rest_api.main.id
  resource_id             = aws_api_gateway_resource.refine.id
  http_method             = aws_api_gateway_method.refine_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.refine.invoke_arn
}

# CORS Configuration for all endpoints
module "cors_validate" {
  source = "./modules/cors"
  
  api_id          = aws_api_gateway_rest_api.main.id
  api_resource_id = aws_api_gateway_resource.validate.id
  allowed_origins = var.cors_allowed_origins
}

module "cors_suggest" {
  source = "./modules/cors"
  
  api_id          = aws_api_gateway_rest_api.main.id
  api_resource_id = aws_api_gateway_resource.suggest_improvements.id
  allowed_origins = var.cors_allowed_origins
}

module "cors_generate" {
  source = "./modules/cors"
  
  api_id          = aws_api_gateway_rest_api.main.id
  api_resource_id = aws_api_gateway_resource.generate.id
  allowed_origins = var.cors_allowed_origins
}

module "cors_refine" {
  source = "./modules/cors"
  
  api_id          = aws_api_gateway_rest_api.main.id
  api_resource_id = aws_api_gateway_resource.refine.id
  allowed_origins = var.cors_allowed_origins
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.validate.id,
      aws_api_gateway_method.validate_post.id,
      aws_api_gateway_integration.validate.id,
      aws_api_gateway_resource.suggest_improvements.id,
      aws_api_gateway_method.suggest_post.id,
      aws_api_gateway_integration.suggest.id,
      aws_api_gateway_resource.generate.id,
      aws_api_gateway_method.generate_post.id,
      aws_api_gateway_integration.generate.id,
      aws_api_gateway_resource.refine.id,
      aws_api_gateway_method.refine_post.id,
      aws_api_gateway_integration.refine.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
  
  depends_on = [
    aws_api_gateway_integration.validate,
    aws_api_gateway_integration.suggest,
    aws_api_gateway_integration.generate,
    aws_api_gateway_integration.refine,
  ]
}

# API Gateway Stage
resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.environment
  
  xray_tracing_enabled = true
  
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
  
  depends_on = [
    aws_api_gateway_account.main
  ]
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days
}

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
