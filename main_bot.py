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
from utils.keyboards import create_main_menu_keyboard
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
    """Команда /start - показывает главное меню"""
    if not update.message:
        return
        
    user_name = update.effective_user.first_name if update.effective_user else "друг"
    welcome_text = f"""
🌟 Привет, {user_name}!

Добро пожаловать в мир саморазвития и вдохновения! ✨

🎯 **Выберите интересующую вас тему:**

� **Мотивация** - вдохновляющие идеи на каждый день
🔮 **Эзотерика** - гороскопы, астрология и духовность  
� **Развитие** - личностный рост и обучение
� **Здоровье** - забота о теле и разуме
💝 **Отношения** - гармония в общении и любви

👇 Нажмите на кнопку ниже, чтобы начать:
"""
    
    # Отправляем приветствие с главным меню
    await update.message.reply_text(
        welcome_text, 
        reply_markup=create_main_menu_keyboard()
    )

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
    
    elif selection == "moon":
        content = {
            "title": "🌙 ЛУННЫЙ КАЛЕНДАРЬ",
            "message": """

Луна влияет на наши эмоции, энергию и жизненные циклы! 🌕

🌙 **Фазы Луны и их влияние:**

🌑 **Новолуние** - время новых начинаний и планов
🌓 **Растущая Луна** - активность, развитие проектов
🌕 **Полнолуние** - пик энергии, завершение дел
🌗 **Убывающая Луна** - отпускание, очищение, отдых

✨ **Сегодняшний совет:** Следи за лунными циклами и планируй дела в гармонии с ними!

Пусть Луна станет твоим помощником! 🌙
"""
        }
        
        full_text = f"{content['title']}{content['message']}"
        
        from utils.keyboards import get_reaction_keyboard
        import uuid
        post_id = str(uuid.uuid4())[:8]
        
        reaction_keyboard = get_reaction_keyboard(post_id)
        back_button = [[InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif selection == "numerology":
        content = {
            "title": "🔢 НУМЕРОЛОГИЯ",
            "message": """

Числа несут в себе тайную мудрость и энергию! ✨

🔢 **Значение чисел в жизни:**

1️⃣ **Единица** - лидерство, новые начинания
2️⃣ **Двойка** - партнерство, сотрудничество
3️⃣ **Тройка** - творчество, самовыражение
7️⃣ **Семерка** - духовность, мудрость
8️⃣ **Восьмерка** - материальный успех, власть
9️⃣ **Девятка** - завершение, служение людям

💫 **Практика:** Обращай внимание на повторяющиеся числа - это знаки Вселенной!

Открой язык чисел! 🔮
"""
        }
        
        full_text = f"{content['title']}{content['message']}"
        
        from utils.keyboards import get_reaction_keyboard
        import uuid
        post_id = str(uuid.uuid4())[:8]
        
        reaction_keyboard = get_reaction_keyboard(post_id)
        back_button = [[InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif selection == "tarot":
        content = {
            "title": "🃏 КАРТЫ ТАРО",
            "message": """

Таро - древний инструмент познания себя и своего пути! 🔮

🃏 **Мудрость Таро:**

🌟 **Старшие Арканы** - важные жизненные уроки
⚔️ **Мечи** - мысли, решения, конфликты  
🏆 **Жезлы** - энергия, творчество, страсть
💧 **Кубки** - эмоции, любовь, отношения
💰 **Пентакли** - материальный мир, здоровье

✨ **Совет дня:** Доверься своей интуиции - она знает ответы на твои вопросы!

Позволь картам открыть тебе путь! 🌙
"""
        }
        
        full_text = f"{content['title']}{content['message']}"
        
        from utils.keyboards import get_reaction_keyboard
        import uuid
        post_id = str(uuid.uuid4())[:8]
        
        reaction_keyboard = get_reaction_keyboard(post_id)
        back_button = [[InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    else:
        await query.answer("🔮 Неизвестная опция!")

async def handle_development_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе развития"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    query = update.callback_query
    if not query or not query.data:
        return
    
    selection = query.data.replace("development_", "")
    
    content_map = {
        "thinking": {
            "title": "🧠 РАЗВИТИЕ МЫШЛЕНИЯ",
            "message": """

Твой мозг - это мышца, которую нужно тренировать! 💪

🎯 **Упражнения для ума:**

🧩 Решай головоломки и логические задачи
📚 Читай книги разных жанров
🎲 Играй в интеллектуальные игры
🤔 Задавай себе вопросы "Почему?" и "Как?"

💡 **Совет дня:** Изучи что-то новое сегодня - даже 15 минут имеют значение!

Развивай свой интеллект каждый день! 🌟
"""
        },
        "learning": {
            "title": "📚 ОБУЧЕНИЕ И ЗНАНИЯ",
            "message": """

Знания - это сила, которую никто не сможет отнять! 🎓

📖 **Способы обучения:**

🎥 Смотри образовательные видео
📱 Используй приложения для изучения языков
👥 Общайся с экспертами в интересных тебе областях
✍️ Веди дневник новых знаний

🌟 **Помни:** Каждый день без обучения - потерянный день!

Инвестируй в свое образование! 💎
"""
        },
        "creativity": {
            "title": "� ТВОРЧЕСКОЕ РАЗВИТИЕ",
            "message": """

Творчество - это способность видеть мир по-новому! ✨

🎭 **Развиваем креативность:**

🖌️ Рисуй, лепи, создавай своими руками
📝 Пиши стихи, рассказы, ведите блог
🎵 Слушай новую музыку, играй на инструментах
🌈 Экспериментируй с цветами и формами

💫 **Секрет:** Не бойся ошибок - они часть творческого процесса!

Раскрой свой творческий потенциал! 🦋
"""
        },
        "career": {
            "title": "💼 КАРЬЕРА И БИЗНЕС",
            "message": """

Успех в карьере начинается с правильного мышления! 🚀

💼 **Ключи к успеху:**

🎯 Ставь четкие профессиональные цели
📈 Развивай навыки, востребованные на рынке
🤝 Строй полезные связи и нетворкинг
📊 Анализируй свои достижения и ошибки

💡 **Правило:** Твоя зарплата = ценность, которую ты приносишь!

Строй карьеру мечты! 👑
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
        back_button = [[InlineKeyboardButton("⬅️ Назад к развитию", callback_data='category_development')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.answer("❓ Неизвестная опция")

async def handle_health_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе здоровья"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    query = update.callback_query
    if not query or not query.data:
        return
    
    selection = query.data.replace("health_", "")
    
    content_map = {
        "fitness": {
            "title": "🏃‍♂️ ФИЗИЧЕСКАЯ АКТИВНОСТЬ",
            "message": """

Движение - это жизнь! Твое тело благодарит тебя за каждый шаг! 💪

🏋️ **Простые упражнения:**

🚶‍♀️ Ходи пешком минимум 10 000 шагов в день
💃 Танцуй под любимую музыку 15 минут
🧘‍♀️ Делай утреннюю зарядку или йогу
🏊‍♀️ Плавай или занимайся любимым спортом

⚡ **Энергия:** Физическая активность дает больше энергии, чем отнимает!

Позаботься о своем теле сегодня! 🌟
"""
        },
        "mental": {
            "title": "🧘‍♀️ МЕНТАЛЬНОЕ ЗДОРОВЬЕ",
            "message": """

Твое душевное равновесие - основа счастливой жизни! 🕊️

🧠 **Техники для ментального здоровья:**

🧘 Медитируй 10-15 минут в день
📝 Веди дневник благодарности
🌸 Проводи время на природе
💚 Окружай себя позитивными людьми

💡 **Помни:** Просить помощи - это признак силы, а не слабости!

Береги свою душу! ✨
"""
        },
        "nutrition": {
            "title": "🥗 ПИТАНИЕ И ДИЕТА",
            "message": """

Ты - то, что ты ешь! Питание влияет на твое самочувствие и энергию! 🌱

🍎 **Принципы здорового питания:**

💧 Пей достаточно воды (1.5-2 литра в день)
🥬 Ешь больше овощей и фруктов
🍚 Выбирай цельнозерновые продукты
🐟 Включай белок в каждый прием пищи

🌟 **Секрет:** Маленькие изменения дают большие результаты!

Наполни тело энергией! 🔋
"""
        },
        "sleep": {
            "title": "😴 СОН И ОТДЫХ",
            "message": """

Качественный сон - основа продуктивности и здоровья! 💤

🌙 **Секреты здорового сна:**

⏰ Ложись спать в одно и то же время
📱 Не используй гаджеты за час до сна
🌡️ Спи в прохладной и темной комнате
📖 Читай перед сном или слушай спокойную музыку

✨ **Факт:** Во время сна мозг "убирается" и восстанавливается!

Подари себе качественный отдых! 🌟
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
        back_button = [[InlineKeyboardButton("⬅️ Назад к здоровью", callback_data='category_health')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.answer("❓ Неизвестная опция")

async def handle_relationships_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор в разделе отношений"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    query = update.callback_query
    if not query or not query.data:
        return
    
    selection = query.data.replace("relationships_", "")
    
    content_map = {
        "love": {
            "title": "💕 ЛЮБОВЬ И РОМАНТИКА",
            "message": """

Любовь - это не только чувство, но и ежедневный выбор! 💝

💞 **Секреты крепких отношений:**

💬 Общайтесь открыто и честно
🎁 Делайте маленькие приятности друг другу
👂 Слушайте партнера без осуждения
🌹 Не забывайте про романтику в будни

✨ **Правда:** Лучшие отношения строятся на дружбе и взаимном уважении!

Цени любовь в своей жизни! 💖
"""
        },
        "family": {
            "title": "👨‍👩‍👧‍👦 СЕМЬЯ И ДЕТИ",
            "message": """

Семья - это твоя крепость и источник силы! 🏠

👨‍👩‍👧‍👦 **Гармония в семье:**

🕰️ Проводите качественное время вместе
📞 Поддерживайте связь с родными
🎯 Создавайте семейные традиции и ритуалы
💕 Выражайте любовь словами и поступками

🌟 **Мудрость:** Дети учатся больше от того, что видят, чем от того, что слышат!

Береги семейные узы! 👨‍👩‍👧‍👦
"""
        },
        "friendship": {
            "title": "👥 ДРУЖБА И ОБЩЕНИЕ",
            "message": """

Настоящие друзья - это сокровище, которое нужно ценить! �

🤝 **Крепкая дружба:**

🎉 Радуйтесь успехам друзей искренне
🤗 Поддерживайте в трудные моменты
🎭 Будьте собой в общении
📅 Не забывайте поддерживать связь

💡 **Секрет:** Чтобы иметь друга, нужно самому быть другом!

Цени дружбу! 🌟
"""
        },
        "work": {
            "title": "🤝 РАБОЧИЕ ОТНОШЕНИЯ",
            "message": """

Хорошие отношения на работе делают карьеру успешнее! 💼

👔 **Профессиональное общение:**

🎯 Будь надежным и выполняй обещания
💬 Общайся вежливо и конструктивно
🤝 Помогай коллегам, когда это возможно
📈 Делись знаниями и опытом

🏆 **Принцип:** Успех команды = твой личный успех!

Строй профессиональные связи! 🚀
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
        back_button = [[InlineKeyboardButton("⬅️ Назад к отношениям", callback_data='category_relationships')]]
        
        keyboard = reaction_keyboard + back_button
        
        await query.edit_message_text(
            full_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await query.answer("❓ Неизвестная опция")

async def handle_zodiac_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор знака зодиака"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    query = update.callback_query
    if not query or not query.data:
        return
    
    sign = query.data.replace("zodiac_", "").title()
    
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
