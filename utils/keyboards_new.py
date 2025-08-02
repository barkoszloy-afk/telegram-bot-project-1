# utils/keyboards.py - Утилиты для создания клавиатур
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ZODIAC_SIGNS, REACTION_EMOJIS, REACTION_NAMES
from .database import reactions_db

def get_zodiac_keyboard():
    """Создает клавиатуру с знаками зодиака"""
    keyboard = []
    
    # Создаем кнопки по 3 в ряд
    for i in range(0, len(ZODIAC_SIGNS), 3):
        row = []
        for j in range(i, min(i + 3, len(ZODIAC_SIGNS))):
            sign_name, sign_emoji = ZODIAC_SIGNS[j]
            button = InlineKeyboardButton(
                text=f"{sign_emoji} {sign_name}",
                callback_data=f"zodiac_{sign_name.lower()}"
            )
            row.append(button)
        keyboard.append(row)
    
    return keyboard

def get_morning_variants_keyboard():
    """Создает клавиатуру для утренних вариантов"""
    keyboard = [
        [InlineKeyboardButton("🌅 Заряд энергии", callback_data='morning_variant1')],
        [InlineKeyboardButton("🌞 Путь к победам", callback_data='morning_variant2')],
        [InlineKeyboardButton("⭐ Звездный путь", callback_data='morning_variant3')]
    ]
    return keyboard

def get_reaction_keyboard(post_id: str):
    """Создает клавиатуру с реакциями и счетчиками"""
    data = reactions_db.data
    post_reactions = data.get('posts', {}).get(post_id, {})
    
    keyboard = []
    for i, (emoji, reaction_name) in enumerate(zip(REACTION_EMOJIS, REACTION_NAMES)):
        count = post_reactions.get(reaction_name, 0)
        button_text = f"{emoji} {count}" if count > 0 else emoji
        
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"react_{reaction_name}_{post_id}"
        )
        keyboard.append([button])
    
    return keyboard

def create_admin_post_keyboard(post_id: str, keyboard_type: str = 'zodiac'):
    """Создает клавиатуру для админских постов"""
    keyboard = []
    
    if keyboard_type == 'morning':
        # Утренний пост - добавляем варианты утра
        keyboard.extend(get_morning_variants_keyboard())
    else:
        # Обычный пост - добавляем зодиак
        keyboard.extend(get_zodiac_keyboard())
    
    # Добавляем реакции
    keyboard.extend(get_reaction_keyboard(post_id))
    
    return InlineKeyboardMarkup(keyboard)

def create_post_keyboard(post_id: str, has_morning_variants: bool = False):
    """Создает клавиатуру для обычных постов"""
    keyboard = []
    
    if has_morning_variants:
        keyboard.extend(get_morning_variants_keyboard())
    else:
        keyboard.extend(get_zodiac_keyboard())
    
    keyboard.extend(get_reaction_keyboard(post_id))
    
    return InlineKeyboardMarkup(keyboard)
