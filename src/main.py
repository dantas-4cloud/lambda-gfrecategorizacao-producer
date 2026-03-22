"""
Lambda handler consolidado para recategorização de eventos
Consolida: lambda_handler + event_processor + categorizer_service + dynamodb_service
"""
import os
import time
from typing import Any, Dict

import boto3
import requests
from botocore.exceptions import ClientError
from requests.exceptions import RequestException, Timeout

from src.config import log_error, log_info, log_warning
from src.models import Categorization, Transaction

# Clients AWS - Inicializados uma única vez ao importar o módulo
# Nota: Recomendado inicializar fora do Lambda handler para reutilizar conexões
_dynamodb_client = boto3.client(
    "dynamodb",
    region_name=os.environ.get("AWS_REGION", "us-east-2"),
    config=boto3.session.Config(connect_timeout=5, read_timeout=5),
)


def get_dynamodb_client():
    """Retorna cliente DynamoDB pré-inicializado"""
    return _dynamodb_client


# Configurações
CATEGORIZER_ENDPOINT = os.environ.get(
    "CATEGORIZER_ENDPOINT", "https://categorizer.example.com/api/v1/categorize"
)
CATEGORIZER_TOKEN = os.environ.get("CATEGORIZER_TOKEN", "")
CATEGORIZATIONS_TABLE = os.environ.get("CATEGORIZATIONS_TABLE", "GestaoFinanceira-Categorizacoes")

