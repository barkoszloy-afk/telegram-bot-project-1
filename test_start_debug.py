#!/usr/bin/env python3
"""
Тест команды /start для диагностики проблем
"""

import sys
import os
import asyncio
import logging

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from main_bot_railway import start_command
    from utils.keyboards import create_main_menu_keyboard
    from telegram import Update, User, Message, Chat
    from telegram.ext import ContextTypes
    
    print("✅ Импорты успешны")
    
    # Тестируем создание клавиатуры
    try:
        keyboard = create_main_menu_keyboard()
        print(f"✅ Клавиатура создана: {len(keyboard.inline_keyboard)} рядов")
        for i, row in enumerate(keyboard.inline_keyboard):
            print(f"  Ряд {i+1}: {[btn.text for btn in row]}")
    except Exception as e:
        print(f"❌ Ошибка создания клавиатуры: {e}")
        sys.exit(1)
    
    # Создаем мок-объекты для тестирования
    class MockContext:
        pass
    
    class MockMessage:
        async def reply_text(self, text, reply_markup=None, parse_mode=None):
            print(f"📤 Отправлено сообщение:")
            print(f"   Текст: {text[:100]}...")
            if reply_markup:
                print(f"   Клавиатура: {len(reply_markup.inline_keyboard)} рядов")
            return True
    
    class MockUser:
        def __init__(self):
            self.id = 345470935
            self.first_name = "Test User"
    
    class MockUpdate:
        def __init__(self):
            self.message = MockMessage()
            self.effective_user = MockUser()
    
    async def test_start_command():
        """Тестируем команду /start"""
        print("\n🧪 Тестируем команду /start...")
        
        update = MockUpdate()
        context = MockContext()
        
        try:
            await start_command(update, context)
            print("✅ Команда /start выполнена успешно")
        except Exception as e:
            print(f"❌ Ошибка в команде /start: {e}")
            import traceback
            traceback.print_exc()
    
    # Запускаем тест
    asyncio.run(test_start_command())
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()
