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
from utils.keyboards import create_main_menu_keyboard, remove_reply_keyboard
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
    import time
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "timestamp": str(time.time())
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

def setup_webhook_route():
    """Настройка webhook route после импорта конфигурации"""
    @app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
    def webhook():
        """Обработчик webhook запросов от Telegram"""
        try:
            # Получаем JSON данные от Telegram
            json_data = request.get_json()
            if not json_data:
                logger.warning("⚠️ Webhook получил пустые данные")
                return "No data", 400
            
            # Логируем тип полученного update
            update_type = "unknown"
            if 'message' in json_data:
                update_type = "message"
                if 'text' in json_data['message']:
                    text = json_data['message']['text']
                    logger.info(f"📥 Webhook получил сообщение: {text}")
            elif 'callback_query' in json_data:
                update_type = "callback_query"
                callback_data = json_data['callback_query'].get('data', '')
                logger.info(f"📥 Webhook получил callback: {callback_data}")
                
            # Создаем Update объект из JSON данных  
            if application and application.bot:
                update = Update.de_json(json_data, application.bot)
                if update:
                    # Простая синхронная обработка
                    import threading
                    import asyncio
                    
                    def run_async_update():
                        new_loop = None
                        try:
                            # Создаем новый event loop для этого потока
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            
                            # Обрабатываем update
                            if application:
                                new_loop.run_until_complete(application.process_update(update))
                                logger.info(f"✅ Webhook обработал {update_type}")
                            
                        except Exception as e:
                            logger.error(f"❌ Ошибка async обработки: {e}")
                        finally:
                            # Безопасно закрываем loop
                            if new_loop and not new_loop.is_closed():
                                try:
                                    new_loop.close()
                                except:
                                    pass
                    
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - показывает главное меню"""
    try:
        # Логируем вызов команды
        user_id = update.effective_user.id if update.effective_user else "unknown"
        user_name = update.effective_user.first_name if update.effective_user else "друг"
        logger.info(f"🌟 Команда /start от пользователя {user_id} ({user_name})")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update")
            return
            
        welcome_text = f"""
🌟 Привет, {user_name}!

Добро пожаловать в мир саморазвития и вдохновения! ✨

🎯 **Выберите интересующую вас тему:**

💫 **Мотивация** - вдохновляющие идеи на каждый день
🔮 **Эзотерика** - гороскопы, астрология и духовность  
🎯 **Развитие** - личностный рост и обучение
🌟 **Здоровье** - забота о теле и разуме
💝 **Отношения** - гармония в общении и любви

👇 Нажмите на кнопку ниже, чтобы начать:
"""
        
        try:
            # Отправляем приветствие с главным меню
            await update.message.reply_text(
                welcome_text, 
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            logger.info("✅ Главное меню отправлено")
            
            # Удаляем любые существующие Reply клавиатуры (отдельным сообщением)
            try:
                await update.message.reply_text(
                    "🔧 Интерфейс обновлен - используйте кнопки под сообщениями",
                    reply_markup=remove_reply_keyboard()
                )
                logger.info("✅ Reply клавиатуры удалены")
            except Exception as remove_error:
                logger.warning(f"⚠️ Не удалось удалить Reply клавиатуры: {remove_error}")
            
        except Exception as send_error:
            logger.error(f"❌ Ошибка отправки сообщения: {send_error}")
            # Попробуем отправить простое сообщение без разметки
            try:
                await update.message.reply_text(
                    f"🌟 Привет, {user_name}! Добро пожаловать!",
                    reply_markup=create_main_menu_keyboard()
                )
                logger.info("✅ Fallback сообщение отправлено")
            except Exception as fallback_error:
                logger.error(f"❌ Ошибка fallback сообщения: {fallback_error}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка в команде /start: {e}")
        if update.message:
            try:
                await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
            except:
                pass

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.info(f"📋 Команда /help от пользователя {user_id}")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update для /help")
            return
            
        help_text = """
📋 Доступные команды:

/start - Приветствие и главное меню с категориями
/help - Показать эту справку
/admin - Админ-панель (только для администратора)

📱 Как пользоваться:
• Выбирайте категории в главном меню
• Читайте мотивационный контент
• Изучайте эзотерические знания  
• Ставьте реакции ❤️👍🥹
• Выбирайте свой знак зодиака для гороскопов

💫 Откройте для себя мир саморазвития!
"""
        await update.message.reply_text(help_text)
        logger.info("✅ Справка отправлена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в команде /help: {e}")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /test для диагностики"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        logger.info(f"🧪 Команда /test от пользователя {user_id}")
        
        if not update.message:
            logger.warning("⚠️ Нет объекта message в update для /test")
            return
            
        test_text = f"""
