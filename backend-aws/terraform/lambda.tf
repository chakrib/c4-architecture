# Lambda Layer for shared code
resource "aws_lambda_layer_version" "common_layer" {
  filename            = "${path.module}/../layers/common.zip"
  layer_name          = "${var.project_name}-common-layer-${var.environment}"
  description         = "Common utilities and dependencies"
  compatible_runtimes = ["python3.11"]
  
  source_code_hash = filebase64sha256("${path.module}/../layers/common.zip")
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Bedrock access policy
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

# DynamoDB access policy (conditional)
resource "aws_iam_role_policy" "dynamodb_access" {
  count = var.enable_dynamodb ? 1 : 0
  
  name = "${var.project_name}-dynamodb-access-${var.environment}"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.diagram_history[0].arn
      }
    ]
  })
}

# Package Lambda functions
data "archive_file" "validate_function" {
  type        = "zip"
  source_dir  = "${path.module}/../functions/validate"
  output_path = "${path.module}/../.terraform/validate.zip"
}

data "archive_file" "suggest_function" {
  type        = "zip"
  source_dir  = "${path.module}/../functions/suggest"
  output_path = "${path.module}/../.terraform/suggest.zip"
}

data "archive_file" "generate_function" {
  type        = "zip"
  source_dir  = "${path.module}/../functions/generate"
  output_path = "${path.module}/../.terraform/generate.zip"
}

data "archive_file" "refine_function" {
  type        = "zip"
  source_dir  = "${path.module}/../functions/refine"
  output_path = "${path.module}/../.terraform/refine.zip"
}

# Validate Lambda Function
resource "aws_lambda_function" "validate" {
  filename         = data.archive_file.validate_function.output_path
  function_name    = "${var.project_name}-validate-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.validate_function.output_base64sha256
  runtime         = "python3.11"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  
  layers = [aws_lambda_layer_version.common_layer.arn]
  
  environment {
    variables = {
      BEDROCK_REGION   = var.bedrock_region
      DYNAMODB_TABLE   = var.enable_dynamodb ? aws_dynamodb_table.diagram_history[0].name : ""
      LOG_LEVEL        = "INFO"
      ENVIRONMENT      = var.environment
    }
  }
  
  tracing_config {
    mode = "Active"
  }
}

# Suggest Lambda Function
resource "aws_lambda_function" "suggest" {
  filename         = data.archive_file.suggest_function.output_path
  function_name    = "${var.project_name}-suggest-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.suggest_function.output_base64sha256
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = var.lambda_memory_size
  
  layers = [aws_lambda_layer_version.common_layer.arn]
  
  environment {
    variables = {
      BEDROCK_REGION   = var.bedrock_region
      DYNAMODB_TABLE   = var.enable_dynamodb ? aws_dynamodb_table.diagram_history[0].name : ""
      LOG_LEVEL        = "INFO"
      ENVIRONMENT      = var.environment
    }
  }
  
  tracing_config {
    mode = "Active"
  }
}

# Generate Lambda Function
resource "aws_lambda_function" "generate" {
  filename         = data.archive_file.generate_function.output_path
  function_name    = "${var.project_name}-generate-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.generate_function.output_base64sha256
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = var.lambda_memory_size
  
  layers = [aws_lambda_layer_version.common_layer.arn]
  
  environment {
    variables = {
      BEDROCK_REGION   = var.bedrock_region
      DYNAMODB_TABLE   = var.enable_dynamodb ? aws_dynamodb_table.diagram_history[0].name : ""
      LOG_LEVEL        = "INFO"
      ENVIRONMENT      = var.environment
    }
  }
  
  tracing_config {
    mode = "Active"
  }
}

# Refine Lambda Function
resource "aws_lambda_function" "refine" {
  filename         = data.archive_file.refine_function.output_path
  function_name    = "${var.project_name}-refine-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.refine_function.output_base64sha256
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = var.lambda_memory_size
  
  layers = [aws_lambda_layer_version.common_layer.arn]
  
  environment {
    variables = {
      BEDROCK_REGION   = var.bedrock_region
      DYNAMODB_TABLE   = var.enable_dynamodb ? aws_dynamodb_table.diagram_history[0].name : ""
      LOG_LEVEL        = "INFO"
      ENVIRONMENT      = var.environment
    }
  }
  
  tracing_config {
    mode = "Active"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "validate" {
  name              = "/aws/lambda/${aws_lambda_function.validate.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "suggest" {
  name              = "/aws/lambda/${aws_lambda_function.suggest.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "generate" {
  name              = "/aws/lambda/${aws_lambda_function.generate.function_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "refine" {
  name              = "/aws/lambda/${aws_lambda_function.refine.function_name}"
  retention_in_days = var.log_retention_days
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "validate_api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.validate.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "suggest_api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.suggest.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "generate_api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generate.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "refine_api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.refine.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}
