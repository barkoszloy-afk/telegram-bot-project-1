# handlers/content_commands.py - Команды для работы с контентом
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Примерные данные для демонстрации
SAMPLE_POSTS = [
    {
        "id": "1",
        "title": "Астрологический прогноз на сегодня",
        "content": "Сегодня звезды благоволят новым начинаниям. Особенно удачный день для знаков огня!",
        "category": "Астрология",
        "date": "2025-08-04",
        "views": 150
    },
    {
        "id": "2", 
        "title": "Медитация для начинающих",
        "content": "Простые техники медитации, которые помогут вам расслабиться и найти внутреннее спокойствие.",
        "category": "Медитация",
        "date": "2025-08-03",
        "views": 89
    },
    {
        "id": "3",
        "title": "Нумерологический анализ имени",
        "content": "Узнайте, что означают цифры в вашем имени и как они влияют на вашу судьбу.",
        "category": "Нумерология", 
        "date": "2025-08-02",
        "views": 234
    },
    {
        "id": "4",
        "title": "Фазы Луны и их влияние",
        "content": "Как лунные циклы влияют на нашу жизнь, эмоции и энергетику.",
        "category": "Астрология",
        "date": "2025-08-01",
        "views": 67
    },
    {
        "id": "5",
        "title": "Таро для самопознания",
        "content": "Как использовать карты Таро для глубокого понимания себя и своих желаний.",
        "category": "Таро",
        "date": "2025-07-31",
        "views": 112
    }
]

