# DynamoDB Table for diagram history
resource "aws_dynamodb_table" "diagram_history" {
  count = var.enable_dynamodb ? 1 : 0
  
  name           = "${var.project_name}-diagram-history-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"
  range_key      = "version"
  
  attribute {
    name = "session_id"
    type = "S"
  }
  
  attribute {
    name = "version"
    type = "N"
  }
  
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  
  point_in_time_recovery {
    enabled = true
  }
  
  tags = {
    Name        = "${var.project_name}-diagram-history"
    Environment = var.environment
  }
}
