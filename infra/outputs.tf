# ============ Lambda Outputs ============

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = module.lambda.lambda_function_arn
}

output "lambda_function_qualified_arn" {
  description = "Lambda function qualified ARN (with alias)"
  value       = module.lambda.lambda_function_qualified_arn
}

# ============ IAM Outputs ============

output "lambda_role_arn" {
  description = "Lambda IAM role ARN"
  value       = module.iam.lambda_role_arn
}

output "lambda_role_name" {
  description = "Lambda IAM role name"
  value       = module.iam.lambda_role_name
}

# ============ DynamoDB Outputs ============

output "dynamodb_categorizations_table_name" {
  description = "DynamoDB categorizations table name"
  value       = module.dynamodb.categorizations_table_name
}

output "dynamodb_categorizations_table_arn" {
  description = "DynamoDB categorizations table ARN"
  value       = module.dynamodb.categorizations_table_arn
}

output "dynamodb_categorizations_table_stream_arn" {
  description = "DynamoDB categorizations table stream ARN"
  value       = module.dynamodb.categorizations_table_stream_arn
}

output "event_source_mapping_uuid" {
  description = "Event source mapping UUID"
  value       = module.dynamodb.event_source_mapping_uuid
}

# ============ CloudWatch Outputs ============

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name"
  value       = module.cloudwatch.log_group_name
}

output "cloudwatch_log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = module.cloudwatch.log_group_arn
}

output "error_alarm_arn" {
  description = "Error metric alarm ARN"
  value       = module.cloudwatch.error_alarm_arn
}

output "duration_alarm_arn" {
  description = "Duration metric alarm ARN"
  value       = module.cloudwatch.duration_alarm_arn
}

output "throttles_alarm_arn" {
  description = "Throttles metric alarm ARN"
  value       = module.cloudwatch.throttles_alarm_arn
}

output "concurrent_executions_alarm_arn" {
  description = "Concurrent executions metric alarm ARN"
  value       = module.cloudwatch.concurrent_executions_alarm_arn
}
