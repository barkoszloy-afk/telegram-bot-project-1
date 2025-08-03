# utils/keyboards.py - Минимальная версия с базовым меню
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

def get_main_menu_keyboard():
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
    return keyboard

def create_main_menu_keyboard():
    """Создает InlineKeyboardMarkup для главного меню"""
    return InlineKeyboardMarkup(get_main_menu_keyboard())

def remove_reply_keyboard():
    """Удаляет reply клавиатуру"""
    return ReplyKeyboardRemove()
