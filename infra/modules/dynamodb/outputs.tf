# ============ DynamoDB Module Outputs ============

output "categorizations_table_name" {
  description = "Name of the DynamoDB categorizations table"
  value       = aws_dynamodb_table.categorizations.name
}

output "categorizations_table_arn" {
  description = "ARN of the DynamoDB categorizations table"
  value       = aws_dynamodb_table.categorizations.arn
}

output "categorizations_table_stream_arn" {
  description = "Stream ARN of the DynamoDB categorizations table"
  value       = aws_dynamodb_table.categorizations.stream_arn
}

output "event_source_mapping_uuid" {
  description = "UUID of the Lambda DynamoDB event source mapping"
  value       = aws_lambda_event_source_mapping.dynamodb_stream.uuid
}
