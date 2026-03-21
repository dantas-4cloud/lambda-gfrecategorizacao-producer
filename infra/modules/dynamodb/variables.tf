# ============ DynamoDB Module Variables ============

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "dynamodb_categorizations_table_name" {
  description = "DynamoDB categorizations table name"
  type        = string
}

variable "dynamodb_transactions_table_name" {
  description = "DynamoDB transactions table name"
  type        = string
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode"
  type        = string

  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.dynamodb_billing_mode)
    error_message = "Billing mode must be PAY_PER_REQUEST or PROVISIONED."
  }
}

variable "dynamodb_read_capacity" {
  description = "DynamoDB read capacity units (for PROVISIONED mode)"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "DynamoDB write capacity units (for PROVISIONED mode)"
  type        = number
  default     = 5
}

variable "lambda_function_arn" {
  description = "ARN of the Lambda function"
  type        = string
}

variable "event_batch_size" {
  description = "Batch size for DynamoDB stream events"
  type        = number
  default     = 100
}

variable "event_batching_window_seconds" {
  description = "Maximum batching window in seconds"
  type        = number
  default     = 30
}

variable "event_parallelization_factor" {
  description = "Number of batches to process in parallel"
  type        = number
  default     = 10
}

variable "event_starting_position" {
  description = "Starting position for event source mapping"
  type        = string
  default     = "LATEST"
}

variable "tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
