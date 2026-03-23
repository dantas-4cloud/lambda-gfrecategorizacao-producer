# ============ DynamoDB Categorizations Table ============

resource "aws_dynamodb_table" "categorizations" {
  name             = var.dynamodb_categorizations_table_name
  billing_mode     = var.dynamodb_billing_mode
  hash_key         = "transaction_id"
  range_key        = "timestamp"
  read_capacity    = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
  write_capacity   = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  # Attributes
  attribute {
    name = "transaction_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # GSI for user queries
  global_secondary_index {
    name            = "user-id-timestamp-index"
    hash_key        = "user_id"
    range_key       = "timestamp"
    projection_type = "ALL"
    read_capacity   = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_read_capacity : null
    write_capacity  = var.dynamodb_billing_mode == "PROVISIONED" ? var.dynamodb_write_capacity : null
  }

  # TTL para auto-cleanup (90 dias)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery (prod only)
  point_in_time_recovery {
    enabled = var.environment == "prod"
  }

  tags = var.tags
}
