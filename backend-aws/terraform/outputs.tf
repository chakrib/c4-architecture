output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_stage.main.invoke_url}"
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.main.id
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for diagram history"
  value       = var.enable_dynamodb ? aws_dynamodb_table.diagram_history[0].name : null
}

output "dynamodb_table_arn" {
  description = "DynamoDB table ARN"
  value       = var.enable_dynamodb ? aws_dynamodb_table.diagram_history[0].arn : null
}

output "validate_function_name" {
  description = "Validate Lambda function name"
  value       = aws_lambda_function.validate.function_name
}

output "validate_function_arn" {
  description = "Validate Lambda function ARN"
  value       = aws_lambda_function.validate.arn
}

output "suggest_function_name" {
  description = "Suggest Lambda function name"
  value       = aws_lambda_function.suggest.function_name
}

output "suggest_function_arn" {
  description = "Suggest Lambda function ARN"
  value       = aws_lambda_function.suggest.arn
}

output "generate_function_name" {
  description = "Generate Lambda function name"
  value       = aws_lambda_function.generate.function_name
}

output "generate_function_arn" {
  description = "Generate Lambda function ARN"
  value       = aws_lambda_function.generate.arn
}

output "refine_function_name" {
  description = "Refine Lambda function name"
  value       = aws_lambda_function.refine.function_name
}

output "refine_function_arn" {
  description = "Refine Lambda function ARN"
  value       = aws_lambda_function.refine.arn
}

output "lambda_layer_arn" {
  description = "Common Lambda layer ARN"
  value       = aws_lambda_layer_version.common_layer.arn
}

output "region" {
  description = "AWS region"
  value       = data.aws_region.current.name
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}
