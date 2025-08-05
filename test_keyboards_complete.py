# test_keyboards_complete.py - Полный тест клавиатур
import unittest
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.keyboards import (
    create_main_menu_keyboard,
    create_submenu_keyboard,
    get_reaction_keyboard,
    create_zodiac_keyboard,
    create_back_to_menu_keyboard
)
from config import REACTION_EMOJIS, ZODIAC_SIGNS

class TestKeyboards(unittest.TestCase):
    """Тестируем все функции создания клавиатур"""

    def test_create_main_menu_keyboard(self):
        """Тест главного меню"""
        keyboard = create_main_menu_keyboard()
        self.assertIsInstance(keyboard, InlineKeyboardMarkup)
        self.assertEqual(len(keyboard.inline_keyboard), 4)
        self.assertEqual(len(keyboard.inline_keyboard[0]), 2)
        self.assertEqual(len(keyboard.inline_keyboard[3]), 2)
        self.assertEqual(keyboard.inline_keyboard[3][0].callback_data, "category_about")
        self.assertEqual(keyboard.inline_keyboard[3][1].callback_data, "category_settings")
        print("✅ Главное меню: OK")

    def test_create_submenu_keyboard(self):
        """Тест подменю"""
        keyboard = create_submenu_keyboard("motivation")
        self.assertIsInstance(keyboard, InlineKeyboardMarkup)
        self.assertEqual(len(keyboard.inline_keyboard), 2)
        self.assertEqual(keyboard.inline_keyboard[0][0].callback_data, "get_post_motivation")
        print("✅ Подменю: OK")

    def test_get_reaction_keyboard(self):
        """Тест клавиатуры реакций"""
        post_id = "123"
        keyboard = get_reaction_keyboard(post_id)
        self.assertIsInstance(keyboard, InlineKeyboardMarkup)
        
        # Проверяем, что есть 2 ряда кнопок
        self.assertEqual(len(keyboard.inline_keyboard), 2)
        
        # Проверяем ряд с реакциями
        reaction_row = keyboard.inline_keyboard[0]
        self.assertEqual(len(reaction_row), len(REACTION_EMOJIS))
        
        # Проверяем, что каждая кнопка - это InlineKeyboardButton
        for i, button in enumerate(reaction_row):
            self.assertIsInstance(button, InlineKeyboardButton)
            self.assertEqual(button.text, REACTION_EMOJIS[i])
            self.assertEqual(button.callback_data, f"reaction_{i}_{post_id}")
        
        # Проверяем кнопку статистики
        stats_button = keyboard.inline_keyboard[1][0]
        self.assertEqual(stats_button.text, "📊 Статистика")
        self.assertEqual(stats_button.callback_data, f"stats_{post_id}")
        
        print("✅ Клавиатура реакций: OK")

    def test_create_zodiac_keyboard(self):
        """Тест клавиатуры знаков зодиака"""
        keyboard = create_zodiac_keyboard()
        self.assertIsInstance(keyboard, InlineKeyboardMarkup)
        # 4 ряда знаков + 1 ряд "назад"
        self.assertEqual(len(keyboard.inline_keyboard), 5)
        self.assertEqual(len(keyboard.inline_keyboard[0]), 3)
        print("✅ Клавиатура знаков зодиака: OK")

    def test_create_back_to_menu_keyboard(self):
        """Тест кнопки 'назад'"""
        keyboard = create_back_to_menu_keyboard()
        self.assertIsInstance(keyboard, InlineKeyboardMarkup)
        self.assertEqual(len(keyboard.inline_keyboard), 1)
        self.assertEqual(keyboard.inline_keyboard[0][0].text, "🔙 Главное меню")
        print("✅ Кнопка 'назад': OK")

if __name__ == '__main__':
    print("🔍 ТЕСТИРОВАНИЕ ВСЕХ КЛАВИАТУР")
    print("="*40)
    unittest.main(verbosity=0)
    print("\n🎉 ВСЕ ТЕСТЫ КЛАВИАТУР ПРОШЛИ УСПЕШНО!")
