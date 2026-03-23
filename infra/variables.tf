# ============ AWS Configuration ============

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "environment" {
  description = "Environment name"
  type        = string

  validation {
    condition     = contains(["dev", "hom", "prod"], var.environment)
    error_message = "Environment must be dev, hom, or prod."
  }
}

# ============ Lambda Configuration ============

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
  default     = 2
}

# ============ DynamoDB Configuration ============

variable "dynamodb_transactions_table_name" {
  description = "DynamoDB transactions table name"
  type        = string
  default     = "GestaoFinanceira-Transacoes"
}

variable "dynamodb_categorizations_table_name" {
  description = "DynamoDB categorizations table name"
  type        = string
  default     = "GestaoFinanceira-Categorizacoes"
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

# ============ DynamoDB Event Source Configuration ============

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

# ============ CloudWatch Configuration ============

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.cloudwatch_log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period."
  }
}

variable "error_threshold" {
  description = "Error threshold for CloudWatch alarms"
  type        = number
  default     = 10
}

variable "duration_threshold_ms" {
  description = "Duration threshold in milliseconds for CloudWatch alarms"
  type        = number
  default     = 15000
}

variable "concurrent_execution_threshold" {
  description = "Concurrent execution threshold for CloudWatch alarms"
  type        = number
  default     = 80
}

variable "alarm_actions" {
  description = "List of SNS topic ARNs to notify on alarm"
  type        = list(string)
  default     = []
}

# ============ External Services ============

variable "categorizer_endpoint" {
  description = "External categorizer service endpoint"
  type        = string
}

variable "categorizer_token" {
  description = "External categorizer service token"
  type        = string
  sensitive   = true
}

# ============ Tags ============

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
