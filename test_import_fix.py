# test_import_fix.py - Тест исправления импортов
import sys


def test_imports():
    """Тестируем все критические импорты"""
    tests = [
        ("config", "from config import BOT_TOKEN, ADMIN_ID, validate_config"),
        ("keyboards", "from utils.keyboards import create_main_menu_keyboard"),
        ("admin handlers", "from handlers.admin import admin_command, stats_command"),
        ("main bot", "import main_bot_railway"),
        ("telegram imports", "from telegram import Update, Bot, BotCommand"),
        ("telegram.ext imports", "from telegram.ext import Application, CommandHandler"),
    ]

    for test_name, import_cmd in tests:
        try:
            exec(import_cmd)
        except Exception as e:
            import pytest

            pytest.fail(f"{test_name}: {e}")


def test_functions():
    """Тестируем основные функции"""
    from utils.keyboards import create_main_menu_keyboard

    keyboard = create_main_menu_keyboard()
    assert keyboard is not None

    from config import validate_config

    assert callable(validate_config)

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
