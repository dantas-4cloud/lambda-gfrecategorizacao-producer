environment                         = "prod"
aws_region                          = "us-east-2"
lambda_memory_size                  = 512
lambda_timeout                      = 30
lambda_reserved_concurrency         = 5
dynamodb_transactions_table_name    = "GestaoFinanceira-Transacoes"
dynamodb_categorizations_table_name = "GestaoFinanceira-Categorizacoes"
dynamodb_billing_mode               = "PROVISIONED"
dynamodb_read_capacity              = 50
dynamodb_write_capacity             = 50
cloudwatch_log_retention_days       = 30
categorizer_endpoint                = "https://api.categorizer.example.com/api/v1/categorize"
categorizer_token                   = "prod-token-placeholder"

tags = {
  Environment = "production"
  CostCenter  = "Finance"
  Owner       = "Platform-Team"
  Backup      = "true"
  DSPM        = "true"
  Compliance  = "PCI-DSS"
}
