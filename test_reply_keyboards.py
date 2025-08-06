from telegram import InlineKeyboardMarkup

from utils.keyboards import create_main_menu_keyboard


def test_create_main_menu_keyboard_structure():
    """create_main_menu_keyboard should build the expected keyboard."""
    keyboard = create_main_menu_keyboard()

    assert isinstance(keyboard, InlineKeyboardMarkup)
    # Expect three rows: two categories rows + one for relationships
    assert len(keyboard.inline_keyboard) == 3
    first_row = keyboard.inline_keyboard[0]
    assert first_row[0].callback_data == "category_motivation"
    assert first_row[1].callback_data == "category_esoteric"
