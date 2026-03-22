environment                         = "dev"
aws_region                          = "us-east-2"
lambda_memory_size                  = 256
lambda_timeout                      = 5
lambda_reserved_concurrency         = 2
dynamodb_transactions_table_name    = "GestaoFinanceira-Transacoes-dev"
dynamodb_categorizations_table_name = "GestaoFinanceira-Categorizacoes-dev"
dynamodb_billing_mode               = "PAY_PER_REQUEST"
cloudwatch_log_retention_days       = 7
categorizer_endpoint                = "https://api-dev.categorizer.example.com/api/v1/categorize"
categorizer_token                   = "dev-token-placeholder"

tags = {
  Environment = "dev"
  CostCenter  = "Engineering"
  Owner       = "Platform-Team"
}
