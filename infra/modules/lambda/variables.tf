# ============ Lambda Module Variables ============

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  type        = string
}

variable "lambda_memory_size" {
  description = "Lambda memory in MB"
  type        = number

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "Lambda memory must be between 128 and 10240 MB."
  }
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 30

  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 1 and 900 seconds."
  }
}

variable "lambda_reserved_concurrency" {
  description = "Lambda reserved concurrency"
  type        = number
  default     = 100
}

variable "dynamodb_categorizations_table_name" {
  description = "DynamoDB categorizations table name"
  type        = string
}

variable "categorizer_endpoint" {
  description = "External categorizer service endpoint"
  type        = string
}

variable "categorizer_token" {
  description = "External categorizer service token"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
