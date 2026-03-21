"""
Configuração global para pytest
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


# ============ Fixtures Globais ============

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup environment variables para testes"""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["CATEGORIZATIONS_TABLE"] = "test-categorizations"
    os.environ["CATEGORIZER_ENDPOINT"] = "https://test.categorizer.local/api/v1/categorize"
    os.environ["CATEGORIZER_TOKEN"] = "test-token"


# ============ Pytest Plugins ============

def pytest_configure(config):
    """Configure pytest plugins"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
