# main_bot_simple.py - Упрощенная версия бота без лишних зависимостей
from flask import Flask, request, jsonify
import requests
import json
import os
import logging
import sys
from threading import Thread
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Базовые команды
def handle_start_command(chat_id, token):
    """Обработка команды /start"""
    welcome_text = """
🎉 Добро пожаловать в бота "Это всё ты"!

Доступные команды:
/start - показать это сообщение
/help - получить помощь
/chat - начать диалог с ChatGPT
/zodiac - узнать свой знак зодиака
/reaction - получить случайную реакцию

Просто отправьте любое сообщение для диалога с ChatGPT!
    """
    send_message(chat_id, welcome_text, token)

def handle_help_command(chat_id, token):
    """Обработка команды /help"""
    help_text = """
ℹ️ Помощь по командам:

/start - приветственное сообщение
/help - эта справка
/chat <текст> - диалог с ChatGPT
/zodiac <дата> - знак зодиака (например: /zodiac 15.07)
/reaction - случайная реакция

💬 Или просто отправьте любое сообщение для общения с ChatGPT!
    """
    send_message(chat_id, help_text, token)

def handle_chat_command(chat_id, text, token):
    """Обработка команды /chat или обычного текста"""
    try:
        # Простой ответ от ChatGPT (заглушка)
        response_text = f"🤖 ChatGPT: Вы написали: '{text}'\n\nЭто тестовый ответ от упрощенной версии бота."
        send_message(chat_id, response_text, token)
    except Exception as e:
        logger.error(f"Ошибка в ChatGPT: {e}")
        send_message(chat_id, "❌ Произошла ошибка при обработке сообщения", token)

def handle_zodiac_command(chat_id, date_text, token):
    """Обработка команды /zodiac"""
    zodiac_signs = {
        "aries": "♈ Овен (21.03 - 19.04)",
        "taurus": "♉ Телец (20.04 - 20.05)",
        "gemini": "♊ Близнецы (21.05 - 20.06)",
        "cancer": "♋ Рак (21.06 - 22.07)",
        "leo": "♌ Лев (23.07 - 22.08)",
        "virgo": "♍ Дева (23.08 - 22.09)",
        "libra": "♎ Весы (23.09 - 22.10)",
        "scorpio": "♏ Скорпион (23.10 - 21.11)",
        "sagittarius": "♐ Стрелец (22.11 - 21.12)",
        "capricorn": "♑ Козерог (22.12 - 19.01)",
        "aquarius": "♒ Водолей (20.01 - 18.02)",
        "pisces": "♓ Рыбы (19.02 - 20.03)"
    }
    
    if not date_text:
        send_message(chat_id, "📅 Укажите дату рождения в формате ДД.ММ\nНапример: /zodiac 15.07", token)
        return
    
    # Простая логика для определения знака (заглушка)
    sign_text = "🔮 Ваш знак зодиака: ♌ Лев\n\nЭто упрощенная версия. Полная логика будет добавлена позже."
    send_message(chat_id, sign_text, token)

def handle_reaction_command(chat_id, token):
    """Обработка команды /reaction"""
    reactions = [
        "😂 Смешно!",
        "🤔 Интересно...",
        "😍 Восхитительно!",
        "🔥 Огонь!",
        "💯 Идеально!",
        "😎 Круто!",
        "🎉 Празднуем!",
        "⚡ Потрясающе!"
    ]
    
    import random
    reaction = random.choice(reactions)
    send_message(chat_id, f"🎭 Случайная реакция: {reaction}", token)

def send_message(chat_id, text, token):
    """Отправка сообщения через Telegram API"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Сообщение отправлено успешно в чат {chat_id}")
        else:
            logger.error(f"Ошибка отправки сообщения: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Исключение при отправке сообщения: {e}")

@app.route('/health')
def health():
    """Проверка здоровья сервиса"""
    return jsonify({
        "status": "healthy",
        "service": "telegram-bot-simple", 
        "version": "1.0.0",
        "python_version": sys.version.split()[0]
    })

@app.route('/webhook/<token>', methods=['POST'])
def webhook(token):
    """Обработка webhook от Telegram"""
    try:
        logger.info(f"Получен webhook от Telegram")
        
        # Получение данных
        try:
            data = request.get_json()
            if not data:
                logger.warning("Пустые данные в webhook")
                return '', 200
        except Exception as json_error:
            logger.error(f"Ошибка парсинга JSON: {json_error}")
            return 'Invalid JSON', 400
        
        # Обработка сообщения
        if 'message' in data:
            message = data['message']
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            
            if not chat_id:
                logger.warning("Отсутствует chat_id")
                return '', 200
            
            logger.info(f"Получено сообщение: '{text}' от чата {chat_id}")
            
            # Обработка команд
            if text.startswith('/start'):
                handle_start_command(chat_id, token)
            elif text.startswith('/help'):
                handle_help_command(chat_id, token)
            elif text.startswith('/chat'):
                chat_text = text[5:].strip() if len(text) > 5 else "Пустое сообщение"
                handle_chat_command(chat_id, chat_text, token)
            elif text.startswith('/zodiac'):
                date_text = text[7:].strip() if len(text) > 7 else ""
                handle_zodiac_command(chat_id, date_text, token)
            elif text.startswith('/reaction'):
                handle_reaction_command(chat_id, token)
            else:
                # Обычное сообщение - отправляем в ChatGPT
                handle_chat_command(chat_id, text, token)
        
        return '', 200
        
    except Exception as e:
        logger.error(f"Критическая ошибка в webhook: {e}")
        return 'Internal Error', 500

def run_flask():
    """Запуск Flask в отдельном потоке"""
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Запуск Flask сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    logger.info("🚀 Запуск упрощенного Telegram бота...")
    
    # Проверка BOT_TOKEN
    bot_token = os.environ.get('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN не найден в переменных окружения")
        sys.exit(1)
    
    logger.info(f"✅ BOT_TOKEN найден: {bot_token[:10]}...")
    
    # Запуск Flask
    try:
        run_flask()
    except Exception as e:
        logger.error(f"❌ Ошибка запуска Flask: {e}")
        sys.exit(1)
