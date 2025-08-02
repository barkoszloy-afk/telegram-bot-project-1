#!/usr/bin/env python3
"""
Проверка статуса бота и команд через Telegram API
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot
from config import BOT_TOKEN

async def check_bot_status():
    """Проверяет статус бота через Telegram API"""
    print("🤖 Проверяем статус бота...")
    
    if not BOT_TOKEN:
        print("❌ Токен бота не найден в config.py")
        return False
    
    try:
        from telegram.ext import Application
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        await application.initialize()
        
        bot = application.bot
        
        # Получаем информацию о боте
        me = await bot.get_me()
        print(f"✅ Бот активен: @{me.username}")
        print(f"📝 Имя: {me.first_name}")
        print(f"🆔 ID: {me.id}")
        
        # Получаем команды бота
        commands = await bot.get_my_commands()
        if commands:
            print(f"\n📋 Зарегистрированные команды:")
            for cmd in commands:
                print(f"   /{cmd.command} - {cmd.description}")
        else:
            print("\n⚠️ Команды не зарегистрированы в боте")
            
        # Проверяем webhook
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            print(f"\n🌐 Webhook активен: {webhook_info.url}")
            print(f"📊 Pending updates: {webhook_info.pending_update_count}")
        else:
            print(f"\n📱 Polling режим (webhook не установлен)")
            
        await application.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки бота: {e}")
        return False

async def main():
    """Главная функция"""
    print("🚀 Диагностика бота\n")
    
    success = await check_bot_status()
    
    if success:
        print(f"\n💡 Рекомендации:")
        print(f"1. Если бот работает на Railway - команды должны работать там")
        print(f"2. Попробуйте написать /help прямо в Telegram боте")
        print(f"3. Если не работает - проверьте логи на Railway")
        print(f"4. Возможно, нужно зарегистрировать команды командой /setcommands в @BotFather")
    else:
        print(f"\n❌ Бот недоступен. Проверьте:")
        print(f"1. Правильность токена в config.py")
        print(f"2. Работает ли бот на Railway")
        print(f"3. Нет ли проблем с сетью")

if __name__ == "__main__":
    asyncio.run(main())
