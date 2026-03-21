# ============ Data Sources ============

data "aws_dynamodb_table" "transactions" {
  name = var.dynamodb_transactions_table_name
}
