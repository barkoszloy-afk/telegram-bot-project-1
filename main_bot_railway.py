# main_bot_railway.py - Версия для Railway с webhook (v1.1)
import logging
import asyncio
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from flask import Flask, request, jsonify
import threading

# Импорты из наших модулей
from config import (
    BOT_TOKEN, ADMIN_ID, validate_config,
    CONNECT_TIMEOUT, READ_TIMEOUT, WRITE_TIMEOUT, POOL_TIMEOUT
)
from utils.database import reactions_db
from handlers.reactions import handle_reaction_callback
from handlers.admin import (
    handle_admin_command, handle_admin_callback, 
    handle_morning_variant_callback
)

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

# Flask app для healthcheck
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Healthcheck endpoint для Railway"""
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "timestamp": str(asyncio.get_event_loop().time())
    }), 200

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        "message": "Telegram Bot is running on Railway",
        "status": "active"
    }), 200

# Глобальные переменные
application = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    if not update.message:
        return
        
    welcome_message = (
        "🤖 **Добро пожаловать в астрологический бот!**\n\n"
        "Этот бот поможет вам получать ежедневные гороскопы "
        "и вдохновляющие сообщения.\n\n"
        "🔮 **Доступные команды:**\n"
        "• /help - справка по командам\n"
        "• /admin - панель администратора (только для админа)\n\n"
        "✨ Наслаждайтесь астрологическими прогнозами!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    if not update.message:
        return
        
    help_message = (
        "📚 **Справка по боту**\n\n"
        "🔮 **Основные функции:**\n"
        "• Ежедневные гороскопы для всех знаков зодиака\n"
        "• Утренние мотивационные сообщения\n"
        "• Вечерние размышления\n"
        "• Система реакций на посты\n\n"
        "⚡ **Команды:**\n"
        "• /start - начать работу с ботом\n"
        "• /help - показать эту справку\n"
        "• /admin - админ-панель (только для администратора)\n\n"
        "💫 Выберите свой знак зодиака в постах и получайте персональные прогнозы!"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback-запросов"""
    query = update.callback_query
    if not query or not query.data:
        return
    
    try:
        if query.data.startswith('admin_'):
            await handle_admin_callback(update, context)
        elif query.data.startswith('morning_variant'):
            await handle_morning_variant_callback(update, context)
        elif query.data.startswith('reaction_'):
            await handle_reaction_callback(update, context)
        else:
            logger.warning(f"Неизвестный callback: {query.data}")
            await query.answer("❌ Неизвестная команда")
    except Exception as e:
        logger.error(f"Ошибка обработки callback {query.data}: {e}")
        await query.answer("❌ Произошла ошибка")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    message_text = update.message.text.lower()
    
    # Список запрещённых слов
    forbidden_words = ['спам', 'реклама', 'купить']
    
    if any(word in message_text for word in forbidden_words):
        await update.message.reply_text("⚠️ Сообщение содержит запрещённый контент")
        return
    
    # Простой ответ на текстовые сообщения
    await update.message.reply_text(
        "🤖 Спасибо за сообщение! Используйте команды /start или /help для навигации."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")

def run_flask():
    """Запуск Flask сервера в отдельном потоке"""
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

async def setup_webhook():
    """Настройка webhook для Railway"""
    global application
    
    # Проверка токена
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    # Создание приложения с таймаутами для Railway
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(CONNECT_TIMEOUT)
        .read_timeout(READ_TIMEOUT)
        .write_timeout(WRITE_TIMEOUT)
        .pool_timeout(POOL_TIMEOUT)
        .build()
    )
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", handle_admin_command))
    
    # Регистрация обработчика callback-запросов
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Регистрация обработчика текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)
    
    # Инициализация приложения
    await application.initialize()
    
    # Получение Railway URL или использование локального тестирования
    railway_url = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    if railway_url:
        webhook_url = f"https://{railway_url}/webhook/{BOT_TOKEN}"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"🌐 Webhook установлен: {webhook_url}")
        # Для webhook режима просто инициализируем приложение
        await application.start()
    else:
        logger.info("🏠 Локальный режим - polling")
        # Запуск polling для локального режима  
        application.run_polling(drop_pending_updates=True)

async def run_webhook_mode():
    """Запуск в режиме webhook для Railway"""
    await setup_webhook()
    # Поддержание приложения активным для webhook
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
        if application:
            await application.stop()

async def run_polling_mode():
    """Запуск в режиме polling для локальной разработки"""
    await setup_webhook()

def main():
    """Главная функция"""
    try:
        # Валидация конфигурации
        validate_config()
        logger.info("✅ Конфигурация успешно загружена")
        
        # Проверка Railway окружения
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
        
        if is_railway:
            logger.info("🚀 Запуск в Railway режиме")
            
            # Запуск Flask сервера в отдельном потоке
            flask_thread = threading.Thread(target=run_flask, daemon=True)
            flask_thread.start()
            logger.info("🌐 Flask сервер запущен")
            
            # Настройка webhook и поддержание активности
            asyncio.run(run_webhook_mode())
        else:
            logger.info("🏠 Запуск в локальном режиме")
            # Локальный режим с polling - используем стандартный метод
            global application
            if not BOT_TOKEN:
                raise ValueError("BOT_TOKEN не найден в переменных окружения")
                
            application = (
                Application.builder()
                .token(BOT_TOKEN)
                .connect_timeout(CONNECT_TIMEOUT)
                .read_timeout(READ_TIMEOUT)
                .write_timeout(WRITE_TIMEOUT)
                .pool_timeout(POOL_TIMEOUT)
                .build()
            )
            
            # Регистрация обработчиков
            application.add_handler(CommandHandler("start", start_command))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("admin", handle_admin_command))
            application.add_handler(CallbackQueryHandler(handle_callback_query))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
            application.add_error_handler(error_handler)
            
            # Запуск polling
            application.run_polling(drop_pending_updates=True)
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        raise

if __name__ == '__main__':
    main()
