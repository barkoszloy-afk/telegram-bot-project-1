# config.py - Конфигурация бота
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Основные настройки
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 345470935))
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1002510932658')
TEST_CHANNEL_ID = os.getenv('TEST_CHANNEL_ID', CHANNEL_ID)  # Для тестирования

# Настройки базы данных и файлов
REACTIONS_FILE = 'reactions_data.json'
LOG_FILE = 'bot.log'
IMAGES_PATH = os.path.expanduser("~/Desktop/images")

# Настройки кеширования
CACHE_TTL = 300  # 5 минут
CACHE_MAX_SIZE = 1000
CACHE_CLEANUP_INTERVAL = 300  # 5 минут

# Настройки таймаутов для Railway
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 20
WRITE_TIMEOUT = 10
POOL_TIMEOUT = 30
CONCURRENT_UPDATES = 256

# Реакции
REACTION_EMOJIS = ["❤️", "�", "🔥", "👍", "�", "💯"]
REACTION_NAMES = ["love", "smile", "fire", "like", "think", "hundred"]
REACTION_MESSAGES = [
    "Спасибо за сердечко!",
    "Спасибо за улыбку!", 
    "Спасибо за огонь!",
    "Спасибо за лайк!",
    "Спасибо за размышления!",
    "Спасибо за 100!"
]

# Знаки зодиака
ZODIAC_SIGNS = [
    ("Овен", "🐏"), ("Телец", "🐂"), ("Близнецы", "👯‍♂️"), ("Рак", "🦀"),
    ("Лев", "🦁"), ("Дева", "👸"), ("Весы", "⚖️"), ("Скорпион", "🦂"),
    ("Стрелец", "🏹"), ("Козерог", "🐐"), ("Водолей", "🌊"), ("Рыбы", "🐟")
]

# Маппинг знаков зодиака (кириллица -> латиница)
ZODIAC_MAPPING = {
    "aries": "Овен", "taurus": "Телец", "gemini": "Близнецы", "cancer": "Рак",
    "leo": "Лев", "virgo": "Дева", "libra": "Весы", "scorpio": "Скорпион", 
    "sagittarius": "Стрелец", "capricorn": "Козерог", "aquarius": "Водолей", "pisces": "Рыбы"
}

# Обратный маппинг (кириллица -> латиница)
ZODIAC_REVERSE_MAPPING = {
    "Овен": "aries", "Телец": "taurus", "Близнецы": "gemini", "Рак": "cancer",
    "Лев": "leo", "Дева": "virgo", "Весы": "libra", "Скорпион": "scorpio",
    "Стрелец": "sagittarius", "Козерог": "capricorn", "Водолей": "aquarius", "Рыбы": "pisces"
}

# Фильтр запрещённых слов
FORBIDDEN_WORDS = ['badword1', 'badword2', 'spam']

# Сообщения для постов
ZODIAC_MESSAGES = [
    "✨ Звезды советуют сегодня быть более открытыми к новым возможностям!",
    "🌟 Сегодня отличный день для реализации ваших планов!",
    "💫 Вселенная посылает вам знаки - будьте внимательны!",
    "⭐ Ваша интуиция сегодня особенно сильна, доверьтесь ей!",
    "🔮 День принесет неожиданные, но приятные сюрпризы!",
    "✨ Сегодня ваша энергия на пике - используйте её мудро!",
    "🌙 Луна благосклонна к новым начинаниям сегодня!"
]

EVENING_MESSAGES = [
    "День подходит к концу, время подвести итоги и поблагодарить за прожитый день! 🙏",
    "Вечер - время для размышлений и планирования завтрашнего дня! 🌅",
    "Пусть звезды подарят вам спокойный сон и яркие сны! ⭐",
    "Завершите день с благодарностью в сердце! 💝",
    "Отдохните и наберитесь сил для новых свершений! 💪",
    "Вечер - время для душевного покоя и гармонии! 🕯️",
    "Пусть ночь принесет восстановление и новые идеи! 💭"
]

# Валидация конфигурации
def validate_config() -> bool:
    """Проверяет корректность конфигурации"""
    if not BOT_TOKEN:
        # В CI/CD среде токен может отсутствовать - это нормально
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            print("⚠️ BOT_TOKEN отсутствует, но это ожидаемо в CI/CD среде")
            return True
        else:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    if not os.path.exists(IMAGES_PATH):
        print(f"⚠️ Предупреждение: папка с изображениями не найдена: {IMAGES_PATH}")
    
    return True

if __name__ == "__main__":
    validate_config()
    print("✅ Конфигурация корректна")
