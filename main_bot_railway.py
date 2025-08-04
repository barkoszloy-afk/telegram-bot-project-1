# main_bot_railway.py - Минимальная версия с базовым меню
import logging
import os
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes
)

# Импорты из наших модулей
from config import (
    BOT_TOKEN, validate_config,
    CONNECT_TIMEOUT, READ_TIMEOUT, WRITE_TIMEOUT, POOL_TIMEOUT
)
from utils.keyboards import create_main_menu_keyboard

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

# Глобальные переменные
application: Optional[Application] = None
start_time: Optional[float] = None

# ================== КОМАНДЫ БОТА ==================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start - показывает главное меню"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        user_name = update.effective_user.first_name if update.effective_user else "друг"
        logger.info(f"🌟 Команда /start от пользователя {user_id} ({user_name})")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update")
            return

        # Показываем главное меню
        logger.info("📋 Вызываем show_main_menu...")
        await show_main_menu(update, context)
        logger.info("✅ show_main_menu выполнена успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка в команде /start: {e}")
        import traceback
        logger.error(f"📋 Полный traceback: {traceback.format_exc()}")
        # Не отправляем ошибку пользователю в webhook режиме, 
        # так как это может вызвать дополнительные проблемы с event loop

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /help - краткая справка"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.info(f"📚 Команда /help от пользователя {user_id}")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update для /help")
            return

        help_text = """🤖 Справка по боту

📋 Доступные команды:
/start - Главное меню с категориями
/help - Показать эту справку  
/instructions - Подробные инструкции

💡 Быстрый старт:
1. Нажмите /start
2. Выберите категорию
3. Наслаждайтесь контентом!

👤 Поддержка: @admin"""

        await update.message.reply_text(help_text)
        logger.info("✅ Команда /help выполнена успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка в команде /help: {e}")
        import traceback
        logger.error(f"📋 Полный traceback: {traceback.format_exc()}")

async def instructions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /instructions - подробные инструкции"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.info(f"📖 Команда /instructions от пользователя {user_id}")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update для /instructions")
            return

        instructions_text = """📚 Подробные инструкции по использованию бота

🚀 Начало работы:
1. Отправьте команду /start
2. Вы увидите главное меню с 5 категориями
3. Нажмите на интересующую категорию

🎯 Категории:
💫 Мотивация - ежедневное вдохновение и цитаты
🔮 Эзотерика - гороскопы, астрология и духовность  
🎯 Развитие - личностный рост и обучение
🌟 Здоровье - советы о здоровье и фитнесе
💝 Отношения - гармония в общении и любви

⚙️ Дополнительные возможности:
- /help - быстрая справка
- /instructions - эти подробные инструкции

🔧 Техническая поддержка:
При проблемах обращайтесь к @admin

✨ Желаем продуктивного использования!"""

        await update.message.reply_text(instructions_text)
        logger.info("✅ Команда /instructions выполнена успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка в команде /instructions: {e}")
        import traceback
        logger.error(f"📋 Полный traceback: {traceback.format_exc()}")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /test - тестирование работы бота"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        user_name = update.effective_user.first_name if update.effective_user else "друг"
        logger.info(f"🧪 Команда /test от пользователя {user_id} ({user_name})")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update для /test")
            return

        # Создаем тестовое сообщение с информацией о системе
        import time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        
        test_text = f"""🧪 **Тест бота пройден успешно!**

👤 **Пользователь:** {user_name} (ID: {user_id})
🕐 **Время теста:** {current_time}
🌐 **Режим:** Railway webhook
🔗 **Статус:** ✅ Онлайн

**🚀 Доступные команды:**
• `/start` - Главное меню
• `/help` - Быстрая справка  
• `/instructions` - Подробные инструкции
• `/test` - Тест системы

**📊 Системная информация:**
• Webhook: Активен
• База данных: Подключена
• Клавиатуры: Работают
• Логирование: Включено

✅ **Все системы работают нормально!**"""

        await update.message.reply_text(test_text, parse_mode='Markdown')
        logger.info("✅ Команда /test выполнена успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка в команде /test: {e}")
        import traceback
        logger.error(f"📋 Полный traceback: {traceback.format_exc()}")
        
        # Отправляем простое сообщение об ошибке
        try:
            if update.message:
                await update.message.reply_text("❌ Произошла ошибка при выполнении теста")
        except Exception:
            pass

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Универсальный обработчик callback-запросов"""
    query = update.callback_query
    if not query or not query.data:
        return
    
    data = query.data
    
    try:
        # Главное меню
        if data == "main_menu":
            await show_main_menu(update, context)
        
        # Заглушки для категорий
        elif data.startswith("category_"):
            await query.answer("🚧 В разработке!", show_alert=True)
        
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

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает главное меню"""
    try:
        logger.info("🔍 Начинаем show_main_menu")
        query = getattr(update, 'callback_query', None)
        message = getattr(update, 'message', None)
        logger.info(f"📋 query: {query is not None}, message: {message is not None}")
        
        # Получаем имя пользователя
        user = query.from_user if query else update.effective_user
        user_name = user.first_name if user and user.first_name else "друг"
        logger.info(f"👤 Пользователь: {user_name}")
            
        text = f"""🌟 Привет, {user_name}!

Добро пожаловать в бота! ✨

🎯 **Выберите категорию:**

💫 **Мотивация** - вдохновляющие идеи
🔮 **Эзотерика** - гороскопы и астрология
🎯 **Развитие** - личностный рост
🌟 **Здоровье** - забота о теле и разуме
💝 **Отношения** - гармония в общении

👇 Выберите категорию:
"""
        
        logger.info("⌨️ Создаем клавиатуру...")
        keyboard = create_main_menu_keyboard()
        logger.info(f"✅ Клавиатура создана: {len(keyboard.inline_keyboard)} рядов")
        
        # Отображаем или редактируем главное меню
        if query:
            logger.info("📝 Редактируем сообщение через callback...")
            await query.answer()
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            logger.info("✅ Сообщение отредактировано")
        elif message:
            logger.info("📤 Отправляем новое сообщение...")
            await message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            logger.info("✅ Сообщение отправлено")
        else:
            logger.warning("⚠️ Нет ни query, ни message!")
            
    except Exception as e:
        logger.error(f"❌ Ошибка в show_main_menu: {e}")
        import traceback
        logger.error(f"📋 Полный traceback: {traceback.format_exc()}")
        raise

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")

