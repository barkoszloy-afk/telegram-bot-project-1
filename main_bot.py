# main_bot_refactored.py - Улучшенная версия бота
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    if not update.message:
        return
        
    user_name = update.effective_user.first_name if update.effective_user else "друг"
    welcome_text = f"""
🌟 Привет, {user_name}!

Это канал астрологии и саморазвития! ✨

Здесь вы найдете:
🔮 Ежедневные гороскопы
🌅 Утренние мотивации
🌙 Вечерние размышления
⭐ Астрологические советы

Подписывайтесь на канал и оставляйте реакции на посты! 💫
"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    if not update.message:
        return
        
    help_text = """
🔧 Доступные команды:

/start - Приветствие и информация о боте
/help - Показать эту справку
/admin - Админ-панель (только для администратора)

📱 Как пользоваться:
• Читайте посты в канале
• Ставьте реакции ❤️🙏🥹
• Выбирайте свой знак зодиака
• Участвуйте в утренних голосованиях

💫 Наслаждайтесь контентом!
"""
    await update.message.reply_text(help_text)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик callback-запросов"""
    query = update.callback_query
    if not query or not query.data:
        return
    
    data = query.data
    
    try:
        # Реакции на посты
        if data.startswith("react_"):
            await handle_reaction_callback(update, context)
        
        # Утренние варианты
        elif data.startswith("morning_variant"):
            await handle_morning_variant_callback(update, context)
        
        # Админские команды
        elif data.startswith("admin_"):
            await handle_admin_callback(update, context)
        
        # Зодиакальные знаки
        elif data.startswith("zodiac_"):
            await query.answer("✨ Спасибо за выбор знака зодиака!")
        
        # Неизвестная команда
        else:
            await query.answer("❓ Неизвестная команда")
            logger.warning(f"Неизвестный callback: {data}")
    
    except Exception as e:
        logger.error(f"Ошибка обработки callback {data}: {e}")
        try:
            await query.answer("❌ Произошла ошибка")
        except:
            pass

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.lower()
    
    # Простые ответы на ключевые слова
    if any(word in text for word in ['привет', 'hello', 'hi']):
        await update.message.reply_text("🌟 Привет! Добро пожаловать!")
    elif any(word in text for word in ['спасибо', 'благодарю', 'thanks']):
        await update.message.reply_text("💫 Всегда пожалуйста!")
    elif any(word in text for word in ['гороскоп', 'астрология']):
        await update.message.reply_text("🔮 Следите за нашими ежедневными гороскопами в канале!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка обновления: {context.error}")
    
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
            )
        except:
            pass

def main():
    """Главная функция запуска бота"""
    try:
        # Валидация конфигурации
        validate_config()
        logger.info("✅ Конфигурация проверена")
        
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        
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
        
        # Запуск бота
        logger.info("🤖 Бот запущен и готов к работе!")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        raise

if __name__ == '__main__':
    main()
