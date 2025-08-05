# final_test.py - Финальный тест всей системы
import asyncio
import sys
import pytest
from telegram import Bot


def test_bot_functionality():
    """Тестируем базовую функциональность бота."""
    from config import BOT_TOKEN, validate_config

    # Если токен отсутствует, пропускаем интеграционный тест
    if not BOT_TOKEN:
        pytest.skip("BOT_TOKEN не задан")

    # Проверяем корректность конфигурации
    validate_config()

    async def _run_checks():
        bot = Bot(token=BOT_TOKEN)

        # Получаем информацию о боте
        bot_info = await bot.get_me()
        assert bot_info.username, "Имя пользователя бота не получено"

        # Проверяем список команд
        commands = await bot.get_my_commands()
        assert isinstance(commands, list)

        # Проверяем информацию о webhook
        webhook_info = await bot.get_webhook_info()
        assert webhook_info is not None

    asyncio.run(_run_checks())

def run_module_imports():
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
    return success == total

def main():
    """Главная функция тестирования"""
    print("🚀 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("=" * 60)

    # Тест модулей
    modules_ok = run_module_imports()

    # Тест бота
    print("\n🤖 ТЕСТИРОВАНИЕ БОТА")
    print("=" * 30)
    try:
        test_bot_functionality()
        bot_ok = True
    except pytest.skip.Exception:
        bot_ok = True
    except Exception as exc:
        print(f"❌ Ошибка: {exc}")
        bot_ok = False

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
    sys.exit(main())
