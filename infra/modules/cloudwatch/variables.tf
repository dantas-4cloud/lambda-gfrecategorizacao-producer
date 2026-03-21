# ============ CloudWatch Module Variables ============

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.cloudwatch_log_retention_days)
    error_message = "Log retention must be a valid CloudWatch retention period."
  }
}

variable "error_threshold" {
  description = "Error threshold for CloudWatch alarm"
  type        = number
  default     = 10
}

variable "duration_threshold_ms" {
  description = "Duration threshold in milliseconds for CloudWatch alarm"
  type        = number
  default     = 15000 # 15 seconds
}

variable "concurrent_execution_threshold" {
  description = "Concurrent execution threshold for CloudWatch alarm"
  type        = number
  default     = 80
}

variable "alarm_actions" {
  description = "List of ARNs to notify when alarm triggers"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
