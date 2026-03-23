# ============ Archive Lambda Code ============

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/../../lambda_function.zip"
}

# ============ Data Sources ============

data "aws_region" "current" {}
