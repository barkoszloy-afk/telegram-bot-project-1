#!/usr/bin/env python3
"""
Тест команд бота через прямую отправку сообщений
"""

import asyncio
import time
from telegram import Bot
from config import BOT_TOKEN, ADMIN_ID

async def test_bot_commands():
    """Тестируем команды бота через прямую отправку"""
    bot = Bot(token=BOT_TOKEN)
    
    print("🧪 ТЕСТИРОВАНИЕ КОМАНД БОТА")
    print("=" * 50)
    
    # Получаем информацию о боте
    me = await bot.get_me()
    print(f"🤖 Бот: @{me.username} ({me.first_name})")
    print(f"🆔 ID: {me.id}")
    
    # Проверяем webhook
    webhook_info = await bot.get_webhook_info()
    print(f"🌐 Webhook: {webhook_info.url}")
    print(f"📨 Pending updates: {webhook_info.pending_update_count}")
    
    # Отправляем тестовые команды
    test_commands = [
        "/start",
        "/help", 
        "/test",
        "/ping",
        "/status"
    ]
    
    print(f"\n📋 Отправляем команды админу {ADMIN_ID}:")
    
    for cmd in test_commands:
        try:
            # Отправляем команду
            message = await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🧪 Тест команды: {cmd}"
            )
            print(f"✅ {cmd} - отправлено (ID: {message.message_id})")
            
            # Небольшая пауза между командами
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ {cmd} - ошибка: {e}")
    
    print(f"\n📢 Инструкция:")
    print(f"1. Откройте Telegram и найдите бота @{me.username}")
    print(f"2. Отправьте команду /start")
    print(f"3. Проверьте, отвечает ли бот")
    print(f"4. Если бот не отвечает, проверьте логи Railway")

if __name__ == "__main__":
    asyncio.run(test_bot_commands())
