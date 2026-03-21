# ============ Lambda Reserved Concurrency ============

resource "aws_lambda_provisioned_concurrency_config" "recategorization_producer_concurrency" {
  count                             = var.lambda_reserved_concurrency > 0 ? 1 : 0
  function_name                     = aws_lambda_function.recategorization_producer.function_name
  provisioned_concurrent_executions = var.lambda_reserved_concurrency
  qualifier                         = aws_lambda_function.recategorization_producer.version
}
