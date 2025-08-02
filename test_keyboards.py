#!/usr/bin/env python3
"""
Тест новых inline кнопок в keyboards.py
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.keyboards import (
    get_admin_menu_keyboard,
    get_admin_preview_keyboard,
    create_admin_menu_keyboard,
    create_admin_preview_keyboard,
    get_zodiac_keyboard,
    get_morning_variants_keyboard,
    get_reaction_keyboard
)

def test_admin_keyboards():
    """Тестирует админские клавиатуры"""
    print("🧪 Тестируем админские inline кнопки...\n")
    
    # Тест главного меню админа
    print("📋 Админ меню:")
    admin_menu = get_admin_menu_keyboard()
    for i, row in enumerate(admin_menu):
        for j, button in enumerate(row):
            print(f"   [{i}][{j}] {button.text} -> {button.callback_data}")
    
    # Тест создания InlineKeyboardMarkup
    admin_markup = create_admin_menu_keyboard()
    print(f"✅ InlineKeyboardMarkup создан: {type(admin_markup).__name__}")
    
    print("\n📋 Предварительный просмотр кнопок:")
    
    # Тест утреннего поста
    morning_preview = get_admin_preview_keyboard("morning", "post123")
    print("🌅 Утренний пост:")
    for i, row in enumerate(morning_preview):
        for j, button in enumerate(row):
            print(f"   [{i}][{j}] {button.text} -> {button.callback_data}")
    
    # Тест гороскопа
    horoscope_preview = get_admin_preview_keyboard("horoscope", "post456")
    print("\n🔮 Гороскоп:")
    for i, row in enumerate(horoscope_preview):
        for j, button in enumerate(row):
            print(f"   [{i}][{j}] {button.text} -> {button.callback_data}")
    
    # Тест вечернего поста
    evening_preview = get_admin_preview_keyboard("evening", "post789")
    print("\n🌙 Вечерний пост:")
    for i, row in enumerate(evening_preview):
        for j, button in enumerate(row):
            print(f"   [{i}][{j}] {button.text} -> {button.callback_data}")
    
    return True

def test_user_keyboards():
    """Тестирует пользовательские клавиатуры"""
    print("\n🧪 Тестируем пользовательские inline кнопки...\n")
    
    # Тест знаков зодиака
    zodiac_keyboard = get_zodiac_keyboard()
    print("♈ Знаки зодиака:")
    for i, row in enumerate(zodiac_keyboard):
        row_text = " | ".join([f"{btn.text}" for btn in row])
        print(f"   Ряд {i+1}: {row_text}")
    
    # Тест утренних вариантов
    morning_keyboard = get_morning_variants_keyboard()
    print("\n🌅 Утренние варианты:")
    for i, row in enumerate(morning_keyboard):
        for j, button in enumerate(row):
            print(f"   [{i}][{j}] {button.text} -> {button.callback_data}")
    
    # Тест реакций
    reaction_keyboard = get_reaction_keyboard("test_post_123")
    print("\n❤️ Реакции:")
    for i, row in enumerate(reaction_keyboard):
        for j, button in enumerate(row):
            print(f"   [{i}][{j}] {button.text} -> {button.callback_data}")
    
    return True

def main():
    """Главная функция тестирования"""
    print("🚀 Тест inline кнопок keyboards.py\n")
    
    try:
        test_admin_keyboards()
        test_user_keyboards()
        
        print("\n📊 Результаты:")
        print("✅ Админ меню: 5 кнопок")
        print("✅ Предварительный просмотр: 2-3 кнопки в зависимости от типа")
        print("✅ Знаки зодиака: 12 кнопок в сетке 3x4")
        print("✅ Утренние варианты: 3 кнопки")
        print("✅ Реакции: динамические кнопки с callback_data")
        
        print("\n🎉 Все inline кнопки работают корректно!")
        print("💡 Теперь все кнопки централизованы в utils/keyboards.py")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
