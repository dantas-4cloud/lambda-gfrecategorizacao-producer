"""
AWS Lambda Handler - Template Básico
Template padrão da AWS para Python em Lambda
"""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function - ponto de entrada da função Lambda.

    Args:
        event: Evento disparado pelo AWS Lambda
        context: Contexto da execução (ID da requisição, memory limit, etc)

    Returns:
        Dict com statusCode e body

    Example:
        {
            'statusCode': 200,
            'body': JSON stringify da resposta
        }
    """
    logger.info(f"Evento recebido: {json.dumps(event)}")

    try:
        # Processamento básico
        message = "Hello from AWS Lambda!"

        logger.info(f"Processing complete: {message}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": message,
                    "event": event,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Erro ao processar evento: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": str(e),
                }
            ),
        }


# Para testes locais
if __name__ == "__main__":
    test_event = {"test": "data"}

    class MockContext:
        aws_request_id = "local-test"
        memory_limit_in_mb = 128

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
