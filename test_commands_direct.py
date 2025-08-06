#!/usr/bin/env python3
"""
Локальный тест обработчика команд без webhook
"""

import asyncio
import sys
import os
import pytest

# Добавляем путь к проекту
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes
from main_bot_railway import start_command, test_command

@pytest.mark.asyncio
async def test_commands_directly():
    """Тестируем команды напрямую без webhook"""
    print("🧪 ПРЯМОЙ ТЕСТ КОМАНД")
    print("=" * 30)
    
    # Создаем мок объекты
    user = User(
        id=345470935,
        is_bot=False,
        first_name="TestUser",
        username="testuser"
    )
    
    chat = Chat(
        id=345470935,
        type="private",
        first_name="TestUser",
        username="testuser"
    )
    
    message = Message(
        message_id=9999,
        date=None,
        chat=chat,
        from_user=user,
        text="/start"
    )
    
    update = Update(
        update_id=999999,
        message=message
    )
    
    # Создаем пустой context
    context = ContextTypes.DEFAULT_TYPE()
    
    print("📋 Тестируем start_command...")
    try:
        await start_command(update, context)
        print("✅ start_command выполнена без ошибок")
    except Exception as e:
        print(f"❌ start_command ошибка: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        pytest.fail(f"start_command failed: {e}")
    
    print("\n📋 Тестируем test_command...")
    message.text = "/test"
    try:
        await test_command(update, context)
        print("✅ test_command выполнена без ошибок")
    except Exception as e:
        print(f"❌ test_command ошибка: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        pytest.fail(f"test_command failed: {e}")

# Дополнительный тест для проверки без pytest
def test_command():
    """Функция для проверки вне pytest"""
    print("📋 Запуск локального теста...")
    asyncio.run(test_commands_directly())
