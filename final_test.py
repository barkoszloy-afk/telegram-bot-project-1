# final_test.py - Финальный тест всей системы
import asyncio
import sys
import pytest
from telegram import Bot

@pytest.mark.asyncio
async def test_bot_functionality():
    """Тестируем функциональность бота"""
    try:
        from config import BOT_TOKEN, validate_config
    except Exception as e:
        pytest.skip(f"config недоступен: {e}")

    if not BOT_TOKEN:
        pytest.skip("BOT_TOKEN не настроен")

    # Валидация конфигурации
    validate_config()

    # Создаем бота и проверяем доступные данные
    bot = Bot(token=BOT_TOKEN)

    bot_info = await bot.get_me()
    assert bot_info is not None

    commands = await bot.get_my_commands()
    assert commands is not None

    webhook_info = await bot.get_webhook_info()
    assert webhook_info is not None

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

    success = 0
    total = len(modules)

    print("🔍 ТЕСТИРОВАНИЕ ВСЕХ МОДУЛЕЙ")
    print("=" * 50)

    for name, import_cmd in modules:
        try:
            exec(import_cmd)
            print(f"✅ {name}: OK")
            success += 1
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")

    print(f"\n📊 Модули: {success}/{total}")
    assert success == total, "Некоторые модули не импортируются"

async def main():
    """Главная функция тестирования"""
    print("🚀 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("=" * 60)
    test_all_modules()

    print("\n🤖 ТЕСТИРОВАНИЕ БОТА")
    print("=" * 30)
    await test_bot_functionality()

    print("\n" + "=" * 60)
    print("🎉 ТЕСТЫ ЗАВЕРШЕНЫ")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
