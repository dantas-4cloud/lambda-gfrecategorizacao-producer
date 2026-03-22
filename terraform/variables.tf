variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, hom, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "hom", "prod"], var.environment)
    error_message = "Environment must be dev, hom, or prod."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "recategorization-producer"
}

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "recategorization-producer"
}

variable "lambda_handler" {
  description = "Lambda handler"
  type        = string
  default     = "lambda_handler.lambda_handler"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.12"
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 60
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 256
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    CostCenter = "Engineering"
    Team       = "Platform"
  }
}
