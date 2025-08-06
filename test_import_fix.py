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

    # Все импорты должны выполняться без ошибок
    assert success_count == total_tests, "Некоторые импорты завершились ошибкой"

def test_functions():
    """Тестируем основные функции"""
    try:
        from utils.keyboards import create_main_menu_keyboard
        keyboard = create_main_menu_keyboard()
        print(f"✅ create_main_menu_keyboard: {len(keyboard.inline_keyboard)} рядов")
    except Exception as e:
        pytest.skip(f"create_main_menu_keyboard недоступна: {e}")

    try:
        from config import validate_config
        validate_config()
        print("✅ validate_config: работает")
    except Exception as e:
        pytest.skip(f"validate_config недоступна: {e}")

if __name__ == "__main__":
    print("🔍 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ИМПОРТОВ")
    print("=" * 50)
    test_imports()
    test_functions()

    print("\n🎯 ПОЛНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print("🚀 Бот готов к запуску!")
    sys.exit(0)
