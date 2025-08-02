#!/usr/bin/env python3
"""
Тестовый скрипт для публикации поста в канал
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = '-1002510932658'

# Эмодзи и названия реакций
REACTION_EMOJIS = ["❤️", "🙏", "🥹"]
REACTION_NAMES = ["heart", "pray", "touched"]

# Знаки зодиака
ZODIAC_SIGNS = [
    ("Овен", "🐏"), ("Телец", "🐂"), ("Близнецы", "👯‍♂️"), ("Рак", "🦀"),
    ("Лев", "🦁"), ("Дева", "👸"), ("Весы", "⚖️"), ("Скорпион", "🦂"),
    ("Стрелец", "🏹"), ("Козерог", "🐐"), ("Водолей", "🌊"), ("Рыбы", "🐟")
]

def create_reaction_keyboard(post_id):
    """Создает клавиатуру с реакциями"""
    reaction_buttons = []
    for i in range(3):
        emoji = REACTION_EMOJIS[i]
        name = REACTION_NAMES[i]
        button_text = f"{emoji} 0"
        reaction_buttons.append(InlineKeyboardButton(button_text, callback_data=f"react_{name}_{post_id}"))
    
    return [reaction_buttons]

def create_zodiac_keyboard():
    """Создает клавиатуру знаков зодиака"""
    keyboard = []
    for name, emoji in ZODIAC_SIGNS:
        button = InlineKeyboardButton(f"{emoji} {name}", callback_data=f"zodiac_{name}")
        keyboard.append([button])  # Каждый знак на отдельной строке
    return keyboard

async def publish_test_post():
    """Публикует тестовый пост с гороскопом"""
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден")
        return False
        
    # Генерируем уникальный ID поста
    post_id = f"test_horoscope_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Путь к изображению гороскопа
    image_path = os.path.expanduser("~/Desktop/images/гороскоп2августа.jpg")
    
    try:
        # Создаем Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Инициализируем bot
        await application.initialize()
        
        # Создаем клавиатуру
        keyboard = create_zodiac_keyboard() + create_reaction_keyboard(post_id)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Текст для поста
        caption = "🌟 Тестовая публикация гороскопа на 2 августа! Узнайте, что звезды приготовили именно для вашего знака зодиака. Выберите свой знак и откройте персональное предсказание! ✨"
        
        print(f"📤 Публикуем тестовый пост с ID: {post_id}")
        print(f"🖼️ Изображение: {image_path}")
        print(f"📝 Подпись: {caption[:50]}...")
        
        # Отправляем фото с клавиатурой
        with open(image_path, 'rb') as photo:
            message = await application.bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
        
        print(f"✅ Пост успешно опубликован!")
        print(f"📎 ID сообщения в канале: {message.message_id}")
        print(f"🔗 Пост содержит {len(ZODIAC_SIGNS)} кнопок знаков зодиака и 3 кнопки реакций")
        
        # Останавливаем application
        await application.shutdown()
        return True
        
    except FileNotFoundError:
        print(f"❌ Ошибка: файл изображения не найден: {image_path}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при публикации: {e}")
        return False

async def main():
    """Главная функция"""
    print("🚀 Запуск тестовой публикации...")
    
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        return
    
    success = await publish_test_post()
    
    if success:
        print("🎉 Тестовая публикация завершена успешно!")
    else:
        print("💥 Тестовая публикация не удалась")

if __name__ == "__main__":
    asyncio.run(main())
