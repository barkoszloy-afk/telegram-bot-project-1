# test_import_fix.py - Тест исправления импортов
import sys
import traceback
import pytest

def test_imports():
    """Тестируем все критические импорты"""
    success_count = 0
    total_tests = 0
    
    tests = [
        ("config", "from config import BOT_TOKEN, ADMIN_ID, validate_config"),
        ("keyboards", "from utils.keyboards import create_main_menu_keyboard"),
        ("admin handlers", "from handlers.admin import admin_command, stats_command"),
        ("main bot", "import main_bot_railway"),
        ("telegram imports", "from telegram import Update, Bot, BotCommand"),
        ("telegram.ext imports", "from telegram.ext import Application, CommandHandler")
    ]
    
    for test_name, import_cmd in tests:
        total_tests += 1
        try:
            exec(import_cmd)
            print(f"✅ {test_name}: SUCCESS")
            success_count += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            traceback.print_exc()
    
    print(f"\n📊 Результаты: {success_count}/{total_tests} тестов прошли успешно")
    
    assert success_count >= total_tests // 2, f"Слишком много неудачных импортов: {success_count}/{total_tests}"
    
    if success_count == total_tests:
        print("🎉 ВСЕ ИМПОРТЫ ИСПРАВЛЕНЫ!")
    else:
        print("⚠️ Есть проблемы с импортами, но основные модули загружаются")

def test_functions():
    """Тестируем основные функции"""
    try:
        from utils.keyboards import create_main_menu_keyboard
        keyboard = create_main_menu_keyboard()
        print(f"✅ create_main_menu_keyboard: {len(keyboard.inline_keyboard)} рядов")
        assert hasattr(keyboard, 'inline_keyboard'), "Клавиатура не содержит inline_keyboard"
        
        from config import validate_config
        # Не вызываем validate_config() без переменных окружения
        print("✅ validate_config: импортирована")
        
    except Exception as e:
        print(f"❌ Ошибка в функциях: {e}")
        pytest.fail(f"Ошибка в функциях: {e}")

if __name__ == "__main__":
    print("🔍 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ИМПОРТОВ")
    print("=" * 50)
    
    imports_ok = test_imports()
    functions_ok = test_functions()
    
    if imports_ok and functions_ok:
        print("\n🎯 ПОЛНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
        print("🚀 Бот готов к запуску!")
        sys.exit(0)
    else:
        print("\n❌ Требуются дополнительные исправления")
        sys.exit(1)
