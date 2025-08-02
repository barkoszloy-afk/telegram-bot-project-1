# handlers/admin.py - Обработчики админ-панели
import asyncio
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import ADMIN_ID, CHANNEL_ID, ZODIAC_MESSAGES, EVENING_MESSAGES
from utils.keyboards import create_admin_post_keyboard
from utils.database import reactions_db

async def handle_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin - показывает админ-панель"""
    if not update.effective_user or not update.message:
        return
        
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав администратора")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data='admin_stats')],
        [InlineKeyboardButton("🌅 Утренний пост", callback_data='admin_morning')],
        [InlineKeyboardButton("🔮 Гороскоп", callback_data='admin_horoscope')],
        [InlineKeyboardButton("🌙 Вечерний пост", callback_data='admin_evening')],
        [InlineKeyboardButton("🔄 Очистить старые данные", callback_data='admin_cleanup')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔧 Админ-панель:", reply_markup=reply_markup)

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик админ-команд"""
    query = update.callback_query
    if not query or not update.effective_user:
        return
        
    await query.answer()
    
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ У вас нет прав администратора")
        return
    
    action = query.data
    if not action:
        return
    
    if action == 'admin_stats':
        await show_statistics(query, context)
    elif action == 'admin_morning':
        await create_morning_post(query, context)
    elif action == 'admin_horoscope':
        await create_horoscope_post(query, context)
    elif action == 'admin_evening':
        await create_evening_post(query, context)
    elif action == 'admin_cleanup':
        await cleanup_old_data(query, context)

async def show_statistics(query, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статистику реакций"""
    try:
        data = reactions_db.get_data()
        total_users = len(data.get('users', {}))
        total_reactions = sum(len(user_data.get('reactions', {})) for user_data in data.get('users', {}).values())
        posts_count = len(data.get('posts', {}))
        
        stats_text = f"""📊 Статистика бота:
        
👥 Всего пользователей: {total_users}
👍 Всего реакций: {total_reactions}
📝 Постов с реакциями: {posts_count}

📈 Популярные реакции:"""
        
        # Считаем популярность реакций
        reaction_counts = {}
        for user_data in data.get('users', {}).values():
            for reaction in user_data.get('reactions', {}).values():
                reaction_counts[reaction] = reaction_counts.get(reaction, 0) + 1
        
        if reaction_counts:
            sorted_reactions = sorted(reaction_counts.items(), key=lambda x: x[1], reverse=True)
            for reaction, count in sorted_reactions[:5]:
                stats_text += f"\n{reaction}: {count}"
        
        await query.edit_message_text(stats_text)
        
    except Exception as e:
        logging.error(f"Ошибка получения статистики: {e}")
        await query.edit_message_text("❌ Ошибка получения статистики")

async def create_morning_post(query, context: ContextTypes.DEFAULT_TYPE):
    """Создает утренний пост"""
    try:
        post_text = """🌅 Доброе утро! ✨

Новый день — новые возможности! 🚀
Пусть этот день принесет вам радость, успех и вдохновение! 💫

Выберите ваш настрой на день:"""
        
        post_id = f"morning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        keyboard = create_admin_post_keyboard(post_id, 'morning')
        
        message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            reply_markup=keyboard
        )
        
        await query.edit_message_text(f"✅ Утренний пост опубликован!\nID поста: {post_id}")
        
    except Exception as e:
        logging.error(f"Ошибка создания утреннего поста: {e}")
        await query.edit_message_text(f"❌ Ошибка создания поста: {e}")

async def create_horoscope_post(query, context: ContextTypes.DEFAULT_TYPE):
    """Создает пост с гороскопом"""
    try:
        horoscope_text = random.choice(ZODIAC_MESSAGES)
        post_text = f"🔮 Гороскоп на сегодня\n\n{horoscope_text}"
        
        post_id = f"horoscope_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        keyboard = create_admin_post_keyboard(post_id, 'zodiac')
        
        message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            reply_markup=keyboard
        )
        
        await query.edit_message_text(f"✅ Гороскоп опубликован!\nID поста: {post_id}")
        
    except Exception as e:
        logging.error(f"Ошибка создания гороскопа: {e}")
        await query.edit_message_text(f"❌ Ошибка создания поста: {e}")

async def create_evening_post(query, context: ContextTypes.DEFAULT_TYPE):
    """Создает вечерний пост"""
    try:
        evening_text = random.choice(EVENING_MESSAGES)
        post_text = f"🌙 Добрый вечер! ✨\n\n{evening_text}"
        
        post_id = f"evening_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        keyboard = create_admin_post_keyboard(post_id, 'zodiac')
        
        message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            reply_markup=keyboard
        )
        
        await query.edit_message_text(f"✅ Вечерний пост опубликован!\nID поста: {post_id}")
        
    except Exception as e:
        logging.error(f"Ошибка создания вечернего поста: {e}")
        await query.edit_message_text(f"❌ Ошибка создания поста: {e}")

async def cleanup_old_data(query, context: ContextTypes.DEFAULT_TYPE):
    """Очищает старые данные реакций"""
    try:
        cleaned_count = reactions_db.cleanup_old_data()
        await query.edit_message_text(f"✅ Очищено записей: {cleaned_count}")
        
    except Exception as e:
        logging.error(f"Ошибка очистки данных: {e}")
        await query.edit_message_text(f"❌ Ошибка очистки: {e}")

async def handle_morning_variant_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора утренних вариантов"""
    query = update.callback_query
    if not query:
        return
        
    await query.answer()
    
    data = query.data
    if not data:
        return
        
    if data == 'morning_variant1':
        message = "🌅 Заряд энергии выбран! Отличного дня! ⚡"
    elif data == 'morning_variant2':
        message = "🌞 Путь к победам открыт! Удачи! 🏆"
    elif data == 'morning_variant3':
        message = "⭐ Звездный путь начинается! Вперед! 🚀"
    else:
        message = "✨ Спасибо за выбор!"
    
    await query.answer(message, show_alert=True)
