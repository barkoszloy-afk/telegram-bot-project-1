# main_bot_railway.py - Минимальная версия с базовым меню
import logging
import asyncio
import os
from typing import Dict, Any, Optional
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from flask import Flask, request, jsonify, Response
from flask.typing import ResponseReturnValue
import threading

# Импорты из наших модулей
from config import (
    BOT_TOKEN, ADMIN_ID, validate_config,
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

# Flask app для healthcheck
app = Flask(__name__)

@app.route('/health')
def health_check() -> ResponseReturnValue:
    """Healthcheck endpoint для Railway"""
    import time
    global application, start_time
    
    # Проверяем состояние бота
    bot_status = "unknown"
    if application:
        try:
            bot_status = "running" if application.running else "stopped"
        except:
            bot_status = "error"
    
    # Считаем uptime
    uptime: float = 0.0
    if start_time:
        uptime = time.time() - start_time
    
    return jsonify({
        "status": "healthy",
        "bot": bot_status,
        "timestamp": str(time.time()),
        "uptime_seconds": round(uptime, 2)
    }), 200

@app.route('/')
def index() -> ResponseReturnValue:
    """Главная страница"""
    return jsonify({
        "message": "Telegram Bot is running on Railway",
        "status": "active"
    }), 200

@app.route('/logs')
def get_logs() -> ResponseReturnValue:
    """Показать последние записи из лога"""
    try:
        import os
        log_file = 'bot.log'
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Берем последние 50 строк
                last_lines = lines[-50:] if len(lines) > 50 else lines
                return jsonify({
                    "logs": last_lines,
                    "total_lines": len(lines),
                    "showing_last": len(last_lines)
                }), 200
        else:
            return jsonify({
                "error": "Log file not found",
                "logs": []
            }), 404
    except Exception as e:
        return jsonify({
            "error": f"Error reading logs: {str(e)}",
            "logs": []
        }), 500

# Глобальные переменные
application: Optional[Application] = None
start_time: Optional[float] = None

def setup_webhook_route() -> None:
    """Настройка webhook route после импорта конфигурации"""
    @app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
    def webhook() -> ResponseReturnValue:
        """Обработчик webhook запросов от Telegram"""
        try:
            # Получаем JSON данные от Telegram
            json_data = request.get_json()
            if not json_data:
                logger.warning("⚠️ Webhook получил пустые данные")
                return "No data", 400
            
            # Создаем Update объект из JSON данных  
            if application and application.bot:
                update = Update.de_json(json_data, application.bot)
                if update:
                    # Простая синхронная обработка
                    import threading
                    import asyncio
                    
                    def run_async_update() -> None:
                        try:
                            # Используем asyncio.run() вместо создания loop вручную
                            if application:
                                logger.info(f"🔄 Начинаем обработку update")
                                asyncio.run(application.process_update(update))
                                logger.info(f"✅ Webhook обработал update")
                            else:
                                logger.error("❌ Application отсутствует при обработке")
                            
                        except Exception as e:
                            logger.error(f"❌ Ошибка async обработки: {e}")
                            import traceback
                            logger.error(f"📋 Полный traceback: {traceback.format_exc()}")
                    
                    # Запускаем в отдельном потоке
                    thread = threading.Thread(target=run_async_update, daemon=True)
                    thread.start()
                else:
                    logger.warning("⚠️ Не удалось создать Update объект")
            else:
                logger.error("❌ Application или bot не инициализированы")
            
            return "OK", 200
        except Exception as e:
            logger.error(f"❌ Ошибка обработки webhook: {e}")
            return "Error", 500

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
            BotCommand("instructions", "Подробные инструкции")
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
    application.add_handler(CommandHandler("instructions", instructions_command))
    
    # Регистрация обработчика callback-запросов
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)
    
    # Инициализация приложения
    await application.initialize()
    
    # Установка команд бота в меню Telegram
    await setup_bot_commands(application)
    
    # Получение Railway URL для webhook
    webhook_url = None
    
    # Вариант 1: Переменная WEBHOOK_URL (устанавливается вручную)
    manual_webhook = os.environ.get('WEBHOOK_URL')
    if manual_webhook:
        if not manual_webhook.startswith('https://'):
            manual_webhook = f"https://{manual_webhook}"
        webhook_url = f"{manual_webhook}/webhook/{BOT_TOKEN}"
        
    # Вариант 2: RAILWAY_PUBLIC_DOMAIN (автоматически от Railway)
    elif os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        webhook_url = f"https://{railway_domain}/webhook/{BOT_TOKEN}"
        
    # Вариант 3: Fallback домен
    if not webhook_url:
        fallback_domain = "telegram-bot-project-1-production.up.railway.app"
        webhook_url = f"https://{fallback_domain}/webhook/{BOT_TOKEN}"
        logger.info(f"🔄 Используем fallback домен: {fallback_domain}")
    
    # Railway окружение
    is_railway_env = (
        os.environ.get('RAILWAY_PROJECT_ID') is not None or
        os.environ.get('PORT') is not None
    )
    
    if webhook_url:
        await application.bot.set_webhook(webhook_url)
        logger.info(f"🌐 Webhook установлен: {webhook_url}")
    elif is_railway_env:
        await application.bot.delete_webhook()
        logger.info("⚠️ Webhook очищен - добавьте WEBHOOK_URL переменную!")
    else:
        logger.info("🏠 Локальный режим - polling")
        return False
        
    # Для webhook режима просто инициализируем приложение
    await application.start()
    logger.info("✅ Приложение запущено в webhook режиме")
    return True

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

def main():
    """Главная функция"""
    global start_time
    import time
    
    # Устанавливаем время запуска
    start_time = time.time()
    
    try:
        # Валидация конфигурации
        validate_config()
        logger.info("✅ Конфигурация успешно загружена")
        
        # Настройка webhook route после загрузки конфигурации
        setup_webhook_route()
        
        # Проверка Railway окружения
        is_railway = (
            os.environ.get('RAILWAY_PROJECT_ID') is not None or
            os.environ.get('RAILWAY_SERVICE_ID') is not None or 
            os.environ.get('RAILWAY_DEPLOYMENT_ID') is not None or
            os.environ.get('PORT') is not None
        )
        
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
