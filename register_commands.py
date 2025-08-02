#!/usr/bin/env python3
"""
Регистрация команд бота в Telegram
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import BotCommand
from telegram.ext import Application
from config import BOT_TOKEN

async def register_commands():
    """Регистрирует команды бота в Telegram"""
    print("🚀 Регистрируем команды бота...")
    
    if not BOT_TOKEN:
        print("❌ Токен бота не найден в config.py")
        return False
    
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        await application.initialize()
        
        bot = application.bot
        
        # Определяем команды
        commands = [
            BotCommand("start", "🚀 Начать работу с ботом"),
            BotCommand("help", "📚 Показать справку по командам"),
            BotCommand("admin", "⚙️ Админ-панель (только для администратора)")
        ]
        
        # Регистрируем команды
        await bot.set_my_commands(commands)
        
        print("✅ Команды успешно зарегистрированы!")
        
        # Проверяем регистрацию
        registered_commands = await bot.get_my_commands()
        print(f"\n📋 Зарегистрированные команды:")
        for cmd in registered_commands:
            print(f"   /{cmd.command} - {cmd.description}")
        
        await application.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка регистрации команд: {e}")
        return False

async def main():
    """Главная функция"""
    print("🔧 Регистрация команд Telegram бота\n")
    
    success = await register_commands()
    
    if success:
        print(f"\n🎉 Готово!")
        print(f"📱 Теперь команды должны работать в Telegram:")
        print(f"   • /start - запуск бота")
        print(f"   • /help - справка")
        print(f"   • /admin - админ-панель")
        print(f"\n💡 Попробуйте написать /help в боте - должно работать!")
    else:
        print(f"\n❌ Не удалось зарегистрировать команды")
        print(f"   Проверьте токен и подключение к интернету")

if __name__ == "__main__":
    asyncio.run(main())
