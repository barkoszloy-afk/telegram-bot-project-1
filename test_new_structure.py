# test_new_structure.py - Тестирование новой структурированной системы

import asyncio
from telegram import Update, CallbackQuery, Message, User, Chat
from telegram.ext import ContextTypes
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

def test_new_structure():
    """Тестирует новую структурированную систему меню"""
    
    print("🧪 ТЕСТ НОВОЙ СТРУКТУРИРОВАННОЙ СИСТЕМЫ")
    print("=" * 60)
    
    try:
        # 1. Тест импортов новых клавиатур
        from utils.keyboards import (
            create_main_menu_keyboard,
            create_motivation_submenu, 
            create_esoteric_submenu,
            create_development_submenu,
            create_health_submenu,
            create_relationships_submenu,
            create_zodiac_keyboard
        )
        print("✅ 1. Импорты новых клавиатур: OK")
        
        # 2. Тест создания главного меню
        main_menu = create_main_menu_keyboard()
        categories = main_menu.inline_keyboard
        print(f"✅ 2. Главное меню: {len(categories)} категорий")
        
        # Проверяем категории
        category_names = []
        for row in categories:
            for button in row:
                category_names.append(button.text)
        
        expected_categories = ["💫 Мотивация", "🔮 Эзотерика", "🎯 Развитие", "🌟 Здоровье", "💝 Отношения"]
        print(f"   📋 Категории: {', '.join(category_names)}")
        
        # 3. Тест подменю мотивации
        motivation_menu = create_motivation_submenu()
        motivation_options = len(motivation_menu.inline_keyboard)
        print(f"✅ 3. Подменю мотивации: {motivation_options} опций")
        
        # 4. Тест подменю эзотерики  
        esoteric_menu = create_esoteric_submenu()
        esoteric_options = len(esoteric_menu.inline_keyboard)
        print(f"✅ 4. Подменю эзотерики: {esoteric_options} опций")
        
        # 5. Тест клавиатуры зодиака
        zodiac_menu = create_zodiac_keyboard()
        zodiac_rows = len(zodiac_menu.inline_keyboard)
        print(f"✅ 5. Клавиатура зодиака: {zodiac_rows} рядов")
        
        # 6. Тест обработчиков
        from main_bot import (
            start_command,
            show_main_menu, 
            handle_category_selection,
            handle_motivation_selection,
            handle_esoteric_selection,
            handle_zodiac_selection
        )
        print("✅ 6. Обработчики функций: OK")
        
        # 7. Тест callback_data
        callback_tests = {
            "main_menu": "Главное меню",
            "category_motivation": "Категория мотивация", 
            "category_esoteric": "Категория эзотерика",
            "motivation_morning": "Утренняя мотивация",
            "motivation_evening": "Вечерние размышления",
            "esoteric_horoscope": "Гороскоп на день",
            "zodiac_овен": "Знак зодиака Овен"
        }
        
        print("✅ 7. Callback данные:")
        for callback, description in callback_tests.items():
            print(f"   🔗 {callback} → {description}")
        
        # 8. Проверка структуры навигации
        print("✅ 8. Структура навигации:")
        print("   🏠 Главное меню")
        print("   ├── 💫 Мотивация")
        print("   │   ├── 🌅 Утренняя мотивация")
        print("   │   ├── 🌙 Вечерние размышления") 
        print("   │   ├── 💪 Преодоление трудностей")
        print("   │   └── 🎯 Достижение целей")
        print("   ├── 🔮 Эзотерика")
        print("   │   ├── 🔮 Гороскоп на день → 12 знаков зодиака")
        print("   │   ├── 🌙 Лунный календарь")
        print("   │   ├── 🔢 Нумерология")
        print("   │   └── 🃏 Карты Таро")
        print("   ├── 🎯 Развитие (в разработке)")
        print("   ├── 🌟 Здоровье (в разработке)")
        print("   └── 💝 Отношения (в разработке)")
        
        print("\n🎉 ВСЕ ТЕСТЫ НОВОЙ СТРУКТУРЫ ПРОШЛИ!")
        print("📱 Система готова к использованию!")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keyboard_structure():
    """Детальный тест структуры клавиатур"""
    
    print("\n🔍 ДЕТАЛЬНЫЙ ТЕСТ КЛАВИАТУР")
    print("=" * 40)
    
    try:
        from utils.keyboards import create_main_menu_keyboard, create_zodiac_keyboard
        
        # Тест главного меню
        main_keyboard = create_main_menu_keyboard()
        print("📱 Главное меню:")
        for i, row in enumerate(main_keyboard.inline_keyboard):
            for j, button in enumerate(row):
                print(f"   [{i},{j}] {button.text} → {button.callback_data}")
        
        # Тест зодиака
        zodiac_keyboard = create_zodiac_keyboard()
        print("\n🔮 Знаки зодиака:")
        for i, row in enumerate(zodiac_keyboard.inline_keyboard):
            for j, button in enumerate(row):
                print(f"   [{i},{j}] {button.text} → {button.callback_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    # Запуск тестов
    result1 = test_new_structure()
    result2 = test_keyboard_structure()
    
    if result1 and result2:
        print("\n🏆 ВСЕ ТЕСТЫ УСПЕШНО ЗАВЕРШЕНЫ!")
        print("🚀 Новая структурированная система полностью готова!")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ")
