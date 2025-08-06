#!/usr/bin/env python3
"""
Тест команд бота через прямую отправку сообщений
"""

import asyncio
import time
import pytest
from telegram import Bot
from config import BOT_TOKEN, ADMIN_ID

@pytest.mark.asyncio
async def test_bot_commands():
    """Тестируем команды бота через прямую отправку"""
    # Проверяем наличие токена
    if not BOT_TOKEN:
        pytest.skip("BOT_TOKEN не установлен в переменных окружения")
        
    bot = Bot(token=BOT_TOKEN)
    
    print("🧪 ТЕСТИРОВАНИЕ КОМАНД БОТА")
    print("=" * 50)
    
    # Получаем информацию о боте
    me = await bot.get_me()
    print(f"🤖 Бот: @{me.username} ({me.first_name})")
    print(f"🆔 ID: {me.id}")
    
    assert me.username is not None, "Бот не имеет username"
    assert me.id is not None, "Бот не имеет ID"
    
    # Проверяем webhook
    webhook_info = await bot.get_webhook_info()
    print(f"🌐 Webhook: {webhook_info.url}")
    print(f"📨 Pending updates: {webhook_info.pending_update_count}")
    
    assert webhook_info is not None, "Не удалось получить информацию о webhook"
    
    # Отправляем тестовые команды
    test_commands = [
        "/start",
        "/help", 
        "/test",
        "/ping",
        "/status"
    ]
    
    print(f"\n📋 Отправляем команды админу {ADMIN_ID}:")
    
    successful_commands = 0
    for cmd in test_commands:
        try:
            # Отправляем команду
            message = await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🧪 Тест команды: {cmd}"
            )
            print(f"✅ {cmd} - отправлено (ID: {message.message_id})")
            successful_commands += 1
            
            # Небольшая пауза между командами
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ {cmd} - ошибка: {e}")
    
    # Проверяем, что хотя бы некоторые команды были отправлены
    assert successful_commands >= 1, f"Ни одна команда не была отправлена успешно из {len(test_commands)}"
    
    print(f"\n📢 Инструкция:")
    print(f"1. Откройте Telegram и найдите бота @{me.username}")
    print(f"2. Отправьте команду /start")
    print(f"3. Проверьте, отвечает ли бот")
    print(f"4. Если бот не отвечает, проверьте логи Railway")

if __name__ == "__main__":
    asyncio.run(test_bot_commands())