🧪 **ТЕСТ БОТА**

✅ Webhook работает
✅ Команды обрабатываются
✅ Клавиатуры создаются
✅ Сообщения отправляются

🤖 Бот функционирует нормально!
Время: {update.message.date}
Пользователь: {user_id}
"""
        
        try:
            await update.message.reply_text(
                test_text,
                reply_markup=create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
            logger.info("✅ Тестовое сообщение отправлено")
            
        except Exception as send_error:
            logger.error(f"❌ Ошибка отправки тестового сообщения: {send_error}")
            await update.message.reply_text("🧪 Тест пройден, но есть проблемы с разметкой")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в команде /test: {e}")
        if update.message:
            try:
                await update.message.reply_text("❌ Ошибка в тесте")
            except:
                pass

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Универсальный обработчик callback-запросов"""
    query = update.callback_query
    if not query or not query.data:
        return
    
    data = query.data
    
    try:
        # Главное меню
        if data == "main_menu":
            await show_main_menu(update, context)
        
        # Категории (основные разделы)
        elif data.startswith("category_"):
            await handle_category_selection(update, context)
        
        # Подкатегории мотивации
        elif data.startswith("motivation_"):
            await handle_motivation_selection(update, context)
        
        # Подкатегории эзотерики
        elif data.startswith("esoteric_"):
            await handle_esoteric_selection(update, context)
        
        # Подкатегории развития
        elif data.startswith("development_"):
            await handle_development_selection(update, context)
        
        # Подкатегории здоровья
        elif data.startswith("health_"):
            await handle_health_selection(update, context)
        
        # Подкатегории отношений
        elif data.startswith("relationships_"):
            await handle_relationships_selection(update, context)
        
        # Реакции на посты
        elif data.startswith("react_"):
            await handle_reaction_callback(update, context)
        
        # Утренние варианты
        elif data.startswith("morning_variant"):
            await handle_morning_variant_callback(update, context)
        
        # Админские команды
        elif data.startswith("admin_"):
            await handle_admin_callback(update, context)
        
        # Зодиакальные знаки
        elif data.startswith("zodiac_"):
            await handle_zodiac_selection(update, context)
        
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
    query = update.callback_query
    if not query:
        return
        
    text = """
🏠 **ГЛАВНОЕ МЕНЮ**

Выберите интересующую вас категорию:

💫 **Мотивация** - вдохновение и энергия
🔮 **Эзотерика** - астрология и духовность  
🎯 **Развитие** - личностный рост
🌟 **Здоровье** - забота о себе
💝 **Отношения** - гармония в общении
"""
    
    await query.edit_message_text(
        text,
        reply_markup=create_main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор основной категории"""
    from utils.keyboards import (
        create_motivation_submenu, create_esoteric_submenu,
        create_development_submenu, create_health_submenu,
        create_relationships_submenu
    )
    
    query = update.callback_query
    if not query or not query.data:
        return
    
    category = query.data.replace("category_", "")
    
    if category == "motivation":
        text = """
💫 **МОТИВАЦИЯ**

Выберите тип вдохновляющего контента:

🌅 **Утренняя мотивация** - энергия на весь день
🌙 **Вечерние размышления** - итоги и планы
💪 **Преодоление трудностей** - сила духа
🎯 **Достижение целей** - путь к успеху
"""
        keyboard = create_motivation_submenu()
        
    elif category == "esoteric":
        text = """
🔮 **ЭЗОТЕРИКА**

Загляните в мир духовности:

🔮 **Гороскоп на день** - звездные советы
🌙 **Лунный календарь** - влияние луны
🔢 **Нумерология** - магия чисел
🃏 **Карты Таро** - древняя мудрость
"""
        keyboard = create_esoteric_submenu()
        
    elif category == "development":
        text = """
🎯 **РАЗВИТИЕ**

Инвестируйте в себя:

🧠 **Развитие мышления** - острый ум
📚 **Обучение и знания** - новые навыки
🎨 **Творческое развитие** - раскрытие таланта
💼 **Карьера и бизнес** - профессиональный рост
"""
        keyboard = create_development_submenu()
        
    elif category == "health":
        text = """
🌟 **ЗДОРОВЬЕ**

Заботьтесь о своем благополучии:

🏃‍♂️ **Физическая активность** - сила тела
🧘‍♀️ **Ментальное здоровье** - покой души
🥗 **Питание и диета** - энергия изнутри
😴 **Сон и отдых** - восстановление сил
"""
        keyboard = create_health_submenu()
        
    elif category == "relationships":
        text = """
💝 **ОТНОШЕНИЯ**

Гармония в общении:

💕 **Любовь и романтика** - дела сердечные
👨‍👩‍👧‍👦 **Семья и дети** - семейное счастье
👥 **Дружба и общение** - социальные связи
🤝 **Рабочие отношения** - профессиональное общение
"""
        keyboard = create_relationships_submenu()
    
    else:
        await query.answer("❓ Неизвестная категория")
        return
    
    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def handle_motivation_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе мотивации"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    query = update.callback_query
    if not query or not query.data:
        return
    
    selection = query.data.replace("motivation_", "")
    
    content_map = {
        "morning": {
            "title": "🌅 УТРЕННЯЯ МОТИВАЦИЯ",
            "message": """

Доброе утро! ☀️

Каждый день - это новая возможность стать лучше. 
Сегодня ты можешь:

✨ Сделать шаг к своей мечте
💪 Преодолеть то, что вчера казалось невозможным  
🎯 Приблизиться к своим целям
🌟 Подарить миру свой уникальный свет

Начни день с улыбки и веры в себя! 💫
"""
        },
        "evening": {
            "title": "🌙 ВЕЧЕРНИЕ РАЗМЫШЛЕНИЯ", 
            "message": """

Вечер - время подведения итогов 🌆

За сегодняшний день ты:

🎯 Прожил еще один день своей жизни
💫 Получил новый опыт и знания
❤️ Проявил заботу к себе и близким
🌟 Стал немного мудрее

Отдохни, восстанови силы и готовься к новым свершениям! 💤
"""
        },
        "overcome": {
            "title": "💪 ПРЕОДОЛЕНИЕ ТРУДНОСТЕЙ",
            "message": """

Трудности - это ступени к росту 🏔️

Помни:

🔥 Алмаз образуется под давлением
🌱 Сильные корни растут в бурю
⭐ Звезды светят ярче в темноте
💎 Твоя сила проявляется в испытаниях

Каждое препятствие делает тебя сильнее! 💪
"""
        },
        "goals": {
            "title": "🎯 ДОСТИЖЕНИЕ ЦЕЛЕЙ",
            "message": """

Цель без плана - всего лишь мечта 📋

Секреты достижения целей:

🎯 Четко сформулируй что хочешь
📅 Разбей на маленькие шаги  
📈 Отмечай каждый прогресс
🔄 Будь гибким в методах
💫 Верь в свои возможности

Твой успех начинается с первого шага! 🚀
"""
        }
    }
    
    if selection in content_map:
        content = content_map[selection]
        full_text = f"{content['title']}{content['message']}"
        
        # Добавляем кнопки реакций
        from utils.keyboards import get_reaction_keyboard
        import uuid
        post_id = str(uuid.uuid4())[:8]
        
        reaction_keyboard = get_reaction_keyboard(post_id)
        back_button = [[InlineKeyboardButton("⬅️ Назад к мотивации", callback_data='category_motivation')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.answer("❓ Неизвестная опция")

async def handle_esoteric_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе эзотерики"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    query = update.callback_query
    if not query or not query.data:
        return
    
    selection = query.data.replace("esoteric_", "")
    
    if selection == "horoscope":
        # Показываем выбор знака зодиака
        text = """
🔮 **ГОРОСКОП НА ДЕНЬ**

Выберите свой знак зодиака для персонального гороскопа:

✨ Каждый знак получит уникальное предсказание на сегодня
"""
        from utils.keyboards import create_zodiac_keyboard
        await query.edit_message_text(
            text,
            reply_markup=create_zodiac_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await query.answer("🔮 Контент в разработке!")

async def handle_development_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе развития"""
    query = update.callback_query
    if not query:
        return
    await query.answer("🎯 Контент в разработке!")

async def handle_health_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе здоровья"""  
    query = update.callback_query
    if not query:
        return
    await query.answer("🌟 Контент в разработке!")

async def handle_relationships_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе отношений"""
    query = update.callback_query  
    if not query:
        return
    await query.answer("💝 Контент в разработке!")

async def handle_zodiac_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор знака зодиака"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    from config import ZODIAC_MAPPING
    
    query = update.callback_query
    if not query or not query.data:
        return
    
    # Получаем английский ключ из callback_data
    english_key = query.data.replace("zodiac_", "")
    
    # Конвертируем в русское название
    sign = ZODIAC_MAPPING.get(english_key, english_key.title())
    
    horoscope_text = f"""
🔮 **ГОРОСКОП ДЛЯ {sign.upper()}**

Сегодня звезды благосклонны к вам! ✨

💫 **Общая энергетика дня:** Высокая
🎯 **Рекомендации:** Действуйте смело и уверенно
💝 **Отношения:** Время для откровенных разговоров  
💼 **Карьера:** Благоприятный день для новых начинаний
🌟 **Совет дня:** Доверьтесь своей интуиции

Пусть день принесет вам радость и успех! 🌈
"""
    
    # Добавляем кнопки реакций и возврата
    from utils.keyboards import get_reaction_keyboard
    import uuid
    post_id = str(uuid.uuid4())[:8]
    
    reaction_keyboard = get_reaction_keyboard(post_id)
    back_button = [[InlineKeyboardButton("⬅️ Назад к выбору знака", callback_data='esoteric_horoscope')]]
    
    keyboard = reaction_keyboard + back_button
    
    await query.edit_message_text(
        horoscope_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

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
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("admin", handle_admin_command))
    
    # Регистрация обработчика callback-запросов
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Регистрация обработчика текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Регистрация обработчика ошибок
    application.add_error_handler(error_handler)
    
    # Инициализация приложения
    await application.initialize()
    
    # Получение Railway URL для webhook
    # Проверяем несколько вариантов получения webhook URL
    webhook_url = None
    
    # Вариант 1: Переменная WEBHOOK_URL (устанавливается вручную)
    manual_webhook = os.environ.get('WEBHOOK_URL')
    if manual_webhook:
        webhook_url = f"{manual_webhook}/webhook/{BOT_TOKEN}"
        
    # Вариант 2: RAILWAY_PUBLIC_DOMAIN (автоматически от Railway)
    elif os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        webhook_url = f"https://{railway_domain}/webhook/{BOT_TOKEN}"
        
    # Вариант 3: RAILWAY_STATIC_URL (ещё один вариант от Railway)
    elif os.environ.get('RAILWAY_STATIC_URL'):
        railway_static = os.environ.get('RAILWAY_STATIC_URL')
        webhook_url = f"{railway_static}/webhook/{BOT_TOKEN}"
    
    # Вариант 4: Автодетект домена через переменные Railway
    elif os.environ.get('RAILWAY_PROJECT_NAME') and os.environ.get('RAILWAY_SERVICE_NAME'):
        # Формируем URL по шаблону Railway: service-name-project-name.up.railway.app
        project = os.environ.get('RAILWAY_PROJECT_NAME', '').lower()
        service = os.environ.get('RAILWAY_SERVICE_NAME', '').lower()
        if project and service:
            auto_domain = f"{service}-{project}.up.railway.app"
            webhook_url = f"https://{auto_domain}/webhook/{BOT_TOKEN}"
            logger.info(f"🔍 Попытка автодетекта домена: {auto_domain}")
    
    # В Railway всегда используем webhook, даже если нет URL
    is_railway_env = (
        os.environ.get('RAILWAY_PROJECT_ID') is not None or
        os.environ.get('PORT') is not None
    )
    
    if webhook_url:
        await application.bot.set_webhook(webhook_url)
        logger.info(f"🌐 Webhook установлен: {webhook_url}")
    elif is_railway_env:
        # Railway окружение без webhook URL - очищаем старый webhook
        await application.bot.delete_webhook()
        logger.info("⚠️ Webhook очищен - добавьте WEBHOOK_URL переменную для получения сообщений!")
        logger.info("📋 Инструкция: Railway → Settings → Generate Domain → Variables → WEBHOOK_URL=ваш_домен")
    else:
        logger.info("🏠 Локальный режим - polling")
        # Для локального режима возвращаем False чтобы запустить polling отдельно
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
    try:
        # Валидация конфигурации
        validate_config()
        logger.info("✅ Конфигурация успешно загружена")
        
        # Настройка webhook route после загрузки конфигурации
        setup_webhook_route()
        
        # Проверка Railway окружения - используем переменные, которые автоматически создаёт Railway
        is_railway = (
            os.environ.get('RAILWAY_PROJECT_ID') is not None or
            os.environ.get('RAILWAY_SERVICE_ID') is not None or 
            os.environ.get('RAILWAY_DEPLOYMENT_ID') is not None or
            os.environ.get('PORT') is not None  # Railway всегда устанавливает PORT
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
            # Локальный режим с polling - используем простой подход
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
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("admin", handle_admin_command))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_error_handler(error_handler)
    
    logger.info("🔄 Запуск polling режима...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
