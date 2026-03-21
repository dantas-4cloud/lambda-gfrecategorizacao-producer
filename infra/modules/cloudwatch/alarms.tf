# ============ CloudWatch Alarms ============

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "recategorization-producer-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = var.error_threshold
  alarm_description   = "Alert when lambda errors exceed ${var.error_threshold} in 5 minutes"

  dimensions = {
    FunctionName = var.lambda_function_name
  }

  alarm_actions      = var.alarm_actions
  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "recategorization-producer-duration-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = var.duration_threshold_ms
  alarm_description   = "Alert when lambda duration exceeds ${var.duration_threshold_ms}ms"

  dimensions = {
    FunctionName = var.lambda_function_name
  }

  alarm_actions      = var.alarm_actions
  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "recategorization-producer-throttles-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when lambda is throttled"

  dimensions = {
    FunctionName = var.lambda_function_name
  }

  alarm_actions      = var.alarm_actions
  treat_missing_data = "notBreaching"

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "lambda_concurrent_executions" {
  alarm_name          = "recategorization-producer-concurrent-executions-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ConcurrentExecutions"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Maximum"
  threshold           = var.concurrent_execution_threshold
  alarm_description   = "Alert when concurrent executions exceed ${var.concurrent_execution_threshold}"

  dimensions = {
    FunctionName = var.lambda_function_name
  }

  alarm_actions      = var.alarm_actions
  treat_missing_data = "notBreaching"

  tags = var.tags
}