# Retry config
MAX_RETRIES = 3
BASE_DELAY = 0.5
CATEGORIZER_TIMEOUT = 5


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal da Lambda

    Processa eventos de DynamoDB Streams e categoriza transações

    Args:
        event: Evento de DynamoDB Streams
        context: Contexto da Lambda AWS

    Returns:
        dict: Resposta estruturada com status e resultados
    """
    try:
        records = event.get("Records", [])

        log_info("processing_dynamodb_stream", record_count=len(records))

        if not records:
            log_warning("empty_records_in_event")
            return build_success_response([], 0)

        categorized_transactions = []
        processed_count = 0
        error_count = 0

        for record in records:
            try:
                # Valida evento
                validate_record(record)

                # Extrai transação do DynamoDB NewImage
                transaction = extract_transaction(record)

                # Obtém preferências do usuário
                user_preferences = get_user_preferences(transaction.user_id)

                # Chama categorizador
                categorization = categorize_transaction(transaction, user_preferences)

                # Persiste resultado
                persist_categorization(categorization)

                categorized_transactions.append(categorization.to_dict())
                processed_count += 1

            except ValueError as e:
                log_warning("validation_error_in_record", error=str(e))
                error_count += 1

            except (RequestException, ClientError) as e:
                log_error("service_error", exception=e)
                error_count += 1

        log_info(
            "event_processing_completed",
            processed=processed_count,
            errors=error_count,
            total=len(records),
        )

        return build_success_response(categorized_transactions, processed_count)

    except Exception as e:
        log_error("unexpected_error_processing_event", exception=e)
        return build_error_response("INTERNAL_ERROR", str(e))


def validate_record(record: Dict[str, Any]) -> None:
    """
    Valida estrutura do record do DynamoDB Stream

    Args:
        record: Record do stream

    Raises:
        ValueError: Se estrutura inválida
    """
    if "dynamodb" not in record:
        raise ValueError("Missing 'dynamodb' key in record")

    if "NewImage" not in record.get("dynamodb", {}):
        raise ValueError("Missing 'NewImage' in dynamodb event")

    event_name = record.get("eventName", "")
    if event_name not in ["INSERT", "MODIFY"]:
        raise ValueError(f"Unsupported event type: {event_name}")


def extract_transaction(record: Dict[str, Any]) -> Transaction:
    """
    Extrai transação do record do DynamoDB

    Args:
        record: Record do stream

    Returns:
        Transaction: Transação validada

    Raises:
        ValueError: Se dados inválidos
    """
    try:
        new_image = record["dynamodb"]["NewImage"]
        transaction = Transaction.from_dynamodb(new_image)
        return transaction

    except ValueError as e:
        raise ValueError(f"Invalid transaction data: {str(e)}")


def categorize_transaction(
    transaction: Transaction, user_preferences: Dict[str, Any]
) -> Categorization:
    """
    Categoriza transação chamando API externa

    Implementa retry com backoff exponencial

    Args:
        transaction: Transação a categorizar
        user_preferences: Preferências do usuário

    Returns:
        Categorization: Resultado da categorização

    Raises:
        RuntimeError: Se falhar após retries
    """
    payload = {
        "transaction_id": transaction.transaction_id,
        "user_id": transaction.user_id,
        "amount": transaction.amount,
        "merchant": transaction.merchant,
        "description": transaction.description,
        "type": transaction.transaction_type.value,
        "user_preferences": user_preferences,
    }

    headers = {
        "Authorization": f"Bearer {CATEGORIZER_TOKEN}",
        "Content-Type": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                CATEGORIZER_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=CATEGORIZER_TIMEOUT,
            )

            response.raise_for_status()

            # Sucesso
            data = response.json()
            categorization = parse_categorizer_response(transaction, data)

            log_info(
                "categorization_completed_successfully",
                transaction_id=transaction.transaction_id,
                new_category=categorization.new_category,
                confidence=categorization.confidence,
            )

            return categorization

        except Timeout:
            if attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2**attempt)
                log_warning(
                    "categorizer_timeout_retrying",
                    transaction_id=transaction.transaction_id,
                    attempt=attempt + 1,
                    delay_seconds=delay,
                )
                time.sleep(delay)
                continue

            log_error(
                "categorizer_timeout_after_retries",
                transaction_id=transaction.transaction_id,
                timeout_seconds=CATEGORIZER_TIMEOUT,
                max_attempts=MAX_RETRIES,
            )
            raise RuntimeError(f"Categorizer timeout after {MAX_RETRIES} attempts")

        except RequestException as e:
            log_error(
                "categorizer_request_failed",
                exception=e,
                transaction_id=transaction.transaction_id,
                attempt=attempt + 1,
            )

            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Categorizer service error: {str(e)}")

            delay = BASE_DELAY * (2**attempt)
            time.sleep(delay)

    raise RuntimeError("Failed to categorize transaction")


def parse_categorizer_response(
    transaction: Transaction, response: Dict[str, Any]
) -> Categorization:
    """
    Parse resposta do categorizador

    Args:
        transaction: Transação original
        response: Resposta da API

    Returns:
        Categorization: Objeto de categorização

    Raises:
        ValueError: Se resposta inválida
    """
    try:
        if "categorization" not in response:
            raise ValueError("Missing 'categorization' in response")

        categorization_data = response.get("categorization", {})

        return Categorization(
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            original_category="UNCATEGORIZED",
            new_category=categorization_data.get("category", "UNCATEGORIZED"),
            confidence=float(categorization_data.get("confidence", 0.0)),
            rules_applied=tuple(categorization_data.get("rules_applied", [])),
        )
    except (KeyError, ValueError, TypeError) as e:
        log_error("failed_to_parse_categorizer_response", exception=e, response=response)
        raise ValueError(f"Invalid categorizer response: {str(e)}")


def get_user_preferences(_user_id: str) -> Dict[str, Any]:
    return {
        "preferred_categories": ["Food", "Transport", "Entertainment"],
        "category_overrides": {"Starbucks": "Coffee"},
    }


def persist_categorization(categorization: Categorization) -> bool:
    client = get_dynamodb_client()
    item = categorization.to_dynamodb_item()

    for attempt in range(MAX_RETRIES):
        try:
            client.put_item(TableName=CATEGORIZATIONS_TABLE, Item=item)
            log_info(
                "categorization_persisted_successfully",
                transaction_id=categorization.transaction_id,
                new_category=categorization.new_category,
            )
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            # Throttling - retry com delay
            if error_code == "ProvisionedThroughputExceededException":
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY * (2**attempt)
                    log_warning(
                        "dynamodb_throttled_retrying",
                        transaction_id=categorization.transaction_id,
                        attempt=attempt + 1,
                        delay_seconds=delay,
                    )
                    time.sleep(delay)
                    continue
                else:
                    log_error(
                        "dynamodb_throttled_after_retries",
                        exception=e,
                        transaction_id=categorization.transaction_id,
                        max_attempts=MAX_RETRIES,
                    )
                    raise RuntimeError(f"DynamoDB throttled after {MAX_RETRIES} attempts")

            # Outros erros - não retry
            log_error(
                "failed_to_persist_categorization",
                exception=e,
                error_code=error_code,
                transaction_id=categorization.transaction_id,
            )
            raise RuntimeError(f"DynamoDB error: {error_code}")

    raise RuntimeError("Failed to persist categorization after retries")


def build_success_response(categorized_transactions: list, processed_count: int) -> Dict[str, Any]:
    """Constrói payload de sucesso"""
    return {
        "status": "SUCCESS",
        "processed_transactions": processed_count,
        "records": categorized_transactions,
    }


def build_error_response(error_code: str, error_message: str) -> Dict[str, Any]:
    """Constrói payload de erro"""
    return {
        "status": "ERROR",
        "error_code": error_code,
        "error_message": error_message,
    }
