# ============ Lambda Function ============

resource "aws_lambda_function" "recategorization_producer" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "recategorization-producer-${var.environment}"
  role          = var.lambda_role_arn
  handler       = "src.main.lambda_handler"
  runtime       = "python3.12"
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size
  architectures = ["arm64"] # Graviton
  publish       = true      # Automatically create versions

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT           = var.environment
      AWS_REGION            = data.aws_region.current.name
      CATEGORIZATIONS_TABLE = var.dynamodb_categorizations_table_name
      CATEGORIZER_ENDPOINT  = var.categorizer_endpoint
      CATEGORIZER_TOKEN     = var.categorizer_token
      LOG_LEVEL             = var.environment == "prod" ? "INFO" : "DEBUG"
    }
  }

  layers = [] # Adicionar layers se necessário (ex: DataDog)

  tracing_config {
    mode = "Active" # X-Ray tracing
  }

  tags = var.tags
}

# ============ Lambda Alias for Environment ============

resource "aws_lambda_alias" "recategorization_producer_live" {
  name             = "live"
  description      = "Live alias for ${var.environment}"
  function_name    = aws_lambda_function.recategorization_producer.function_name
  function_version = aws_lambda_function.recategorization_producer.version
}
