#!/usr/bin/env python3
"""
Тест команды /start
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from config import BOT_TOKEN
from utils.keyboards import create_main_menu_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда /start"""
    user = update.effective_user
    print(f"📨 Получена команда /start от пользователя: {user.first_name if user else 'Неизвестный'}")
    
    if not update.message:
        print("❌ update.message отсутствует")
        return
        
    user_name = user.first_name if user else "друг"
    welcome_text = f"""
🌟 Привет, {user_name}!

Добро пожаловать в мир саморазвития и вдохновения! ✨

🎯 **Выберите интересующую вас тему:**

💫 **Мотивация** - вдохновляющие идеи на каждый день
🔮 **Эзотерика** - гороскопы, астрология и духовность  
🎯 **Развитие** - личностный рост и обучение
🌟 **Здоровье** - забота о теле и разуме
💝 **Отношения** - гармония в общении и любви

👇 Нажмите на кнопку ниже, чтобы начать:
"""
    
    try:
        keyboard = create_main_menu_keyboard()
        print(f"✅ Клавиатура создана: {len(keyboard.inline_keyboard)} рядов")
        
        # Отправляем приветствие с главным меню
        await update.message.reply_text(
            welcome_text, 
            reply_markup=keyboard
        )
        print("✅ Сообщение отправлено!")
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

def main():
    """Основная функция для тестирования"""
    print("🚀 Запуск тестового бота...")
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден!")
        return
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчика
    application.add_handler(CommandHandler("start", start_command))
    
    print("✅ Обработчик зарегистрирован")
    print("📱 Отправьте команду /start боту в Telegram")
    print("🛑 Нажмите Ctrl+C для остановки")
    
    # Запуск polling
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
