# tests/conftest.py - Конфигурация pytest

import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_bot():
    """Мок-объект для Telegram бота"""
    bot = Mock()
    bot.get_me = AsyncMock()
    bot.set_my_commands = AsyncMock()
    return bot

@pytest.fixture
def mock_update():
    """Мок-объект для Telegram Update"""
    update = Mock()
    update.effective_user.id = 12345
    update.effective_chat.id = 12345
    update.message.text = "/test"
    return update

@pytest.fixture
def mock_context():
    """Мок-объект для Context"""
    context = Mock()
    context.user_data = {}
    return context

# Маркеры для pytest
pytest_plugins = []

def pytest_configure(config):
    """Конфигурация маркеров pytest"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
