# ============ IAM Module Variables ============

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "dynamodb_transactions_table_name" {
  description = "DynamoDB transactions table name"
  type        = string
}

variable "dynamodb_categorizations_table_name" {
  description = "DynamoDB categorizations table name"
  type        = string
}

variable "tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default     = {}
}
