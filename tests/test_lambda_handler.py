"""
Tests for Lambda handler function.
"""

import json
import logging
from typing import Any, Dict

import pytest

from src.lambda_handler import lambda_handler


class TestLambdaHandlerBasic:
    """Test basic Lambda handler functionality."""

    def test_returns_200_on_success(self, mock_context, sample_event):
        """Test successful invocation returns 200."""
        response = lambda_handler(sample_event, mock_context)
        assert response["statusCode"] == 200

    def test_returns_dict(self, mock_context, sample_event):
        """Test response is a dictionary."""
        response = lambda_handler(sample_event, mock_context)
        assert isinstance(response, dict)

    def test_has_status_code(self, mock_context, sample_event):
        """Test response has statusCode."""
        response = lambda_handler(sample_event, mock_context)
        assert "statusCode" in response
        assert isinstance(response["statusCode"], int)

    def test_has_body(self, mock_context, sample_event):
        """Test response has body."""
        response = lambda_handler(sample_event, mock_context)
        assert "body" in response
        assert isinstance(response["body"], str)

    def test_body_is_valid_json(self, mock_context, sample_event):
        """Test body is valid JSON."""
        response = lambda_handler(sample_event, mock_context)
        body = json.loads(response["body"])
        assert isinstance(body, dict)

    def test_body_contains_message(self, mock_context, sample_event):
        """Test body contains message."""
        response = lambda_handler(sample_event, mock_context)
        body = json.loads(response["body"])
        assert "message" in body
        assert body["message"] == "Hello from AWS Lambda!"

    def test_body_contains_event(self, mock_context, sample_event):
        """Test body contains event."""
        response = lambda_handler(sample_event, mock_context)
        body = json.loads(response["body"])
        assert "event" in body
        assert body["event"] == sample_event


class TestLambdaHandlerEventTypes:
    """Test with different event types."""

    def test_with_empty_event(self, mock_context):
        """Test with empty event dict."""
        response = lambda_handler({}, mock_context)
        assert response["statusCode"] == 200

    def test_with_dynamodb_stream(self, mock_context, dynamodb_stream_event):
        """Test with DynamoDB Stream event."""
        response = lambda_handler(dynamodb_stream_event, mock_context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "Records" in body["event"]

    def test_with_api_gateway(self, mock_context, api_gateway_event):
        """Test with API Gateway event."""
        response = lambda_handler(api_gateway_event, mock_context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["event"]["httpMethod"] == "POST"

    def test_with_simple_dict(self, mock_context):
        """Test with simple dict event."""
        event = {"test": "data", "number": 42}
        response = lambda_handler(event, mock_context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["event"]["test"] == "data"
        assert body["event"]["number"] == 42


class TestLambdaHandlerEdgeCases:
    """Test edge cases."""

    def test_with_large_payload(self, mock_context):
        """Test with large event payload."""
        large_event = {"items": ["x" * 100 for _ in range(100)]}
        response = lambda_handler(large_event, mock_context)
        assert response["statusCode"] == 200

    def test_with_nested_dict(self, mock_context):
        """Test with nested dictionary."""
        nested = {"level1": {"level2": {"level3": {"value": "deep"}}}}
        response = lambda_handler(nested, mock_context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["event"]["level1"]["level2"]["level3"]["value"] == "deep"

    def test_with_unicode_chars(self, mock_context):
        """Test with unicode characters."""
        event = {"emoji": "🚀", "chinese": "你好", "arabic": "مرحبا"}
        response = lambda_handler(event, mock_context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["event"]["emoji"] == "🚀"

    def test_with_special_chars(self, mock_context):
        """Test with special characters."""
        event = {
            "special": "!@#$%^&*()",
            "quotes": "Test \"quotes\" and 'apostrophes'",
            "newline": "line1\nline2",
        }
        response = lambda_handler(event, mock_context)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["event"]["special"] == "!@#$%^&*()"


class TestLambdaHandlerLogging:
    """Test logging behavior."""

    def test_logs_event_received(self, mock_context, sample_event, caplog):
        """Test that event receipt is logged."""
        with caplog.at_level(logging.INFO):
            lambda_handler(sample_event, mock_context)
        assert "Evento recebido" in caplog.text

    def test_logs_processing_complete(self, mock_context, sample_event, caplog):
        """Test that processing completion is logged."""
        with caplog.at_level(logging.INFO):
            lambda_handler(sample_event, mock_context)
        assert "Processing complete" in caplog.text
        assert "Hello from AWS Lambda!" in caplog.text


class TestLambdaHandlerContextHandling:
    """Test context parameter handling."""

    def test_accepts_mock_context(self, sample_event):
        """Test handler accepts mock context."""
        from tests.conftest import MockContext

        context = MockContext()
        response = lambda_handler(sample_event, context)
        assert response["statusCode"] == 200

    def test_with_real_context_attributes(self, mock_context, sample_event):
        """Test handler works with context object."""
        # Just ensure handler doesn't fail
        response = lambda_handler(sample_event, mock_context)
        assert response is not None
        assert response["statusCode"] == 200


class TestLambdaHandlerIntegration:
    """Integration tests."""

    def test_multiple_invocations(self, mock_context):
        """Test multiple sequential invocations."""
        for i in range(3):
            event = {"run": i}
            response = lambda_handler(event, mock_context)
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert body["event"]["run"] == i

    def test_event_preservation(self, mock_context):
        """Test that events are preserved exactly."""
        event = {
            "id": "12345",
            "timestamp": "2024-03-21T12:00:00Z",
            "data": {"nested": {"value": True}},
        }
        response = lambda_handler(event, mock_context)
        body = json.loads(response["body"])
        assert body["event"] == event

    def test_standard_response_format(self, mock_context):
        """Test standard AWS Lambda response format."""
        response = lambda_handler({"test": "data"}, mock_context)

        # AWS Lambda standard response format
        assert "statusCode" in response
        assert "body" in response
        assert response["statusCode"] in [200, 201, 400, 403, 404, 500]

        # Body should be JSON string for API Gateway
        body = json.loads(response["body"])
        assert isinstance(body, dict)
