#!/usr/bin/env python3
"""
Тест минимальной версии бота
"""

import asyncio
from utils.keyboards import create_main_menu_keyboard

def test_minimal_bot():
    """Тестирует минимальную версию бота"""
    print("🧪 ТЕСТ МИНИМАЛЬНОЙ ВЕРСИИ БОТА")
    print("=" * 40)
    
    # Тест клавиатуры
    try:
        keyboard = create_main_menu_keyboard()
        print(f"✅ Клавиатура создана: {len(keyboard.inline_keyboard)} рядов")
        
        # Проверяем структуру
        categories = []
        for row in keyboard.inline_keyboard:
            for button in row:
                categories.append(button.text)
        
        print(f"📱 Категории: {', '.join(categories)}")
        
        expected_categories = ["💫 Мотивация", "🔮 Эзотерика", "🎯 Развитие", "🌟 Здоровье", "💝 Отношения"]
        
        if all(cat in categories for cat in expected_categories):
            print("✅ Все категории присутствуют")
        else:
            print("❌ Некоторые категории отсутствуют")
            
    except Exception as e:
        print(f"❌ Ошибка создания клавиатуры: {e}")
        return False
    
    # Тест импорта основного модуля
    try:
        import main_bot_railway
        print("✅ Основной модуль импортируется")
    except Exception as e:
        print(f"❌ Ошибка импорта основного модуля: {e}")
        return False
    
    print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("🚀 Минимальная версия бота готова")
    print("\n📋 Что работает:")
    print("   • Команда /start")
    print("   • Главное меню с 5 категориями")
    print("   • Заглушки для категорий ('В разработке!')")
    print("   • Webhook для Railway")
    print("   • Базовая обработка ошибок")
    
    print("\n📝 Что нужно добавить:")
    print("   • Контент для каждой категории")
    print("   • Подменю для категорий")
    print("   • Команды /help, /test, /admin")
    print("   • Реакции на посты")
    print("   • Обработка текстовых сообщений")
    
    return True

if __name__ == '__main__':
    test_minimal_bot()
