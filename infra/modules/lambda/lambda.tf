# ============ Archive Lambda Code ============

# modules/lambda/lambda.tf
data "archive_file" "lambda_zip" {
  type = "zip"
  # Use path.root para apontar para a pasta src no root do repositório
  source_dir  = "${path.root}/src"
  output_path = "${path.module}/lambda.zip"
}

# ============ Data Sources ============

data "aws_region" "current" {}
