# ============ Event Source Mapping ============

resource "aws_lambda_event_source_mapping" "dynamodb_stream" {
  event_source_arn                   = data.aws_dynamodb_table.transactions.stream_arn
  function_name                      = var.lambda_function_arn
  enabled                            = true
  batch_size                         = var.event_batch_size
  maximum_batching_window_in_seconds = var.event_batching_window_seconds
  parallelization_factor             = var.event_parallelization_factor
  starting_position                  = var.event_starting_position
  function_response_types            = ["ReportBatchItemFailures"]
}
