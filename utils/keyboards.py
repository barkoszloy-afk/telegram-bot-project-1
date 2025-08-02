# utils/keyboards.py - Утилиты для создания клавиатур
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from config import ZODIAC_SIGNS, REACTION_EMOJIS, REACTION_NAMES, ZODIAC_REVERSE_MAPPING
from .database import reactions_db

def get_zodiac_keyboard():
    """ЗНАКИ ЗОДИАКА: Красивая сетка 3x4 + навигация"""
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
    
    # Добавляем кнопку "Назад" отдельным рядом
    keyboard.append([
        InlineKeyboardButton("⬅️ Назад к эзотерике", callback_data='category_esoteric')
    ])
    
    return keyboard

def get_reaction_keyboard(post_id: str):
    """РЕАКЦИИ: Красивое расположение в 2 ряда"""
    data = reactions_db.data
    post_reactions = data.get('posts', {}).get(post_id, {})
    
    keyboard = []
    
    # Первый ряд: ❤️ и 👍
    row1 = []
    for i, (emoji, reaction_name) in enumerate(zip(REACTION_EMOJIS[:2], REACTION_NAMES[:2])):
        count = post_reactions.get(reaction_name, 0)
        button_text = f"{emoji} {count}" if count > 0 else emoji
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"react_{reaction_name}_{post_id}"
        )
        row1.append(button)
    keyboard.append(row1)
    
    # Второй ряд: 🔥 и 💫
    row2 = []
    for i, (emoji, reaction_name) in enumerate(zip(REACTION_EMOJIS[2:], REACTION_NAMES[2:]), 2):
        count = post_reactions.get(reaction_name, 0)
        button_text = f"{emoji} {count}" if count > 0 else emoji
        button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"react_{reaction_name}_{post_id}"
        )
        row2.append(button)
    keyboard.append(row2)
    
    return keyboard

def get_morning_variants_keyboard():
    """Создает клавиатуру для утренних вариантов"""
    keyboard = [
        [InlineKeyboardButton("🌅 Заряд энергии", callback_data='morning_variant1')],
        [InlineKeyboardButton("🌞 Путь к победам", callback_data='morning_variant2')],
        [InlineKeyboardButton("⭐ Звездный путь", callback_data='morning_variant3')]
    ]
    return keyboard

def create_admin_post_keyboard(post_id: str, keyboard_type: str = 'zodiac'):
    """Создает клавиатуру для админских постов"""
    keyboard = []
    
    if keyboard_type == 'morning':
        # Утренний пост - добавляем варианты утра
        keyboard.extend(get_morning_variants_keyboard())
    else:
        # Обычный пост - добавляем зодиак
        keyboard.extend(get_zodiac_keyboard())
    
    # Добавляем реакции
    keyboard.extend(get_reaction_keyboard(post_id))
    
    return InlineKeyboardMarkup(keyboard)

