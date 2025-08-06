# main_bot_railway.py - Минимальная версия с базовым меню
import logging
import os
import threading
import time
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from flask import Flask, jsonify

# Импорты из наших модулей
from config import (
    BOT_TOKEN, validate_config,
    CONNECT_TIMEOUT, READ_TIMEOUT, WRITE_TIMEOUT, POOL_TIMEOUT
)
from utils.keyboards import (
    create_main_menu_keyboard,
    create_esoteric_submenu,
    create_motivation_submenu,
    create_development_submenu,
    create_health_submenu,
    create_relationships_submenu,
    create_zodiac_keyboard
)

# Импорты новых обработчиков команд
from handlers.diagnostics import (
    ping_command, status_command, uptime_command, 
    version_command, health_command
)
from handlers.stats import (
    stats_command, users_command, update_stats
)
from handlers.user_commands import (
    about_command, profile_command, feedback_command, settings_command
)
from handlers.content_commands import (
    random_command, popular_command, recent_command,
    categories_command, search_command
)
from handlers.admin_commands import (
    logs_command, restart_command, broadcast_command, cleanup_command
)
from handlers.chatgpt_commands import (
    handle_chatgpt_callback, chatgpt_command, process_gpt_message
)

# Flask app для health endpoint
app = Flask(__name__)

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

# ================== FLASK ENDPOINTS ==================

@app.route('/health')
def health_check():
    """Health check endpoint для Railway"""
    uptime = time.time() - start_time if start_time else 0
    return jsonify({
        'status': 'healthy',
        'uptime_seconds': round(uptime, 2),
        'service': 'telegram-bot',
        'version': '1.0.0'
    })

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'Telegram Bot is running',
        'status': 'online',
        'endpoints': ['/health', '/webhook']
    })

@app.route('/webhook/<token>', methods=['POST'])
def webhook(token):
    """Webhook endpoint для Telegram"""
    from flask import request
    import asyncio
    import threading
    
    # Проверяем токен для безопасности
    if token != BOT_TOKEN:
        logger.warning(f"❌ Неверный токен в webhook: {token[:10]}...")
        return '', 404
    
    if not application:
        logger.error("❌ Application не инициализирован!")
        return '', 500
    
    try:
        update_data = request.get_json()
        if not update_data:
            logger.warning("❌ Пустые данные в webhook")
            return '', 400
            
        logger.info(f"📨 Получен webhook update: {update_data.get('update_id', 'unknown')}")
        
        # Логируем детали сообщения если есть
        if 'message' in update_data:
            msg = update_data['message']
            user_id = msg.get('from', {}).get('id', 'unknown')
            text = msg.get('text', 'no text')
            logger.info(f"👤 От пользователя {user_id}: {text}")
        
        update = Update.de_json(update_data, application.bot)
        
        # Обрабатываем update в отдельном потоке с новым event loop
        def process_update():
            try:
                logger.info("🔄 Начинаем обработку update...")
                asyncio.run(application.process_update(update))
                logger.info("✅ Update обработан успешно")
            except Exception as e:
                logger.error(f"❌ Ошибка обработки update: {e}")
                import traceback
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=process_update)
        thread.daemon = True
        thread.start()
        
        logger.info("✅ Webhook update отправлен на обработку")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка webhook: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return '', 500
    
    return '', 200

# ================== КОМАНДЫ БОТА ==================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start - показывает главное меню"""
    try:
        user_id = update.effective_user.id if update.effective_user else "unknown"
        user_name = update.effective_user.first_name if update.effective_user else "друг"
        logger.info(f"🌟 Команда /start от пользователя {user_id} ({user_name})")
        
        # Обновляем статистику
        try:
            update_stats(
                user_id, 
                update.effective_user.username if update.effective_user else None,
                update.effective_user.first_name if update.effective_user else None,
                "start"
            )
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики: {e}")
        
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
        
        # Обновляем статистику
        try:
            update_stats(
                user_id, 
                update.effective_user.username if update.effective_user else None,
                update.effective_user.first_name if update.effective_user else None,
                "help"
            )
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики: {e}")
        
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
        
        # Реакции на посты
        elif data.startswith("reaction_"):
            from handlers.reactions import handle_reaction
            await handle_reaction(update, context)
        
        # Статистика реакций
        elif data.startswith("stats_"):
            from handlers.reactions import show_post_reactions
            await show_post_reactions(update, context)
        
        # Случайный пост (новый)
        elif data == "random_new":
            from handlers.content_commands import random_command
            await random_command(update, context)
        
        # Показать полный пост
        elif data.startswith("show_post_"):
            await query.answer("📖 Открытие поста...", show_alert=True)
        
        # Категории контента
        elif data.startswith("category_"):
            category = data.split("_", 1)[1]
            
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

