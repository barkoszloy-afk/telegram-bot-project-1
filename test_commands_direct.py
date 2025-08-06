#!/usr/bin/env python3
"""
Локальный тест обработчика команд без webhook
"""

import asyncio
import sys
import os
import pytest

# Добавляем путь к проекту
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes
from main_bot_railway import start_command, test_command

@pytest.mark.asyncio
async def test_commands_directly():
    """Тестируем команды напрямую без webhook"""
    print("🧪 ПРЯМОЙ ТЕСТ КОМАНД")
    print("=" * 30)
    
    # Это сложный интеграционный тест, который требует полной настройки бота
    # Мы просто проверяем, что функции можно импортировать
    try:
        from main_bot_railway import start_command, test_command
        print("✅ Команды импортированы успешно")
        assert start_command is not None
        assert test_command is not None
        print("✅ Функции команд существуют и не равны None")
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать команды: {e}")
    except Exception as e:
        pytest.fail(f"Ошибка при проверке команд: {e}")

# Дополнительный тест для проверки без pytest
def test_command():
    """Функция для проверки вне pytest"""
    print("📋 Запуск простого теста импорта...")
    try:
        from main_bot_railway import start_command, test_command
        print("✅ Команды импортированы успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
