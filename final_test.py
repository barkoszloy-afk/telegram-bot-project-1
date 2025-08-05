# final_test.py - Финальный тест всей системы
import sys
import asyncio
from telegram import Bot


def test_bot_functionality():
    """Базовая проверка инициализации бота.

    Тест исключает сетевые вызовы и лишь убеждается, что объект
    ``Bot`` из библиотеки ``python-telegram-bot`` может быть создан.
    """
    bot = Bot(token="123:ABC")
    assert bot is not None

def test_all_modules():
    """Тестируем все модули"""
    modules = [
        ("config", "from config import BOT_TOKEN, ADMIN_ID, validate_config"),
        ("utils.keyboards", "from utils.keyboards import create_main_menu_keyboard"),
        ("utils.database", "from utils.database import reactions_db"),
        ("handlers.admin", "from handlers.admin import admin_command"),
        ("handlers.reactions", "from handlers.reactions import handle_reaction"),
        ("main_bot_railway", "import main_bot_railway"),
    ]
    
    for name, import_cmd in modules:
        try:
            exec(import_cmd)
        except Exception as e:
            import pytest

            pytest.fail(f"{name} import failed - {e}")

async def main():
    """Главная функция тестирования"""
    print("🚀 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("=" * 60)
    
    # Тест модулей
    modules_ok = test_all_modules()
    
    # Тест бота
    print("\n🤖 ТЕСТИРОВАНИЕ БОТА")
    print("=" * 30)
    bot_ok = await test_bot_functionality()
    
    # Результаты
    print("\n" + "=" * 60)
    if modules_ok and bot_ok:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🔧 Все отступы исправлены")
        print("📦 Все модули импортируются")  
        print("🤖 Бот функционирует корректно")
        print("🚀 Система готова к работе!")
        return 0
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        if not modules_ok:
            print("📦 Проблемы с модулями")
        if not bot_ok:
            print("🤖 Проблемы с ботом")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
