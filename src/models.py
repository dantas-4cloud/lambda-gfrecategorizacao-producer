"""
Modelos consolidados para transações e categorização
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TypedDict


class TransactionType(str, Enum):
    """Tipos de transação suportadas"""

    CREDIT_CARD = "CREDIT_CARD"
    CHECKING_ACCOUNT = "CHECKING_ACCOUNT"
    PIX = "PIX"


class UserPreferencesDict(TypedDict, total=False):
    """Preferências do usuário"""

    default_category: str
    merchant_overrides: dict


@dataclass(frozen=True, slots=True)
class Transaction:
    """
    Modelo de transação financeira

    Imutável (frozen=True) e otimizado em memória (slots=True)
    """

    transaction_id: str
    user_id: str
    transaction_type: TransactionType
    amount: float
    merchant: str
    description: str
    timestamp: str

    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.transaction_id:
            raise ValueError("transaction_id é obrigatório")
        if not self.user_id:
            raise ValueError("user_id é obrigatório")
        if self.amount <= 0:
            raise ValueError("amount deve ser maior que zero")
        if not self.timestamp:
            raise ValueError("timestamp é obrigatório")

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "type": self.transaction_type.value,
            "amount": self.amount,
            "merchant": self.merchant,
            "description": self.description,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dynamodb(cls, item: dict) -> "Transaction":
        """Constrói a partir de item DynamoDB"""
        return cls(
            transaction_id=item.get("transaction_id", {}).get("S"),
            user_id=item.get("user_id", {}).get("S"),
            transaction_type=TransactionType(item.get("type", {}).get("S", "CREDIT_CARD")),
            amount=float(item.get("amount", {}).get("N", 0)),
            merchant=item.get("merchant", {}).get("S", ""),
            description=item.get("description", {}).get("S", ""),
            timestamp=item.get("timestamp", {}).get("S", datetime.now(timezone.utc).isoformat()),
        )


@dataclass(frozen=True, slots=True)
class Categorization:
    """
    Modelo de categorização de transação

    Imutável (frozen=True) e otimizado em memória (slots=True)
    """

    transaction_id: str
    user_id: str
    original_category: str
    new_category: str
    confidence: float
    rules_applied: tuple = field(default_factory=tuple)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    def __post_init__(self):
        """Validação pós-inicialização"""
        if not self.transaction_id:
            raise ValueError("transaction_id é obrigatório")
        if not self.user_id:
            raise ValueError("user_id é obrigatório")
        if not self.new_category:
            raise ValueError("new_category é obrigatório")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence deve estar entre 0 e 1")

    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "original_category": self.original_category,
            "new_category": self.new_category,
            "confidence": self.confidence,
            "rules_applied": list(self.rules_applied),
            "timestamp": self.timestamp,
        }

    def to_dynamodb_item(self) -> dict:
        """Converte para item DynamoDB"""
        return {
            "transaction_id": {"S": self.transaction_id},
            "user_id": {"S": self.user_id},
            "timestamp": {"N": str(int(datetime.now(timezone.utc).timestamp()))},
            "original_category": {"S": self.original_category},
            "new_category": {"S": self.new_category},
            "confidence": {"N": str(self.confidence)},
            "rules_applied": {"L": [{"S": rule} for rule in self.rules_applied]},
            "ttl": {"N": str(int(datetime.now(timezone.utc).timestamp()) + 7776000)},  # 90 dias
        }