CATEGORIES = [
    "Астрология", "Нумерология", "Таро", "Медитация", 
    "Руны", "Хиромантия", "Энергетика", "Сновидения"
]

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /random - случайный пост"""
    try:
        # Выбираем случайный пост
        post = random.choice(SAMPLE_POSTS)
        
        # Создаем клавиатуру с реакциями
        keyboard = []
        reaction_row = []
        
        from config import REACTION_EMOJIS
        for i, reaction in enumerate(REACTION_EMOJIS[:4]):  # Показываем первые 4 реакции
            reaction_row.append(
                InlineKeyboardButton(
                    reaction, 
                    callback_data=f"reaction_{i}_{post['id']}"
                )
            )
        
        keyboard.append(reaction_row)
        keyboard.append([
            InlineKeyboardButton("📊 Статистика", callback_data=f"stats_{post['id']}"),
            InlineKeyboardButton("🔄 Другой пост", callback_data="random_new")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        post_text = (
            f"🎲 **Случайный пост**\n\n"
            f"**{post['title']}**\n\n"
            f"{post['content']}\n\n"
            f"📂 Категория: {post['category']}\n"
            f"📅 Дата: {post['date']}\n"
            f"👁 Просмотров: {post['views']}"
        )
        
        if update.message:
            await update.message.reply_text(
                post_text, 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                post_text,
                parse_mode='Markdown', 
                reply_markup=reply_markup
            )
            await update.callback_query.answer("🎲 Новый случайный пост!")
        
        logger.info(f"🎲 Случайный пост показан пользователю {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /random: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении случайного поста")

async def popular_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /popular - популярные посты"""
    try:
        # Сортируем посты по просмотрам
        popular_posts = sorted(SAMPLE_POSTS, key=lambda x: x['views'], reverse=True)[:3]
        
        popular_text = "🔥 **Популярные посты**\n\n"
        
        for i, post in enumerate(popular_posts, 1):
            popular_text += (
                f"**{i}. {post['title']}**\n"
                f"📂 {post['category']} | 👁 {post['views']} просмотров\n"
                f"{post['content'][:100]}{'...' if len(post['content']) > 100 else ''}\n\n"
            )
        
        # Клавиатура для навигации
        keyboard = []
        post_row = []
        
        for i, post in enumerate(popular_posts):
            post_row.append(
                InlineKeyboardButton(
                    f"{i+1}. {post['title'][:20]}...",
                    callback_data=f"show_post_{post['id']}"
                )
            )
            if len(post_row) == 2:  # По 2 кнопки в ряду
                keyboard.append(post_row)
                post_row = []
        
        if post_row:  # Добавляем оставшиеся кнопки
            keyboard.append(post_row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                popular_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        logger.info(f"🔥 Популярные посты показаны пользователю {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /popular: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении популярных постов")

async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /recent - последние посты"""
    try:
        # Сортируем посты по дате
        recent_posts = sorted(SAMPLE_POSTS, key=lambda x: x['date'], reverse=True)[:3]
        
        recent_text = "🆕 **Последние посты**\n\n"
        
        for i, post in enumerate(recent_posts, 1):
            recent_text += (
                f"**{i}. {post['title']}**\n"
                f"📅 {post['date']} | 📂 {post['category']}\n"
                f"{post['content'][:100]}{'...' if len(post['content']) > 100 else ''}\n\n"
            )
        
        # Клавиатура для просмотра полных постов
        keyboard = []
        for i, post in enumerate(recent_posts):
            keyboard.append([
                InlineKeyboardButton(
                    f"📖 Читать полностью: {post['title'][:30]}...",
                    callback_data=f"show_post_{post['id']}"
                )
            ])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                recent_text,
                parse_mode='Markdown', 
                reply_markup=reply_markup
            )
        
        logger.info(f"🆕 Последние посты показаны пользователю {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /recent: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении последних постов")

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /categories - список категорий"""
    try:
        # Подсчитываем количество постов в каждой категории
        category_counts = {}
        for post in SAMPLE_POSTS:
            category = post['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        categories_text = "📂 **Категории контента**\n\n"
        
        for category in CATEGORIES:
            count = category_counts.get(category, 0)
            categories_text += f"• {category}: {count} постов\n"
        
        categories_text += f"\n📊 Всего категорий: {len(CATEGORIES)}\n"
        categories_text += f"📰 Всего постов: {len(SAMPLE_POSTS)}"
        
        # Клавиатура с категориями
        keyboard = []
        row = []
        
        for category in CATEGORIES:
            if category_counts.get(category, 0) > 0:  # Показываем только категории с постами
                row.append(
                    InlineKeyboardButton(
                        f"{category} ({category_counts[category]})",
                        callback_data=f"category_{category}"
                    )
                )
                if len(row) == 2:  # По 2 кнопки в ряду
                    keyboard.append(row)
                    row = []
        
        if row:  # Добавляем оставшиеся кнопки
            keyboard.append(row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(
                categories_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        logger.info(f"📂 Категории показаны пользователю {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /categories: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении категорий")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /search - поиск по контенту"""
    try:
        # Получаем аргументы поиска
        query = ' '.join(context.args).lower() if context.args else ""
        
        if not query:
            search_text = (
                f"🔍 **Поиск по контенту**\n\n"
                f"Используйте команду в формате:\n"
                f"`/search ваш запрос`\n\n"
                f"**Примеры:**\n"
                f"• `/search астрология`\n"
                f"• `/search медитация луна`\n"
                f"• `/search таро карты`\n\n"
                f"**Доступные категории для поиска:**\n"
                f"{', '.join(CATEGORIES)}"
            )
            
            if update.message:
                await update.message.reply_text(search_text, parse_mode='Markdown')
            return
        
        # Ищем посты по запросу
        found_posts = []
        for post in SAMPLE_POSTS:
            if (query in post['title'].lower() or 
                query in post['content'].lower() or 
                query in post['category'].lower()):
                found_posts.append(post)
        
        if not found_posts:
            search_text = (
                f"🔍 **Результаты поиска**\n\n"
                f"По запросу \"{query}\" ничего не найдено.\n\n"
                f"Попробуйте:\n"
                f"• Изменить запрос\n"
                f"• Использовать другие ключевые слова\n"
                f"• Посмотреть /categories для доступных тем"
            )
        else:
            search_text = f"🔍 **Результаты поиска по \"{query}\"**\n\n"
            search_text += f"Найдено: {len(found_posts)} постов\n\n"
            
            for i, post in enumerate(found_posts[:5], 1):  # Показываем максимум 5 результатов
                search_text += (
                    f"**{i}. {post['title']}**\n"
                    f"📂 {post['category']} | 📅 {post['date']}\n"
                    f"{post['content'][:80]}{'...' if len(post['content']) > 80 else ''}\n\n"
                )
            
            if len(found_posts) > 5:
                search_text += f"... и еще {len(found_posts) - 5} результатов"
        
        # Клавиатура с результатами
        keyboard = []
        for post in found_posts[:3]:  # Показываем кнопки для первых 3 результатов
            keyboard.append([
                InlineKeyboardButton(
                    f"📖 {post['title'][:30]}...",
                    callback_data=f"show_post_{post['id']}"
                )
            ])
            
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        if update.message:
            await update.message.reply_text(
                search_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        logger.info(f"🔍 Поиск '{query}' выполнен пользователем {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /search: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при выполнении поиска")