def create_post_keyboard(post_id: str, has_morning_variants: bool = False):
    """Создает клавиатуру для обычных постов"""
    keyboard = []
    
    if has_morning_variants:
        keyboard.extend(get_morning_variants_keyboard())
    else:
        keyboard.extend(get_zodiac_keyboard())
    
    keyboard.extend(get_reaction_keyboard(post_id))
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu_keyboard():
    """Создает клавиатуру для главного меню админ-панели"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("🌅 Утренний пост", callback_data='admin_morning')],
        [InlineKeyboardButton("🔮 Гороскоп", callback_data='admin_horoscope')],
        [InlineKeyboardButton("🌙 Вечерний пост", callback_data='admin_evening')],
        [InlineKeyboardButton("🔄 Очистить старые данные", callback_data='admin_cleanup')]
    ]
    return keyboard

def get_admin_preview_keyboard(post_type: str, post_id: str = ""):
    """Создает клавиатуру для предварительного просмотра постов"""
    if post_type == "morning":
        keyboard = [
            [InlineKeyboardButton("📤 Опубликовать", callback_data=f'publish_morning_{post_id}')],
            [InlineKeyboardButton("❌ Отменить", callback_data=f'cancel_morning_{post_id}')]
        ]
    elif post_type == "horoscope":
        keyboard = [
            [InlineKeyboardButton("📤 Опубликовать", callback_data=f'publish_horoscope_{post_id}')],
            [InlineKeyboardButton("🔄 Другой гороскоп", callback_data='admin_horoscope')],
            [InlineKeyboardButton("❌ Отменить", callback_data=f'cancel_horoscope_{post_id}')]
        ]
    elif post_type == "evening":
        keyboard = [
            [InlineKeyboardButton("📤 Опубликовать", callback_data=f'publish_evening_{post_id}')],
            [InlineKeyboardButton("🔄 Другое сообщение", callback_data='admin_evening')],
            [InlineKeyboardButton("❌ Отменить", callback_data=f'cancel_evening_{post_id}')]
        ]
    else:
        # Универсальная клавиатура
        keyboard = [
            [InlineKeyboardButton("📤 Опубликовать", callback_data=f'publish_{post_type}_{post_id}')],
            [InlineKeyboardButton("❌ Отменить", callback_data=f'cancel_{post_type}_{post_id}')]
        ]
    
    return keyboard

def create_admin_menu_keyboard():
    """Создает InlineKeyboardMarkup для админ-панели"""
    return InlineKeyboardMarkup(get_admin_menu_keyboard())

def create_admin_preview_keyboard(post_type: str, post_id: str = ""):
    """Создает InlineKeyboardMarkup для предварительного просмотра"""
    return InlineKeyboardMarkup(get_admin_preview_keyboard(post_type, post_id))

# ============= НОВАЯ СТРУКТУРИРОВАННАЯ СИСТЕМА =============

def get_main_menu_keyboard():
    """ГЛАВНОЕ МЕНЮ: Основные категории контента с красивым расположением"""
    keyboard = [
        # Ряд 1: Мотивация и Эзотерика
        [
            InlineKeyboardButton("💫 Мотивация", callback_data='category_motivation'),
            InlineKeyboardButton("🔮 Эзотерика", callback_data='category_esoteric')
        ],
        # Ряд 2: Развитие и Здоровье  
        [
            InlineKeyboardButton("🎯 Развитие", callback_data='category_development'),
            InlineKeyboardButton("🌟 Здоровье", callback_data='category_health')
        ],
        # Ряд 3: Отношения (по центру)
        [
            InlineKeyboardButton("💝 Отношения", callback_data='category_relationships')
        ]
    ]
    return keyboard

def get_motivation_submenu():
    """МОТИВАЦИЯ: Подкатегории с удобным расположением"""
    keyboard = [
        # Ряд 1: Утро и Вечер
        [
            InlineKeyboardButton("🌅 Утренняя мотивация", callback_data='motivation_morning'),
            InlineKeyboardButton("🌙 Вечерние размышления", callback_data='motivation_evening')
        ],
        # Ряд 2: Трудности и Цели
        [
            InlineKeyboardButton("💪 Преодоление трудностей", callback_data='motivation_overcome'),
            InlineKeyboardButton("🎯 Достижение целей", callback_data='motivation_goals')
        ],
        # Ряд 3: Назад
        [
            InlineKeyboardButton("⬅️ Назад в главное меню", callback_data='main_menu')
        ]
    ]
    return keyboard

def get_esoteric_submenu():
    """ЭЗОТЕРИКА: Подкатегории с красивым расположением"""
    keyboard = [
        # Ряд 1: Гороскоп и Луна
        [
            InlineKeyboardButton("🔮 Гороскоп на день", callback_data='esoteric_horoscope'),
            InlineKeyboardButton("🌙 Лунный календарь", callback_data='esoteric_moon')
        ],
        # Ряд 2: Нумерология и Таро
        [
            InlineKeyboardButton("🔢 Нумерология", callback_data='esoteric_numerology'),
            InlineKeyboardButton("🃏 Карты Таро", callback_data='esoteric_tarot')
        ],
        # Ряд 3: Назад
        [
            InlineKeyboardButton("⬅️ Назад в главное меню", callback_data='main_menu')
        ]
    ]
    return keyboard

def get_development_submenu():
    """РАЗВИТИЕ: Подкатегории с интуитивным расположением"""
    keyboard = [
        # Ряд 1: Мышление и Обучение
        [
            InlineKeyboardButton("🧠 Развитие мышления", callback_data='development_thinking'),
            InlineKeyboardButton("📚 Обучение и знания", callback_data='development_learning')
        ],
        # Ряд 2: Творчество и Карьера
        [
            InlineKeyboardButton("🎨 Творческое развитие", callback_data='development_creativity'),
            InlineKeyboardButton("💼 Карьера и бизнес", callback_data='development_career')
        ],
        # Ряд 3: Назад
        [
            InlineKeyboardButton("⬅️ Назад в главное меню", callback_data='main_menu')
        ]
    ]
    return keyboard

def get_health_submenu():
    """ЗДОРОВЬЕ: Подкатегории с логичным расположением"""
    keyboard = [
        # Ряд 1: Физическое и Ментальное
        [
            InlineKeyboardButton("🏃‍♂️ Физическая активность", callback_data='health_fitness'),
            InlineKeyboardButton("🧘‍♀️ Ментальное здоровье", callback_data='health_mental')
        ],
        # Ряд 2: Питание и Сон
        [
            InlineKeyboardButton("🥗 Питание и диета", callback_data='health_nutrition'),
            InlineKeyboardButton("😴 Сон и отдых", callback_data='health_sleep')
        ],
        # Ряд 3: Назад
        [
            InlineKeyboardButton("⬅️ Назад в главное меню", callback_data='main_menu')
        ]
    ]
    return keyboard

def get_relationships_submenu():
    """ОТНОШЕНИЯ: Подкатегории с понятным расположением"""
    keyboard = [
        # Ряд 1: Любовь и Семья
        [
            InlineKeyboardButton("💕 Любовь и романтика", callback_data='relationships_love'),
            InlineKeyboardButton("👨‍👩‍👧‍👦 Семья и дети", callback_data='relationships_family')
        ],
        # Ряд 2: Дружба и Работа
        [
            InlineKeyboardButton("👥 Дружба и общение", callback_data='relationships_friendship'),
            InlineKeyboardButton("🤝 Рабочие отношения", callback_data='relationships_work')
        ],
        # Ряд 3: Назад
        [
            InlineKeyboardButton("⬅️ Назад в главное меню", callback_data='main_menu')
        ]
    ]
    return keyboard

# ============= WRAPPER ФУНКЦИИ =============

def create_main_menu_keyboard():
    """Создает InlineKeyboardMarkup для главного меню"""
    return InlineKeyboardMarkup(get_main_menu_keyboard())

def create_motivation_submenu():
    """Создает InlineKeyboardMarkup для подменю мотивации"""
    return InlineKeyboardMarkup(get_motivation_submenu())

def create_esoteric_submenu():
    """Создает InlineKeyboardMarkup для подменю эзотерики"""
    return InlineKeyboardMarkup(get_esoteric_submenu())

def create_development_submenu():
    """Создает InlineKeyboardMarkup для подменю развития"""
    return InlineKeyboardMarkup(get_development_submenu())

def create_health_submenu():
    """Создает InlineKeyboardMarkup для подменю здоровья"""
    return InlineKeyboardMarkup(get_health_submenu())

def create_relationships_submenu():
    """Создает InlineKeyboardMarkup для подменю отношений"""
    return InlineKeyboardMarkup(get_relationships_submenu())

def create_zodiac_keyboard():
    """Создает InlineKeyboardMarkup для выбора знака зодиака"""
    return InlineKeyboardMarkup(get_zodiac_keyboard())

def remove_reply_keyboard():
    """Создает ReplyKeyboardRemove для удаления постоянной клавиатуры"""
    return ReplyKeyboardRemove(selective=True)
