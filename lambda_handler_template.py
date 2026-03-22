"""
Lambda Handler - Template Base

Estrutura inicial para desenvolvimento de Lambda functions.
Esta é a base que será expandida com features em branches de desenvolvimento.

Fluxo:
  main (template base)
    ↓
  feature-flag (homolog - versões testadas)
    ↓
  develop (trabalho em progresso)
    ↓
  feature/* (features individuais)
"""

import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler main entry point

    This is the base template for the Lambda function.
    Expand this handler with your business logic in feature branches.

    Args:
        event: Lambda event (structure depends on trigger source)
        context: Lambda context object

    Returns:
        dict: Response with statusCode and body

    Example event from DynamoDB Stream:
        {
            "Records": [
                {
                    "eventID": "...",
                    "eventVersion": "1.0",
                    "dynamodb": {...},
                    "eventName": "INSERT|MODIFY|REMOVE",
                    "eventSource": "aws:dynamodb"
                }
            ]
        }
    """
    try:
        logger.info(f"Lambda invoked with event: {json.dumps(event)}")

        # Placeholder: Add your business logic here
        result = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Lambda template base - ready for development",
                    "event_received": bool(event),
                }
            ),
        }

        logger.info(f"Lambda response: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in Lambda handler: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }


# For local testing
if __name__ == "__main__":
    test_event = {
        "Records": [
            {
                "eventID": "test-event-1",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {"id": {"S": "test-id"}},
                    "NewImage": {
                        "id": {"S": "test-id"},
                        "data": {"S": "test-data"},
                    },
                },
                "eventName": "INSERT",
                "eventSource": "aws:dynamodb",
            }
        ]
    }

    response = handler(test_event, None)
    print(json.dumps(response, indent=2))
