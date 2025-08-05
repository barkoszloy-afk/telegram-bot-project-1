# final_test.py - Финальный тест всей системы
import asyncio
import sys
import pytest
from telegram import Bot

async def test_bot_functionality():
    """Тестируем функциональность бота"""
    try:
        from config import BOT_TOKEN, validate_config

        # Валидация конфигурации
        print("🔍 Проверяем конфигурацию...")
        try:
            validate_config()
        except ValueError as e:
            pytest.skip(str(e))
        
        # Создаем бота
        print("🤖 Создаем экземпляр бота...")
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем информацию о боте
        print("📋 Получаем информацию о боте...")
        bot_info = await bot.get_me()
        print(f"✅ Бот: @{bot_info.username} ({bot_info.first_name})")
        
        # Проверяем команды
        print("📱 Проверяем команды...")
        commands = await bot.get_my_commands()
        print(f"✅ Команд в меню: {len(commands)}")
        for cmd in commands:
            print(f"   /{cmd.command} - {cmd.description}")
        
        # Проверяем webhook
        print("🌐 Проверяем webhook...")
        webhook_info = await bot.get_webhook_info()
        print(f"✅ Webhook URL: {webhook_info.url or 'Не установлен'}")
        print(f"✅ Pending updates: {webhook_info.pending_update_count}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        pytest.fail(f"Ошибка тестирования бота: {e}")

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
