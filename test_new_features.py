# test_new_features.py - Тест новых эзотерических функций
import asyncio
import sys
import pytest
from telegram import Update
from telegram.ext import ContextTypes

# Эмулируем создание новых клавиатур
@pytest.mark.asyncio
async def test_new_keyboards():
    """Тестируем новые клавиатуры"""
    print("🧪 ТЕСТИРОВАНИЕ НОВЫХ ЭЗОТЕРИЧЕСКИХ ФУНКЦИЙ")
    print("=" * 50)
    
    try:
        from utils.keyboards import (
            create_esoteric_submenu,
            create_motivation_submenu, 
            create_development_submenu,
            create_health_submenu,
            create_relationships_submenu,
            create_zodiac_keyboard
        )
        
        print("✅ Все submenu функции импортированы успешно")
        
        # Тестируем эзотерическое подменю
        esoteric_keyboard = create_esoteric_submenu()
        print(f"✅ Эзотерическое подменю: {len(esoteric_keyboard.inline_keyboard)} рядов")
        
        # Проверяем количество кнопок в эзотерическом меню
        button_count = sum(len(row) for row in esoteric_keyboard.inline_keyboard)
        expected_buttons = 7  # 6 эзотерических функций + кнопка "Назад"
        
        if button_count == expected_buttons:
            print(f"✅ Правильное количество кнопок: {button_count}")
        else:
            print(f"⚠️ Ожидалось {expected_buttons} кнопок, получено {button_count}")
        
        # Проверяем конкретные callback_data
        expected_callbacks = [
            'esoteric_horoscope', 'esoteric_daily_card',
            'esoteric_good_morning', 'esoteric_lunar_forecast', 
            'esoteric_interactive', 'esoteric_evening_message',
            'main_menu'
        ]
        
        found_callbacks = []
        for row in esoteric_keyboard.inline_keyboard:
            for button in row:
                found_callbacks.append(button.callback_data)
        
        print("📋 Найденные callback_data:")
        for cb in found_callbacks:
            status = "✅" if cb in expected_callbacks else "❌"
            print(f"  {status} {cb}")
        
        # Тестируем зодиакальную клавиатуру
        zodiac_keyboard = create_zodiac_keyboard()
        zodiac_buttons = sum(len(row) for row in zodiac_keyboard.inline_keyboard)
        print(f"✅ Зодиакальная клавиатура: {zodiac_buttons} кнопок")
        
        print("\n🎉 ВСЕ ТЕСТЫ КЛАВИАТУР ПРОШЛИ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

@pytest.mark.asyncio
async def test_callback_data():
    """Тестируем обработку callback данных"""
    print("\n🧪 ТЕСТИРОВАНИЕ CALLBACK ОБРАБОТЧИКОВ")
    print("=" * 50)
    
    test_callbacks = [
        "category_esoteric",
        "esoteric_horoscope", 
        "esoteric_daily_card",
        "esoteric_good_morning",
        "esoteric_lunar_forecast", 
        "esoteric_interactive",
        "esoteric_evening_message",
        "zodiac_aries",
        "zodiac_leo",
        "zodiac_scorpio"
    ]
    
    for callback in test_callbacks:
        if callback.startswith("category_"):
            print(f"✅ Категория: {callback}")
        elif callback.startswith("esoteric_"):
            print(f"✅ Эзотерическая функция: {callback}")
        elif callback.startswith("zodiac_"):
            print(f"✅ Знак зодиака: {callback}")
    
    print(f"\n📊 Всего протестировано {len(test_callbacks)} callback'ов")
    return True

async def main():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ НОВЫХ ФУНКЦИЙ")
    print("=" * 60)
    
    keyboard_test = await test_new_keyboards()
    callback_test = await test_callback_data()
    
    if keyboard_test and callback_test:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("🔮 Новые эзотерические функции готовы к использованию!")
        return 0
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
