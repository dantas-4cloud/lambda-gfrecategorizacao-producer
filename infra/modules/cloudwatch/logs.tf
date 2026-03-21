# ============ CloudWatch Log Group ============

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}-${var.environment}"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = var.tags
}
