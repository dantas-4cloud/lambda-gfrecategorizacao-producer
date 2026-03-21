# ============ CloudWatch Module Outputs ============

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.arn
}

output "error_alarm_arn" {
  description = "ARN of the error alarm"
  value       = aws_cloudwatch_metric_alarm.lambda_errors.arn
}

output "duration_alarm_arn" {
  description = "ARN of the duration alarm"
  value       = aws_cloudwatch_metric_alarm.lambda_duration.arn
}

output "throttles_alarm_arn" {
  description = "ARN of the throttles alarm"
  value       = aws_cloudwatch_metric_alarm.lambda_throttles.arn
}

output "concurrent_executions_alarm_arn" {
  description = "ARN of the concurrent executions alarm"
  value       = aws_cloudwatch_metric_alarm.lambda_concurrent_executions.arn
}
