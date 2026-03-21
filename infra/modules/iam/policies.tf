# ============ CloudWatch Logs Policy ============

resource "aws_iam_role_policy" "lambda_logs_policy" {
  name = "recategorization-producer-logs-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/recategorization-producer-${var.environment}:*"
      }
    ]
  })
}

# ============ DynamoDB Read Permissions ============

resource "aws_iam_role_policy" "lambda_dynamodb_read_policy" {
  name = "recategorization-producer-dynamodb-read-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetRecords",
          "dynamodb:GetItem",
          "dynamodb:DescribeStream",
          "dynamodb:ListStreams",
          "dynamodb:ListShards"
        ]
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_transactions_table_name}/stream/*"
      }
    ]
  })
}

# ============ DynamoDB Write Permissions ============

resource "aws_iam_role_policy" "lambda_dynamodb_write_policy" {
  name = "recategorization-producer-dynamodb-write-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${var.dynamodb_categorizations_table_name}"
      }
    ]
  })
}

# ============ X-Ray Write Permissions ============

resource "aws_iam_role_policy" "lambda_xray_policy" {
  name = "recategorization-producer-xray-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })
}

# ============ Data Sources ============

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
