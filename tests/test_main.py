"""Testes consolidados para o sistema de recategorização"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, Timeout

from src.main import (
    categorize_transaction,
    extract_transaction,
    lambda_handler,
    parse_categorizer_response,
    persist_categorization,
    validate_record,
)
from src.models import Categorization, Transaction, TransactionType

# ============ Test Constants ============

EXPECTED_RULES_COUNT = 2
EXPECTED_RETRY_ATTEMPT_COUNT = 2


# ============ Fixtures ============


@pytest.fixture
def mock_context():
    """Lambda context mock"""
    context = Mock()
    context.function_name = "recategorization-producer"
    context.request_id = "test-request-id"
    context.get_remaining_time_in_millis = Mock(return_value=30000)
    return context


@pytest.fixture
def valid_transaction():
    """Transação de teste válida"""
    return Transaction(
        transaction_id="txn_test",
        user_id="usr_test",
        transaction_type=TransactionType.CREDIT_CARD,
        amount=100.0,
        merchant="Test Store",
        description="Test Purchase",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    )


@pytest.fixture
def valid_dynamodb_stream_event():
    """Event válido do DynamoDB Stream"""
    return {
        "Records": [
            {
                "eventID": "test-event-id",
                "eventVersion": "1.0",
                "dynamodb": {
                    "Keys": {"transaction_id": {"S": "txn_abc123"}},
                    "NewImage": {
                        "transaction_id": {"S": "txn_abc123"},
                        "user_id": {"S": "usr_def456"},
                        "type": {"S": "CREDIT_CARD"},
                        "amount": {"N": "150.50"},
                        "merchant": {"S": "Test Store"},
                        "description": {"S": "Test Purchase"},
                        "timestamp": {
                            "S": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                        },
                    },
                },
                "eventName": "INSERT",
                "eventSource": "aws:dynamodb",
            }
        ]
    }


@pytest.fixture
def empty_records_event():
    """Event com records vazios"""
    return {"Records": []}


# ============ Test Validation ============


class TestValidation:
    """Testes para validação de records"""

    def test_validate_record_valid(self, valid_dynamodb_stream_event):
        """Deve validar record válido"""
        record = valid_dynamodb_stream_event["Records"][0]
        # Não deve lançar exceção
        validate_record(record)

    def test_validate_record_missing_dynamodb_key(self):
        """Deve lançar ValueError se falta 'dynamodb'"""
        record = {"eventName": "INSERT"}

        with pytest.raises(ValueError, match="Missing 'dynamodb'"):
            validate_record(record)

    def test_validate_record_missing_newimage(self):
        """Deve lançar ValueError se falta 'NewImage'"""
        record = {
            "eventName": "INSERT",
            "dynamodb": {},  # Sem NewImage
        }

        with pytest.raises(ValueError, match="Missing 'NewImage'"):
            validate_record(record)

    def test_validate_record_unsupported_event_type(self):
        """Deve lançar ValueError para tipos não suportados"""
        record = {
            "eventName": "REMOVE",  # Não suportado
            "dynamodb": {"NewImage": {}},
        }

        with pytest.raises(ValueError, match="Unsupported event type"):
            validate_record(record)


# ============ Test Transaction Extraction ============


class TestTransactionExtraction:
    """Testes para extração de transações"""

    def test_extract_valid_transaction(self, valid_dynamodb_stream_event):
        """Deve extrair transação válida"""
        record = valid_dynamodb_stream_event["Records"][0]

        transaction = extract_transaction(record)

        assert transaction.transaction_id == "txn_abc123"
        assert transaction.user_id == "usr_def456"
        assert transaction.amount == pytest.approx(150.50)

    def test_extract_transaction_missing_fields(self):
        """Deve lançar ValueError se dados inválidos"""
        record = {
            "dynamodb": {
                "NewImage": {
                    "transaction_id": {"S": "txn_123"},
                    # Faltam outros campos obrigatórios
                }
            }
        }

        with pytest.raises(ValueError):
            extract_transaction(record)


# ============ Test Transaction Model ============


class TestTransactionModel:
    """Testes para o modelo Transaction"""

    def test_create_valid_transaction(self):
        """Deve criar transação válida"""
        txn = Transaction(
            transaction_id="txn_123",
            user_id="usr_456",
            transaction_type=TransactionType.CREDIT_CARD,
            amount=100.0,
            merchant="Store",
            description="Purchase",
            timestamp="2024-12-11T10:30:00Z",
        )

        assert txn.transaction_id == "txn_123"
        assert txn.amount == pytest.approx(100.0)
        assert txn.transaction_type == TransactionType.CREDIT_CARD

    def test_transaction_immutable(self):
        """Transaction deve ser imutável (frozen)"""
        txn = Transaction(
            transaction_id="txn_123",
            user_id="usr_456",
            transaction_type=TransactionType.CREDIT_CARD,
            amount=100.0,
            merchant="Store",
            description="Purchase",
            timestamp="2024-12-11T10:30:00Z",
        )

        with pytest.raises(Exception):  # dataclass frozen levanta FrozenInstanceError
            txn.amount = 200.0

    def test_transaction_missing_id_raises_error(self):
        """Deve lançar ValueError se transaction_id vazio"""
        with pytest.raises(ValueError, match="transaction_id é obrigatório"):
            Transaction(
                transaction_id="",
                user_id="usr_456",
                transaction_type=TransactionType.CREDIT_CARD,
                amount=100.0,
                merchant="Store",
                description="Purchase",
                timestamp="2024-12-11T10:30:00Z",
            )

    def test_transaction_zero_amount_raises_error(self):
        """Deve lançar ValueError se amount <= 0"""
        with pytest.raises(ValueError, match="amount deve ser maior que zero"):
            Transaction(
                transaction_id="txn_123",
                user_id="usr_456",
                transaction_type=TransactionType.CREDIT_CARD,
                amount=0,
                merchant="Store",
                description="Purchase",
                timestamp="2024-12-11T10:30:00Z",
            )

    def test_transaction_to_dict(self):
        """Deve converter para dict"""
        txn = Transaction(
            transaction_id="txn_123",
            user_id="usr_456",
            transaction_type=TransactionType.PIX,
            amount=150.50,
            merchant="João",
            description="Pagamento",
            timestamp="2024-12-11T10:30:00Z",
        )

        result = txn.to_dict()

        assert result["transaction_id"] == "txn_123"
        assert result["type"] == "PIX"
        assert result["amount"] == pytest.approx(150.50)

    def test_transaction_from_dynamodb(self):
        """Deve parsear item DynamoDB"""
        item = {
            "transaction_id": {"S": "txn_abc"},
            "user_id": {"S": "usr_def"},
            "type": {"S": "CREDIT_CARD"},
            "amount": {"N": "99.99"},
            "merchant": {"S": "Store"},
            "description": {"S": "Purchase"},
            "timestamp": {"S": "2024-12-11T10:30:00Z"},
        }

        txn = Transaction.from_dynamodb(item)

        assert txn.transaction_id == "txn_abc"
        assert txn.user_id == "usr_def"
        assert txn.amount == pytest.approx(99.99)


# ============ Test Categorization Model ============


class TestCategorizationModel:
    """Testes para modelo Categorization"""

    def test_create_valid_categorization(self):
        """Deve criar categorização válida"""
        cat = Categorization(
            transaction_id="txn_123",
            user_id="usr_456",
            original_category="UNCATEGORIZED",
            new_category="ALIMENTACAO",
            confidence=0.95,
            rules_applied=("rule1", "rule2"),
        )

        assert cat.new_category == "ALIMENTACAO"
        assert cat.confidence == pytest.approx(0.95)
        assert len(cat.rules_applied) == EXPECTED_RULES_COUNT

    def test_categorization_immutable(self):
        """Categorization deve ser imutável"""
        cat = Categorization(
            transaction_id="txn_123",
            user_id="usr_456",
            original_category="UNCATEGORIZED",
            new_category="ALIMENTACAO",
            confidence=0.95,
        )

        with pytest.raises(Exception):
            cat.confidence = 0.5

    def test_categorization_invalid_confidence_raises_error(self):
        """Deve lançar ValueError se confidence inválido"""
        with pytest.raises(ValueError, match="confidence deve estar entre 0 e 1"):
            Categorization(
                transaction_id="txn_123",
                user_id="usr_456",
                original_category="UNCATEGORIZED",
                new_category="ALIMENTACAO",
                confidence=1.5,
            )

    def test_categorization_to_dict(self):
        """Deve converter para dict"""
        cat = Categorization(
            transaction_id="txn_123",
            user_id="usr_456",
            original_category="UNCATEGORIZED",
            new_category="ALIMENTACAO",
            confidence=0.85,
            rules_applied=("merchant_match",),
        )

        result = cat.to_dict()

        assert result["new_category"] == "ALIMENTACAO"
        assert result["confidence"] == pytest.approx(0.85)
        assert "merchant_match" in result["rules_applied"]

    def test_categorization_to_dynamodb_item(self):
        """Deve converter para item DynamoDB com TTL"""
        cat = Categorization(
            transaction_id="txn_123",
            user_id="usr_456",
            original_category="UNCATEGORIZED",
            new_category="ALIMENTACAO",
            confidence=0.90,
        )

        item = cat.to_dynamodb_item()

        assert item["transaction_id"]["S"] == "txn_123"
        assert item["new_category"]["S"] == "ALIMENTACAO"
        assert "ttl" in item


# ============ Test Categorization ============


class TestCategorization:
    """Testes para função de categorização"""

    @patch("requests.post")
    def test_categorize_success(self, mock_post, valid_transaction):
        """Deve categorizar com sucesso"""
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(
                return_value={
                    "categorization": {
                        "category": "ALIMENTACAO",
                        "confidence": 0.95,
                        "rules_applied": ["merchant_match"],
                    }
                }
            ),
            raise_for_status=Mock(),
        )

        result = categorize_transaction(valid_transaction, {})

        assert result.new_category == "ALIMENTACAO"
        assert result.confidence == pytest.approx(0.95)

    @patch("requests.post")
    def test_categorize_timeout(self, mock_post, valid_transaction):
        """Deve lançar RuntimeError em timeout"""
        mock_post.side_effect = Timeout("Request timeout")

        with pytest.raises(RuntimeError, match="Categorizer timeout"):
            categorize_transaction(valid_transaction, {})

    @patch("requests.post")
    def test_categorize_connection_error(self, mock_post, valid_transaction):
        """Deve lançar RuntimeError em erro de conexão após retries"""
        mock_post.side_effect = ConnectionError("Connection refused")

        with pytest.raises(RuntimeError, match="Categorizer service error"):
            categorize_transaction(valid_transaction, {})


# ============ Test Response Parsing ============


class TestResponseParsing:
    """Testes para parsing de respostas"""

    def test_parse_categorizer_response_valid(self, valid_transaction):
        """Deve parsear resposta válida"""
        response = {
            "categorization": {
                "category": "ALIMENTACAO",
                "confidence": 0.88,
                "rules_applied": ["rule1"],
            }
        }

        result = parse_categorizer_response(valid_transaction, response)

        assert result.new_category == "ALIMENTACAO"
        assert result.confidence == pytest.approx(0.88)

    def test_parse_categorizer_response_missing_fields(self, valid_transaction):
        """Deve usar defaults para campos faltantes"""
        response = {
            "categorization": {
                "category": "OUTROS",
            }
        }

        result = parse_categorizer_response(valid_transaction, response)

        assert result.new_category == "OUTROS"
        assert result.confidence == pytest.approx(0.0)

    def test_parse_categorizer_response_invalid(self, valid_transaction):
        """Deve lançar ValueError para resposta inválida"""
        response = {"error": "Invalid request"}

        with pytest.raises(ValueError):
            parse_categorizer_response(valid_transaction, response)


# ============ Test Persistence ============


class TestPersistence:
    """Testes para persistência em DynamoDB"""

    @patch("src.main.get_dynamodb_client")
    def test_persist_categorization_success(self, mock_get_client):
        """Deve persistir categorização com sucesso"""
        mock_client = Mock()
        mock_client.put_item = Mock()
        mock_get_client.return_value = mock_client

        cat = Categorization(
            transaction_id="txn_123",
            user_id="usr_456",
            original_category="UNCATEGORIZED",
            new_category="ALIMENTACAO",
            confidence=0.95,
        )

        result = persist_categorization(cat)

        assert result is True
        mock_client.put_item.assert_called_once()

    @patch("src.main.get_dynamodb_client")
    def test_persist_categorization_throttling(self, mock_get_client):
        """Deve fazer retry em throttling"""
        mock_client = Mock()
        from botocore.exceptions import ClientError

        # Primeira tentativa: throttling, depois sucesso
        mock_client.put_item = Mock(
            side_effect=[
                ClientError(
                    {"Error": {"Code": "ProvisionedThroughputExceededException"}}, "PutItem"
                ),
                None,  # Success
            ]
        )
        mock_get_client.return_value = mock_client

        cat = Categorization(
            transaction_id="txn_123",
            user_id="usr_456",
            original_category="UNCATEGORIZED",
            new_category="ALIMENTACAO",
            confidence=0.95,
        )

        result = persist_categorization(cat)

        assert result is True
        assert mock_client.put_item.call_count == EXPECTED_RETRY_ATTEMPT_COUNT


# ============ Test Lambda Handler ============


class TestLambdaHandler:
    """Testes para lambda handler"""

    @patch("src.main.persist_categorization")
    @patch("requests.post")
    def test_handler_success(
        self, mock_post, mock_persist, valid_dynamodb_stream_event, mock_context
    ):
        """Handler deve retornar sucesso"""
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(
                return_value={
                    "categorization": {
                        "category": "ALIMENTACAO",
                        "confidence": 0.95,
                        "rules_applied": [],
                    }
                }
            ),
            raise_for_status=Mock(),
        )
        mock_persist.return_value = True

        response = lambda_handler(valid_dynamodb_stream_event, mock_context)

        assert response["status"] == "SUCCESS"
        assert response["processed_transactions"] == 1

    def test_handler_empty_records(self, empty_records_event, mock_context):
        """Handler deve retornar sucesso para records vazios"""
        response = lambda_handler(empty_records_event, mock_context)

        assert response["status"] == "SUCCESS"
        assert response["processed_transactions"] == 0

    def test_handler_error_handling(self, valid_dynamodb_stream_event, mock_context):
        """Handler deve capturar exceções"""
        # Event com dados inválidos
        event = {"Records": [{"eventName": "INVALID", "dynamodb": {"NewImage": {}}}]}

        response = lambda_handler(event, mock_context)

        # Deve retornar sucesso mas com 0 processados (error foi capturado)
        assert response["status"] == "SUCCESS"
        assert response["processed_transactions"] == 0
