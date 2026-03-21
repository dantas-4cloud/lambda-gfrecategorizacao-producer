# ============ IAM Module ============

module "iam" {
  source = "./modules/iam"

  environment                         = var.environment
  dynamodb_transactions_table_name    = var.dynamodb_transactions_table_name
  dynamodb_categorizations_table_name = var.dynamodb_categorizations_table_name
  tags                                = local.common_tags
}

# ============ Lambda Module ============

module "lambda" {
  source = "./modules/lambda"

  environment                         = var.environment
  lambda_role_arn                     = module.iam.lambda_role_arn
  lambda_memory_size                  = var.lambda_memory_size
  lambda_timeout                      = var.lambda_timeout
  lambda_reserved_concurrency         = var.lambda_reserved_concurrency
  dynamodb_categorizations_table_name = var.dynamodb_categorizations_table_name
  categorizer_endpoint                = var.categorizer_endpoint
  categorizer_token                   = var.categorizer_token
  tags                                = local.common_tags
}

# ============ DynamoDB Module ============

module "dynamodb" {
  source = "./modules/dynamodb"

  environment                         = var.environment
  dynamodb_categorizations_table_name = var.dynamodb_categorizations_table_name
  dynamodb_transactions_table_name    = var.dynamodb_transactions_table_name
  dynamodb_billing_mode               = var.dynamodb_billing_mode
  dynamodb_read_capacity              = var.dynamodb_read_capacity
  dynamodb_write_capacity             = var.dynamodb_write_capacity
  lambda_function_arn                 = module.lambda.lambda_function_arn
  event_batch_size                    = var.event_batch_size
  event_batching_window_seconds       = var.event_batching_window_seconds
  event_parallelization_factor        = var.event_parallelization_factor
  event_starting_position             = var.event_starting_position
  tags                                = local.common_tags
}

# ============ CloudWatch Module ============

module "cloudwatch" {
  source = "./modules/cloudwatch"

  environment                    = var.environment
  lambda_function_name           = module.lambda.lambda_function_name
  cloudwatch_log_retention_days  = var.cloudwatch_log_retention_days
  error_threshold                = var.error_threshold
  duration_threshold_ms          = var.duration_threshold_ms
  concurrent_execution_threshold = var.concurrent_execution_threshold
  alarm_actions                  = var.alarm_actions
  tags                           = local.common_tags
}

# ============ Local Values ============

locals {
  common_tags = merge(
    var.tags,
    {
      Project     = "RecategorizationProducer"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}
