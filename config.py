# config.py - Конфигурация бота
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Идентификатор канала для публикаций
CHANNEL_ID = os.getenv('CHANNEL_ID', '')

# Настройки таймаутов для Railway
CONNECT_TIMEOUT = 30
READ_TIMEOUT = 30
WRITE_TIMEOUT = 30
POOL_TIMEOUT = 30

# Знаки зодиака с эмодзи
ZODIAC_SIGNS = [
    ("Овен", "♈"), ("Телец", "♉"), ("Близнецы", "♊"), ("Рак", "♋"),
    ("Лев", "♌"), ("Дева", "♍"), ("Весы", "♎"), ("Скорпион", "♏"),
    ("Стрелец", "♐"), ("Козерог", "♑"), ("Водолей", "♒"), ("Рыбы", "♓")
]

# Обратное отображение для знаков зодиака
ZODIAC_REVERSE_MAPPING = {
    "Овен": "aries", "Телец": "taurus", "Близнецы": "gemini", "Рак": "cancer",
    "Лев": "leo", "Дева": "virgo", "Весы": "libra", "Скорпион": "scorpio",
    "Стрелец": "sagittarius", "Козерог": "capricorn", "Водолей": "aquarius", "Рыбы": "pisces"
}
# Эмодзи для реакций
REACTION_EMOJIS = ['❤️', '👍', '👎', '😂', '😢', '😡', '🤔', '🙏']

# Названия реакций
REACTION_NAMES = ['Сердце', 'Лайк', 'Дизлайк', 'Смех', 'Грусть', 'Злость', 'Думаю', 'Молитва']

# Сообщения благодарности за реакции (ключ — название реакции)
REACTION_MESSAGES = {
    'Сердце': 'Спасибо за сердечко!',
    'Лайк': 'Спасибо за поддержку!',
    'Дизлайк': 'Мы постараемся стать лучше!',
    'Смех': 'Рады, что вам весело!',
    'Грусть': 'Надеемся, следующий пост поднимет настроение.',
    'Злость': 'Мы учтём вашу обратную связь.',
    'Думаю': 'Интересно ваше мнение!',
    'Молитва': 'Благодарим за поддержку!',
}

# Список запрещённых слов для фильтрации сообщений
FORBIDDEN_WORDS = [w for w in os.getenv('FORBIDDEN_WORDS', 'badword1,badword2,spam').split(',') if w]

logger = logging.getLogger(__name__)


def validate_config():
    """Проверка конфигурации"""
    if not BOT_TOKEN:
        raise ValueError('BOT_TOKEN не найден в переменных окружения')

    if not ADMIN_ID:
        raise ValueError('ADMIN_ID не найден в переменных окружения')

    if not CHANNEL_ID:
        raise ValueError('CHANNEL_ID не найден в переменных окружения')

    if not REACTION_EMOJIS or not REACTION_NAMES:
        raise ValueError('REACTION_EMOJIS и REACTION_NAMES не должны быть пустыми')
    if len(REACTION_EMOJIS) != len(REACTION_NAMES):
        raise ValueError('REACTION_EMOJIS и REACTION_NAMES должны быть одинаковой длины')
    if set(REACTION_NAMES) != set(REACTION_MESSAGES.keys()):
        raise ValueError('REACTION_MESSAGES должны соответствовать REACTION_NAMES')

    masked = f'{BOT_TOKEN[:4]}...{BOT_TOKEN[-4:]}' if BOT_TOKEN else 'N/A'
    logger.info('✅ Конфигурация загружена успешно')
    logger.info('🤖 Токен бота: %s', masked)
    logger.info('👤 ID администратора: %s', ADMIN_ID)
    logger.info('📢 ID канала: %s', CHANNEL_ID)
