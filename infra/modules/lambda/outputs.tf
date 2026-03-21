# ============ Lambda Module Outputs ============

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.recategorization_producer.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.recategorization_producer.arn
}

output "lambda_function_qualified_arn" {
  description = "Qualified ARN of the Lambda function"
  value       = aws_lambda_alias.recategorization_producer_live.arn
}

output "lambda_function_version" {
  description = "Version of the Lambda function"
  value       = aws_lambda_function.recategorization_producer.version
}

output "lambda_function_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.recategorization_producer.invoke_arn
}
