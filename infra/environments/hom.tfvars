environment                         = "hom"
aws_region                          = "us-east-1"
lambda_memory_size                  = 256
lambda_timeout                      = 30
lambda_reserved_concurrency         = 25
dynamodb_transactions_table_name    = "GestaoFinanceira-Transacoes-hom"
dynamodb_categorizations_table_name = "GestaoFinanceira-Categorizacoes-hom"
dynamodb_billing_mode               = "PROVISIONED"
dynamodb_read_capacity              = 10
dynamodb_write_capacity             = 10
cloudwatch_log_retention_days       = 14
categorizer_endpoint                = "https://api-hom.categorizer.example.com/api/v1/categorize"
categorizer_token                   = "hom-token-placeholder"

tags = {
  Environment = "homolog"
  CostCenter  = "Engineering"
  Owner       = "Platform-Team"
  Backup      = "true"
}
