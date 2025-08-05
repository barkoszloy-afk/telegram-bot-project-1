# config.py - Конфигурация бота
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ID администратора
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

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
REACTION_EMOJIS = ["❤️", "👍", "👎", "😂", "😢", "😡", "🤔", "🙏"]

# Названия реакций
REACTION_NAMES = ["Сердце", "Лайк", "Дизлайк", "Смех", "Грусть", "Злость", "Думаю", "Молитва"]

def validate_config():
    """Проверка конфигурации"""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    if not ADMIN_ID:
        raise ValueError("ADMIN_ID не найден в переменных окружения")
    
    logger.info("✅ Конфигурация загружена успешно")
    masked_token = BOT_TOKEN if len(BOT_TOKEN) <= 8 else f"{BOT_TOKEN[:4]}...{BOT_TOKEN[-4:]}"
    logger.info(f"🤖 Токен бота: {masked_token}")
    logger.info(f"👤 ID администратора: {ADMIN_ID}")
