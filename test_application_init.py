#!/usr/bin/env python3
"""
Тест запуска main_bot_railway.py с детальным логированием
"""

import sys
import os
import logging
import pytest

# Добавляем путь к проекту
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_application_creation():
    """Тестируем создание Application"""
    try:
        print("🧪 ТЕСТ СОЗДАНИЯ APPLICATION")
        print("=" * 40)
        
        from config import BOT_TOKEN, CONNECT_TIMEOUT, READ_TIMEOUT, WRITE_TIMEOUT, POOL_TIMEOUT
        from telegram.ext import Application
        
        print(f"🔑 BOT_TOKEN: {BOT_TOKEN[:10] if BOT_TOKEN else None}...")
        print(f"⏱️ Timeouts: {CONNECT_TIMEOUT}, {READ_TIMEOUT}, {WRITE_TIMEOUT}, {POOL_TIMEOUT}")
        
        # Проверяем наличие токена
        if not BOT_TOKEN:
            print("⚠️ BOT_TOKEN не установлен - тест пропущен")
            pytest.skip("BOT_TOKEN не установлен в переменных окружения")
        
        # Создаем Application как в main_bot_railway.py
        print("📱 Создаем Application...")
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .connect_timeout(CONNECT_TIMEOUT)
            .read_timeout(READ_TIMEOUT) 
            .write_timeout(WRITE_TIMEOUT)
            .pool_timeout(POOL_TIMEOUT)
            .build()
        )
        
        print(f"✅ Application создан: {type(application)}")
        print(f"🤖 Bot: {application.bot}")
        print(f"📋 Handlers: {len(application.handlers)}")
        
        assert application is not None, "Application не создан"
        assert application.bot is not None, "Bot не создан"
        
        # Тестируем создание Update
        from telegram import Update
        
        test_update_data = {
            "update_id": 999999,
            "message": {
                "message_id": 9999,
                "from": {
                    "id": 345470935,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 345470935,
                    "first_name": "Test", 
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1735776000,
                "text": "/start"
            }
        }
        
        print("📨 Создаем Update объект...")
        update = Update.de_json(test_update_data, application.bot)
        print(f"✅ Update создан: {update.update_id}")
        
        assert update is not None, "Update не создан"
        assert update.update_id == 999999, "Update ID не соответствует"
        
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        
        # Особая обработка для отсутствующего токена
        if "You must pass the token" in str(e):
            pytest.skip(f"BOT_TOKEN не корректен или отсутствует: {e}")
        else:
            pytest.fail(f"Ошибка создания Application: {e}")

if __name__ == "__main__":
    test_application_creation()
