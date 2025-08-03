# utils/keyboards.py - Минимальная версия с базовым меню
from typing import List, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """ГЛАВНОЕ МЕНЮ: Основные категории контента"""
    keyboard = [
        # Ряд 1: Мотивация и Эзотерика
        [
            InlineKeyboardButton("💫 Мотивация", callback_data='category_motivation'),
            InlineKeyboardButton("🔮 Эзотерика", callback_data='category_esoteric')
        ],
        # Ряд 2: Развитие и Здоровье  
        [
            InlineKeyboardButton("🎯 Развитие", callback_data='category_development'),
            InlineKeyboardButton("🌟 Здоровье", callback_data='category_health')
        ],
        # Ряд 3: Отношения (по центру)
        [
            InlineKeyboardButton("💝 Отношения", callback_data='category_relationships')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает InlineKeyboardMarkup для главного меню"""
    return get_main_menu_keyboard()

def remove_reply_keyboard() -> ReplyKeyboardRemove:
    """Удаляет reply клавиатуру"""
    return ReplyKeyboardRemove()

# Функции для админ-панели
def create_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру админ-меню"""
    keyboard = [
        [InlineKeyboardButton("📝 Создать пост", callback_data='admin_create_post')],
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_admin_post_keyboard(post_id: Optional[str] = None, post_type: Optional[str] = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру для управления постами"""
    keyboard = [
        [
            InlineKeyboardButton("🔮 Гороскоп", callback_data='admin_post_zodiac'),
            InlineKeyboardButton("🌙 Вечерний", callback_data='admin_post_evening')
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data='admin_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_admin_preview_keyboard(post_type: str, post_id: Optional[str] = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру для предпросмотра поста"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Опубликовать", callback_data=f'admin_publish_{post_type}'),
            InlineKeyboardButton("🔄 Новый", callback_data=f'admin_post_{post_type}')
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data='admin_create_post')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функции для реакций
def get_reaction_keyboard(post_id: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру с реакциями для поста"""
    keyboard = [
        [
            InlineKeyboardButton("❤️", callback_data=f'react_love_{post_id}'),
            InlineKeyboardButton("😊", callback_data=f'react_smile_{post_id}'),
            InlineKeyboardButton("🔥", callback_data=f'react_fire_{post_id}')
        ],
        [
            InlineKeyboardButton("👍", callback_data=f'react_like_{post_id}'),
            InlineKeyboardButton("🤔", callback_data=f'react_think_{post_id}'),
            InlineKeyboardButton("💯", callback_data=f'react_hundred_{post_id}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_zodiac_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с знаками зодиака"""
    keyboard = [
        [
            InlineKeyboardButton("♈ Овен", callback_data='zodiac_aries'),
            InlineKeyboardButton("♉ Телец", callback_data='zodiac_taurus'),
            InlineKeyboardButton("♊ Близнецы", callback_data='zodiac_gemini')
        ],
        [
            InlineKeyboardButton("♋ Рак", callback_data='zodiac_cancer'),
            InlineKeyboardButton("♌ Лев", callback_data='zodiac_leo'),
            InlineKeyboardButton("♍ Дева", callback_data='zodiac_virgo')
        ],
        [
            InlineKeyboardButton("♎ Весы", callback_data='zodiac_libra'),
            InlineKeyboardButton("♏ Скорпион", callback_data='zodiac_scorpio'),
            InlineKeyboardButton("♐ Стрелец", callback_data='zodiac_sagittarius')
        ],
        [
            InlineKeyboardButton("♑ Козерог", callback_data='zodiac_capricorn'),
            InlineKeyboardButton("♒ Водолей", callback_data='zodiac_aquarius'),
            InlineKeyboardButton("♓ Рыбы", callback_data='zodiac_pisces')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_morning_variants_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с вариантами утреннего настроения"""
    keyboard = [
        [
            InlineKeyboardButton("🌅 Энергичный", callback_data='morning_energetic'),
            InlineKeyboardButton("😌 Спокойный", callback_data='morning_calm')
        ],
        [
            InlineKeyboardButton("💪 Мотивированный", callback_data='morning_motivated'),
            InlineKeyboardButton("🤗 Позитивный", callback_data='morning_positive')
        ],
        [
            InlineKeyboardButton("🧘‍♀️ Медитативный", callback_data='morning_meditative'),
            InlineKeyboardButton("🎯 Целеустремленный", callback_data='morning_focused')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
