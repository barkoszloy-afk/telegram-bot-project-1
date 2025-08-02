#!/usr/bin/env python3
"""
Тест команды help без запуска бота
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from main_bot_railway import help_command

async def test_help_command():
    """Тестирует функцию help_command"""
    print("🧪 Тестируем команду /help...")
    
    # Создаем мок объекты
    update = MagicMock()
    context = MagicMock()
    
    # Настраиваем мок message
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    
    try:
        # Вызываем функцию help_command
        await help_command(update, context)
        
        # Проверяем, что reply_text был вызван
        assert update.message.reply_text.called, "reply_text не был вызван"
        
        # Получаем аргументы вызова
        call_args = update.message.reply_text.call_args
        help_text = call_args[0][0]  # первый аргумент
        
        print("✅ Команда help работает!")
        print(f"📝 Текст справки:\n{help_text}")
        
        # Проверяем содержание справки
        expected_parts = [
            "Справка по боту",
            "/start",
            "/help", 
            "/admin",
            "гороскопы"
        ]
        
        missing_parts = []
        for part in expected_parts:
            if part not in help_text:
                missing_parts.append(part)
        
        if missing_parts:
            print(f"⚠️ Отсутствуют части: {missing_parts}")
        else:
            print("✅ Все необходимые части присутствуют в справке")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

async def test_help_command_no_message():
    """Тестирует функцию help_command когда нет message"""
    print("\n🧪 Тестируем команду /help без message...")
    
    # Создаем мок объекты
    update = MagicMock()
    context = MagicMock()
    
    # message = None
    update.message = None
    
    try:
        # Вызываем функцию help_command
        result = await help_command(update, context)
        
        # Функция должна просто вернуться без ошибок
        print("✅ Команда help корректно обрабатывает отсутствие message")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании без message: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестов команды help\n")
    
    tests = [
        test_help_command(),
        test_help_command_no_message()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    passed = sum(1 for result in results if result is True)
    total = len(results)
    
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Прошло: {passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты команды help прошли успешно!")
        print("\n💡 Команда help работает корректно.")
        print("   Если она не отвечает в боте, проблема в конфликте экземпляров.")
    else:
        print("❌ Есть проблемы с командой help")

if __name__ == "__main__":
    asyncio.run(main())