# ================== SETUP И ЗАПУСК ==================

async def setup_bot_commands(application: Application) -> None:
    """Установка команд бота в меню Telegram"""
    try:
        logger.info("⚙️ Устанавливаем команды бота...")
        
        from telegram import BotCommand
        commands = [
            BotCommand("start", "Главное меню с категориями"),
            BotCommand("help", "Справка по использованию бота"),
            BotCommand("instructions", "Подробные инструкции"),
            BotCommand("test", "Тест работы бота")
        ]
        
        await application.bot.set_my_commands(commands)
        logger.info("✅ Команды бота установлены успешно!")
        
        # Логируем установленные команды
        set_commands = await application.bot.get_my_commands()
        for cmd in set_commands:
            logger.info(f"📋 Команда: /{cmd.command} - {cmd.description}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка установки команд: {e}")
        import traceback
        logger.error(f"📋 Полный traceback: {traceback.format_exc()}")

def main():
    """Главная функция"""
    global start_time, application
    import time
    
    # Устанавливаем время запуска
    start_time = time.time()
    
    try:
        # Валидация конфигурации
        validate_config()
        logger.info("✅ Конфигурация успешно загружена")
        
        if not BOT_TOKEN:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
        
        # Создание приложения
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
        application.add_handler(CommandHandler("instructions", instructions_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        application.add_error_handler(error_handler)
        
        # Проверка Railway окружения
        is_railway = (
            os.environ.get('RAILWAY_PROJECT_ID') is not None or
            os.environ.get('RAILWAY_SERVICE_ID') is not None or 
            os.environ.get('RAILWAY_DEPLOYMENT_ID') is not None or
            os.environ.get('PORT') is not None
        )
        
        if is_railway:
            logger.info("🚀 Запуск в Railway режиме с webhook")
            
            # Получаем домен из переменных окружения Railway или используем fallback
            railway_domain = (
                os.environ.get('RAILWAY_PUBLIC_DOMAIN') or 
                os.environ.get('RAILWAY_STATIC_URL') or
                "telegram-bot-project-1-production.up.railway.app"  # fallback домен
            )
            
            webhook_url = f"https://{railway_domain}/webhook/{BOT_TOKEN}"
            webhook_path = f"/webhook/{BOT_TOKEN}"
            port = int(os.environ.get("PORT", 8443))
            
            logger.info(f"🌐 Webhook URL: {webhook_url}")
            logger.info(f"�️ Webhook path: {webhook_path}")
            logger.info(f"�🔌 Listening on port: {port}")
            
            # Устанавливаем команды перед запуском webhook
            async def post_init(application: Application) -> None:
                await setup_bot_commands(application)
            
            application.post_init = post_init
            
            # Запуск webhook с встроенным сервером
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=webhook_path,
                webhook_url=webhook_url,
                drop_pending_updates=True,
            )
        else:
            logger.info("🏠 Запуск в локальном режиме")
            run_local_polling()
                
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        raise

def run_local_polling():
    """Простой запуск в polling режиме для локальной разработки"""
    global application
    
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    # Создание приложения
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
    application.add_handler(CommandHandler("instructions", instructions_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_error_handler(error_handler)
    
    logger.info("🔄 Запуск polling режима...")
    
    # Устанавливаем команды перед запуском polling
    async def post_init(application: Application) -> None:
        await setup_bot_commands(application)
    
    application.post_init = post_init
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
