# main_bot_minimal.py - Минимальная рабочая версия для Railway
import logging
import os
import threading
import asyncio
import time
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from flask import Flask, request, jsonify

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Получаем токен
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Глобальные переменные
application = None
start_time = time.time()

# Flask app
app = Flask(__name__)

@app.route('/health')
def health():
    uptime = time.time() - start_time
    return jsonify({
        'status': 'healthy',
        'uptime_seconds': round(uptime, 2),
        'service': 'telegram-bot-minimal',
        'version': '1.0.0'
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'Telegram Bot Minimal Version',
        'status': 'online'
    })

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """Webhook endpoint для Telegram"""
    try:
        logger.info("🎯 Webhook получил запрос")
        
        if not application:
            logger.error("❌ Application не инициализирован!")
            return '', 500
            
        data = request.get_json()
        if not data:
            logger.warning("❌ Пустые данные")
            return '', 400
            
        logger.info(f"📨 Update ID: {data.get('update_id', 'unknown')}")
        
        # Логируем сообщение
        if 'message' in data:
            msg = data['message']
            text = msg.get('text', '')
            user_id = msg.get('from', {}).get('id', 'unknown')
            logger.info(f"👤 Пользователь {user_id}: {text}")
        
        # Создаем Update объект
        update = Update.de_json(data, application.bot)
        
        # Обрабатываем в отдельном потоке
        def process():
            try:
                logger.info("🔄 Обработка update...")
                asyncio.run(application.process_update(update))
                logger.info("✅ Update обработан")
            except Exception as e:
                logger.error(f"❌ Ошибка обработки: {e}")
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
        
        return '', 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка webhook: {e}")
        return '', 500

# Команды бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_name = update.effective_user.first_name if update.effective_user else "друг"
    await update.message.reply_text(f"🌟 Привет, {user_name}! Бот работает!")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /test"""
    await update.message.reply_text("✅ Тест прошел успешно! Webhook работает!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
📋 Доступные команды:

/start - Приветствие
/test - Тест работы
/help - Эта справка

🤖 Минимальная версия бота работает!
"""
    await update.message.reply_text(help_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text("🤖 Сообщение получено! Используйте /help")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")

def main():
    """Главная функция"""
    global application
    
    logger.info("🚀 Запуск минимальной версии бота")
    
    # Создаем приложение СРАЗУ
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)
    
    logger.info("✅ Application создан и настроен")
    
    # Устанавливаем webhook
    async def setup_webhook():
        webhook_url = f"https://telegram-bot-project-1-production.up.railway.app/webhook/{BOT_TOKEN}"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"✅ Webhook установлен: {webhook_url}")
    
    # Запускаем setup
    def run_setup():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(setup_webhook())
        loop.close()
    
    setup_thread = threading.Thread(target=run_setup)
    setup_thread.start()
    setup_thread.join()
    
    # Запускаем Flask
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Запуск Flask на порту {port}")
    
    def run_flask():
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Поддерживаем основной поток
    logger.info("🔄 Основной поток активен")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Остановка")

if __name__ == '__main__':
    main()
