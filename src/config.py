"""
Configuração simplificada para logging estruturado
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

# Setup básico de logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")

logger = logging.getLogger("recategorization-producer")


def log_event(level: str, action: str, **metadata: Any) -> None:
    """
    Log estruturado para CloudWatch em formato JSON

    Args:
        level: Level de log (INFO, WARNING, ERROR, DEBUG)
        action: Descrição da ação
        **metadata: Dados adicionais estruturados
    """
    log_data = {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "action": action,
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "service": "recategorization-producer",
        **metadata,
    }

    # Emite como JSON para CloudWatch capturar
    log_line = json.dumps(log_data, default=str)

    if level == "DEBUG":
        logger.debug(log_line)
    elif level == "WARNING":
        logger.warning(log_line)
    elif level == "ERROR":
        logger.error(log_line)
    else:
        logger.info(log_line)


def log_info(action: str, **metadata: Any) -> None:
    """Log de informação"""
    log_event("INFO", action, **metadata)


def log_warning(action: str, **metadata: Any) -> None:
    """Log de aviso"""
    log_event("WARNING", action, **metadata)


def log_error(action: str, exception: Exception | None = None, **metadata: Any) -> None:
    """Log de erro"""
    if exception:
        metadata["exception"] = {
            "type": exception.__class__.__name__,
            "message": str(exception),
        }
    log_event("ERROR", action, **metadata)


def log_debug(action: str, **metadata: Any) -> None:
    """Log de debug"""
    log_event("DEBUG", action, **metadata)
