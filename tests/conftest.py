"""
Pytest configuration and fixtures for Lambda tests.
"""

import pytest
from typing import Any, Dict, Generator


class MockContext:
    """Mock AWS Lambda context object for testing."""

    aws_request_id = "test-request-id-12345"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:us-east-2:123456789012:function:test-function"
    function_version = "$LATEST"
    function_name = "test-function"
    log_group_name = "/aws/lambda/test-function"
    log_stream_name = "2024/03/21/[$LATEST]abc123def456"


@pytest.fixture
def mock_context() -> MockContext:
    """Provide a mock Lambda context for tests."""
    return MockContext()


@pytest.fixture
def sample_event() -> Dict[str, Any]:
    """Provide a sample Lambda event for testing."""
    return {"test": "data", "nested": {"key": "value"}, "items": [1, 2, 3]}


@pytest.fixture
def dynamodb_stream_event() -> Dict[str, Any]:
    """Provide a sample DynamoDB Stream event."""
    return {
        "Records": [
            {
                "eventID": "1",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {"id": {"S": "test-id"}},
                    "NewImage": {
                        "id": {"S": "test-id"},
                        "amount": {"N": "100.50"},
                        "type": {"S": "CREDIT_CARD"},
                    },
                },
                "eventSource": "aws:dynamodb",
                "eventName": "INSERT",
                "awsRegion": "us-east-2",
            }
        ]
    }


@pytest.fixture
def api_gateway_event() -> Dict[str, Any]:
    """Provide a sample API Gateway event."""
    return {
        "resource": "/lambda",
        "path": "/lambda",
        "httpMethod": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": '{"test": "data"}',
        "isBase64Encoded": False,
    }
