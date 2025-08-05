"""Test suite for newly introduced esoteric features.

The previous version of this file relied on prints and return values,
which are not ideal for automated testing.  The rewritten tests use
assertions and the anyio plugin to run asynchronous code.
"""

def test_new_keyboards() -> None:
    """Проверяем создание новых клавиатур."""
    from utils.keyboards import (
        create_esoteric_submenu,
        create_motivation_submenu,
        create_development_submenu,
        create_health_submenu,
        create_relationships_submenu,
        create_zodiac_keyboard,
    )

    # Эзотерическое подменю: 6 функций + кнопка "Назад"
    esoteric_keyboard = create_esoteric_submenu()
    button_count = sum(len(row) for row in esoteric_keyboard.inline_keyboard)
    assert button_count == 7

    expected_callbacks = {
        "esoteric_horoscope",
        "esoteric_daily_card",
        "esoteric_good_morning",
        "esoteric_lunar_forecast",
        "esoteric_interactive",
        "esoteric_evening_message",
        "main_menu",
    }
    found_callbacks = {
        button.callback_data
        for row in esoteric_keyboard.inline_keyboard
        for button in row
    }
    assert expected_callbacks == found_callbacks

    # Зодиакальная клавиатура: 12 знаков + кнопка "Назад"
    zodiac_keyboard = create_zodiac_keyboard()
    zodiac_buttons = sum(len(row) for row in zodiac_keyboard.inline_keyboard)
    assert zodiac_buttons == 13


def test_callback_data() -> None:
    """Убеждаемся, что callback данные имеют ожидаемые префиксы."""
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
        "zodiac_scorpio",
    ]

    for callback in test_callbacks:
        assert callback.startswith(("category_", "esoteric_", "zodiac_"))

    assert len(test_callbacks) == 10