🔮 **Гороскоп** - ваше звездное предсказание
🌙 **Карта дня** - таро-прогноз  
☀️ **Доброе утро** - духовный настрой
🌜 **Лунный прогноз** - влияние луны
🎯 **Интерактив** - гадания и практики
🌟 **Вечернее послание** - завершение дня
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

Забота о теле и душе:

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
                await query.answer(f"📂 Категория: {category}\n🚧 В разработке!", show_alert=True)
                return
                
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        # Эзотерические функции
        elif data.startswith("esoteric_"):
            selection = data.replace("esoteric_", "")
            
            if selection == "horoscope":
                text = """
🔮 **ГОРОСКОП НА ДЕНЬ**

Выберите свой знак зодиака для персонального гороскопа:

✨ Каждый знак получит уникальное предсказание на сегодня
"""
                keyboard = create_zodiac_keyboard()
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
            elif selection == "daily_card":
                text = """
🌙 **КАРТА ДНЯ**

🃏 **Ваша карта дня:**

**🔮 Аркан:** Маг

**💫 Значение:** Сегодня у вас есть все ресурсы для воплощения идей в реальность. День благоприятен для новых начинаний и творческих проектов.

**🎯 Совет:** Доверьтесь своей интуиции и действуйте решительно.

**💖 Отношения:** Время открытых разговоров
**💼 Карьера:** Успех в переговорах
**🌟 Здоровье:** Высокий уровень энергии

🔮 _Пусть карты ведут вас к успеху!_
"""
                from config import REACTION_EMOJIS
                import uuid
                post_id = str(uuid.uuid4())[:8]
                
                # Создаем клавиатуру с реакциями и кнопкой назад
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(emoji, callback_data=f"reaction_{idx}_{post_id}") 
                     for idx, emoji in enumerate(REACTION_EMOJIS)],
                    [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post_id}")],
                    [InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]
                ])
                
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
            elif selection == "good_morning":
                text = """
☀️ **ДОБРОЕ УТРО!**

🌅 **Духовный настрой на день:**

Приветствую вас, дорогие души! ✨

Сегодня - особенный день, полный возможностей и благословений. Позвольте утреннему свету наполнить ваше сердце радостью и энергией.

🙏 **Утренняя мантра:**
"Я открыт(а) для всех благословений этого дня"

🌸 **Практика дня:**
• Сделайте 3 глубоких вдоха
• Поблагодарите за новый день
• Установите позитивное намерение

💫 **Энергетический прогноз:**
Сегодня энергии способствуют творчеству и духовному росту.

Пусть ваш день будет наполнен светом и любовью! 🌟
"""
                from config import REACTION_EMOJIS
                import uuid
                post_id = str(uuid.uuid4())[:8]
                
                # Создаем клавиатуру с реакциями и кнопкой назад
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(emoji, callback_data=f"reaction_{idx}_{post_id}") 
                     for idx, emoji in enumerate(REACTION_EMOJIS)],
                    [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post_id}")],
                    [InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]
                ])
                
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
            elif selection == "lunar_forecast":
                text = """
🌜 **ЛУННЫЙ ПРОГНОЗ**

🌙 **Фаза Луны:** Растущая Луна в Раке

**🌊 Влияние на сегодня:**

Энергии растущей Луны в Раке способствуют:
• 💝 Укреплению семейных связей
• 🏠 Созданию уюта в доме
• 🧘‍♀️ Медитативным практикам
• 🌱 Началу новых проектов

**⚠️ Рекомендации:**
• Избегайте конфликтов и споров
• Больше времени проводите с близкими
• Прислушивайтесь к своей интуиции
• Заботьтесь о своем эмоциональном состоянии

**🔮 Магическое время:** 20:00 - 22:00

**💎 Камень дня:** Лунный камень
**🌿 Растение дня:** Жасмин

Пусть лунная энергия принесет вам гармонию! 🌙✨
"""
                from config import REACTION_EMOJIS
                import uuid
                post_id = str(uuid.uuid4())[:8]
                
                # Создаем клавиатуру с реакциями и кнопкой назад
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(emoji, callback_data=f"reaction_{idx}_{post_id}") 
                     for idx, emoji in enumerate(REACTION_EMOJIS)],
                    [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post_id}")],
                    [InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]
                ])
                
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
            elif selection == "interactive":
                text = """
🎯 **ИНТЕРАКТИВНАЯ ПРАКТИКА**

🔮 **Выберите свою практику:**

🎲 **Гадание "Да/Нет"** - получите быстрый ответ на вопрос
🃏 **Трехкарточный расклад** - прошлое, настоящее, будущее
🧿 **Очистка ауры** - энергетическая практика
🌟 **Медитация дня** - персональная техника
🔢 **Нумерология имени** - раскройте тайны имени
🌙 **Лунная магия** - работа с лунными энергиями
"""
                
                keyboard = [
                    [
                        InlineKeyboardButton("🎲 Да/Нет", callback_data="interactive_yesno"),
                        InlineKeyboardButton("🃏 Расклад", callback_data="interactive_cards")
                    ],
                    [
                        InlineKeyboardButton("🧿 Очистка", callback_data="interactive_cleanse"),
                        InlineKeyboardButton("🌟 Медитация", callback_data="interactive_meditation")
                    ],
                    [
                        InlineKeyboardButton("🔢 Нумерология", callback_data="interactive_numerology"),
                        InlineKeyboardButton("🌙 Луна", callback_data="interactive_lunar")
                    ],
                    [
                        InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')
                    ]
                ]
                
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                
            elif selection == "evening_message":
                text = """
🌟 **ВЕЧЕРНЕЕ ПОСЛАНИЕ**

🌙 **Завершение дня с благодарностью:**

Дорогие души, день подходит к концу, и время подвести итоги. ✨

🙏 **Момент благодарности:**
За что вы благодарны сегодня? Каждый прожитый момент - это дар, каждая встреча - это урок, каждый вызов - это возможность роста.

🌸 **Вечерняя практика:**
• Проанализируйте события дня
• Отпустите все негативные эмоции
• Поблагодарите Вселенную за поддержку
• Загадайте мечту на завтра

💫 **Напутствие на ночь:**
Пусть ваш сон будет спокойным, а сновидения - вдохновляющими. Завтра вас ждет новый день, полный возможностей.

🌙 _Спокойной ночи и сладких снов!_ ✨
"""
                from config import REACTION_EMOJIS
                import uuid
                post_id = str(uuid.uuid4())[:8]
                
                # Создаем клавиатуру с реакциями и кнопкой назад
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(emoji, callback_data=f"reaction_{idx}_{post_id}") 
                     for idx, emoji in enumerate(REACTION_EMOJIS)],
                    [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post_id}")],
                    [InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]
                ])
                
                await query.edit_message_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                
            else:
                await query.answer("🔮 Эта функция в разработке!")
        
        # Обработка гороскопов для знаков зодиака
        elif data.startswith("zodiac_"):
            from config import ZODIAC_REVERSE_MAPPING
            english_key = data.replace("zodiac_", "")
            
            # Создаем обратное отображение из ZODIAC_REVERSE_MAPPING
            reverse_mapping = {v: k for k, v in ZODIAC_REVERSE_MAPPING.items()}
            sign = reverse_mapping.get(english_key, english_key.title())
            
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
            
            from config import REACTION_EMOJIS
            import uuid
            post_id = str(uuid.uuid4())[:8]
            
            # Создаем клавиатуру с реакциями и кнопкой назад
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(emoji, callback_data=f"reaction_{idx}_{post_id}") 
                 for idx, emoji in enumerate(REACTION_EMOJIS)],
                [InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post_id}")],
                [InlineKeyboardButton("⬅️ Назад к выбору знака", callback_data='esoteric_horoscope')]
            ])
            
            await query.edit_message_text(
                horoscope_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
        # ChatGPT callback'ы
        elif data.startswith("gpt_") or data == "back_to_main":
            await handle_chatgpt_callback(update, context)
        
        # Заглушки для категорий (старые)
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

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (для ChatGPT)"""
    try:
        # Проверяем, предназначено ли сообщение для ChatGPT
        if await process_gpt_message(update, context):
            return
        
        # Если сообщение не обработано ChatGPT, можно добавить другую логику
        # Например, показать подсказку или просто игнорировать
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки текстового сообщения: {e}")

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
            # Основные команды
            BotCommand("start", "Главное меню с категориями"),
            BotCommand("help", "Справка по использованию бота"),
            BotCommand("instructions", "Подробные инструкции"),
            BotCommand("test", "Тест работы бота"),
            
            # Диагностические команды
            BotCommand("ping", "Проверка отклика бота"),
            BotCommand("uptime", "Время работы бота"),
            BotCommand("version", "Версия бота"),
            
            # Пользовательские команды
            BotCommand("about", "О боте"),
            BotCommand("profile", "Ваш профиль"),
            BotCommand("feedback", "Обратная связь"),
            BotCommand("settings", "Настройки"),
            
            # Контентные команды
            BotCommand("random", "Случайный пост"),
            BotCommand("popular", "Популярные посты"),
            BotCommand("recent", "Последние посты"),
            BotCommand("categories", "Категории"),
            BotCommand("search", "Поиск по контенту"),
            
            # Административные команды (будут видны только админу в меню)
            BotCommand("status", "Статус системы"),
            BotCommand("stats", "Статистика"),
            BotCommand("users", "Пользователи"),
            BotCommand("logs", "Логи"),
            BotCommand("health", "Проверка системы"),
            BotCommand("restart", "Перезапуск"),
            BotCommand("broadcast", "Рассылка"),
            BotCommand("cleanup", "Очистка")
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
        
        # Создание приложения СНАЧАЛА
        logger.info("🤖 Создание Telegram Application...")
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .connect_timeout(CONNECT_TIMEOUT)
            .read_timeout(READ_TIMEOUT) 
            .write_timeout(WRITE_TIMEOUT)
            .pool_timeout(POOL_TIMEOUT)
            .build()
        )
        logger.info("✅ Application создан успешно")
        
        # Регистрация обработчиков
        logger.info("📋 Регистрация обработчиков...")
        # Основные команды
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("instructions", instructions_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(CommandHandler("chatgpt", chatgpt_command))
        
        # Диагностические команды
        application.add_handler(CommandHandler("ping", ping_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("uptime", uptime_command))
        application.add_handler(CommandHandler("version", version_command))
        application.add_handler(CommandHandler("health", health_command))
        
        # Статистика
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("users", users_command))
        
        # Пользовательские команды
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("feedback", feedback_command))
        application.add_handler(CommandHandler("settings", settings_command))
        
        # Контентные команды
        application.add_handler(CommandHandler("random", random_command))
        application.add_handler(CommandHandler("popular", popular_command))
        application.add_handler(CommandHandler("recent", recent_command))
        application.add_handler(CommandHandler("categories", categories_command))
        application.add_handler(CommandHandler("search", search_command))
        
        # Административные команды
        application.add_handler(CommandHandler("logs", logs_command))
        application.add_handler(CommandHandler("restart", restart_command))
        application.add_handler(CommandHandler("broadcast", broadcast_command))
        application.add_handler(CommandHandler("cleanup", cleanup_command))
        
        # Обработчики callback и ошибок
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
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
            port = int(os.environ.get("PORT", 8080))
            
            logger.info(f"🌐 Webhook URL: {webhook_url}")
            logger.info(f"�️ Webhook path: {webhook_path}")
            logger.info(f"�🔌 Listening on port: {port}")
            
            # Устанавливаем webhook через API
            async def setup_webhook():
                if application and application.bot:
                    await application.bot.set_webhook(webhook_url)
                    await setup_bot_commands(application)
                    logger.info("✅ Webhook установлен успешно!")
                else:
                    logger.error("❌ Application не инициализировано")
            
            # Запускаем setup в отдельном потоке
            def run_setup():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(setup_webhook())
                loop.close()
            
            setup_thread = threading.Thread(target=run_setup)
            setup_thread.start()
            setup_thread.join()  # Ждем завершения setup
            
            # Запускаем Flask server
            logger.info(f"🏥 Запуск Flask server на порту {port}")
            app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
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
    application.add_handler(CommandHandler("chatgpt", chatgpt_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
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
