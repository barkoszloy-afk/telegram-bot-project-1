# utils/keyboards.py - Утилиты для создания клавиатур
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import REACTION_EMOJIS

def create_main_menu_keyboard():
    """Создает главное меню с категориями"""
    keyboard = [
        [
            InlineKeyboardButton("💫 Мотивация", callback_data="category_motivation"),
            InlineKeyboardButton("🔮 Эзотерика", callback_data="category_esoteric")
        ],
        [
            InlineKeyboardButton("🎯 Развитие", callback_data="category_development"),
            InlineKeyboardButton("🌟 Здоровье", callback_data="category_health")
        ],
        [
            InlineKeyboardButton("💝 Отношения", callback_data="category_relationships")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_submenu_keyboard(category: str):
    """Создает подменю для выбранной категории"""
    keyboard = [
        [
            InlineKeyboardButton("📝 Получить пост", callback_data=f"get_post_{category}"),
            InlineKeyboardButton("🔔 Подписаться", callback_data=f"subscribe_{category}")
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_reaction_keyboard(post_id: str):
    """
    Создает клавиатуру с кнопками-реакциями для поста.
    Возвращает InlineKeyboardMarkup.
    """
    buttons = []
    # Создаем один ряд с эмодзи
    row = [
        InlineKeyboardButton(
            text=emoji,
            callback_data=f"reaction_{idx}_{post_id}"
        ) for idx, emoji in enumerate(REACTION_EMOJIS)
    ]
    buttons.append(row)
    
    # Добавляем кнопку для просмотра статистики
    buttons.append([
        InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post_id}")
    ])
    
    return InlineKeyboardMarkup(buttons)

def create_back_to_menu_keyboard():
    """Создает кнопку 'Назад в меню'"""
    keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

def create_esoteric_submenu():
    """Создает подменю для эзотерики с новыми кнопками"""
    keyboard = [
        [
            InlineKeyboardButton("🔮 Гороскоп", callback_data="esoteric_horoscope"),
            InlineKeyboardButton("🌙 Карта дня", callback_data="esoteric_daily_card")
        ],
        [
            InlineKeyboardButton("☀️ Доброе утро", callback_data="esoteric_good_morning"),
            InlineKeyboardButton("🌜 Лунный прогноз", callback_data="esoteric_lunar_forecast")
        ],
        [
            InlineKeyboardButton("🎯 Интерактив", callback_data="esoteric_interactive"),
            InlineKeyboardButton("🌟 Вечернее послание", callback_data="esoteric_evening_message")
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_motivation_submenu():
    """Создает подменю для мотивации"""
    keyboard = [
        [
            InlineKeyboardButton("🌅 Утренняя мотивация", callback_data="motivation_morning"),
            InlineKeyboardButton("🌙 Вечерние размышления", callback_data="motivation_evening")
        ],
        [
            InlineKeyboardButton("💪 Преодоление трудностей", callback_data="motivation_overcome"),
            InlineKeyboardButton("🎯 Достижение целей", callback_data="motivation_goals")
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_development_submenu():
    """Создает подменю для развития"""
    keyboard = [
        [
            InlineKeyboardButton("🧠 Развитие мышления", callback_data="development_thinking"),
            InlineKeyboardButton("📚 Обучение и знания", callback_data="development_learning")
        ],
        [
            InlineKeyboardButton("🎨 Творческое развитие", callback_data="development_creative"),
            InlineKeyboardButton("💼 Карьера и бизнес", callback_data="development_career")
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_health_submenu():
    """Создает подменю для здоровья"""
    keyboard = [
        [
            InlineKeyboardButton("🏃‍♂️ Физическая активность", callback_data="health_physical"),
            InlineKeyboardButton("🧘‍♀️ Ментальное здоровье", callback_data="health_mental")
        ],
        [
            InlineKeyboardButton("🥗 Питание и диета", callback_data="health_nutrition"),
            InlineKeyboardButton("😴 Сон и отдых", callback_data="health_sleep")
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_relationships_submenu():
    """Создает подменю для отношений"""
    keyboard = [
        [
            InlineKeyboardButton("💕 Любовь и романтика", callback_data="relationships_love"),
            InlineKeyboardButton("👨‍👩‍👧‍👦 Семья и дети", callback_data="relationships_family")
        ],
        [
            InlineKeyboardButton("👥 Дружба и общение", callback_data="relationships_friendship"),
            InlineKeyboardButton("🤝 Рабочие отношения", callback_data="relationships_work")
        ],
        [
            InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_zodiac_keyboard():
    """Создает клавиатуру знаков зодиака"""
    from config import ZODIAC_SIGNS, ZODIAC_REVERSE_MAPPING
    
    keyboard = []
    
    # Создаем сетку знаков зодиака 3x4
    for i in range(0, len(ZODIAC_SIGNS), 3):
        row = []
        for j in range(i, min(i + 3, len(ZODIAC_SIGNS))):
            sign_name, sign_emoji = ZODIAC_SIGNS[j]
            # Используем английские ключи для callback_data
            english_key = ZODIAC_REVERSE_MAPPING.get(sign_name, sign_name.lower())
            button = InlineKeyboardButton(
                text=f"{sign_emoji} {sign_name}",
                callback_data=f"zodiac_{english_key}"
            )
            row.append(button)
        keyboard.append(row)
    
    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)
