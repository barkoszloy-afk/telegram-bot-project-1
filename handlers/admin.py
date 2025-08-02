# handlers/admin.py - Обработчики админ-панели
import asyncio
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import ADMIN_ID, CHANNEL_ID, ZODIAC_MESSAGES, EVENING_MESSAGES
from utils.keyboards import (
    create_admin_post_keyboard, 
    create_admin_menu_keyboard,
    create_admin_preview_keyboard
)
from utils.database import reactions_db

async def handle_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin - показывает админ-панель"""
    if not update.effective_user or not update.message:
        return
        
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав администратора")
        return
    
    reply_markup = create_admin_menu_keyboard()
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
        await preview_morning_post(query, context)
    elif action == 'admin_horoscope':
        await preview_horoscope_post(query, context)
    elif action == 'admin_evening':
        await preview_evening_post(query, context)
    elif action == 'admin_cleanup':
        await cleanup_old_data(query, context)
    elif action.startswith('publish_'):
        await publish_post_to_channel(query, context)
    elif action.startswith('cancel_'):
        await cancel_post_preview(query, context)

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

async def preview_morning_post(query, context: ContextTypes.DEFAULT_TYPE):
    """Показывает предпросмотр утреннего поста"""
    try:
        post_text = """🌅 Доброе утро! ✨

Новый день — новые возможности! 🚀
Пусть этот день принесет вам радость, успех и вдохновение! 💫

Выберите ваш настрой на день:"""
        
        post_id = f"morning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем предпросмотр с кнопками управления
        preview_markup = create_admin_preview_keyboard("morning", post_id)
        
        preview_text = f"""📋 ПРЕДПРОСМОТР УТРЕННЕГО ПОСТА:

{post_text}

🔽 Кнопки, которые будут добавлены:
🌅 Заряд энергии
🌞 Путь к победам  
⭐ Звездный путь
❤️ 🙏 🥹 (реакции)

Опубликовать этот пост в канал?"""
        
        await query.edit_message_text(preview_text, reply_markup=preview_markup)
        
    except Exception as e:
        logging.error(f"Ошибка создания предпросмотра утреннего поста: {e}")
        await query.edit_message_text(f"❌ Ошибка создания предпросмотра: {e}")

async def preview_horoscope_post(query, context: ContextTypes.DEFAULT_TYPE):
    """Показывает предпросмотр поста с гороскопом"""
    try:
        horoscope_text = random.choice(ZODIAC_MESSAGES)
        post_id = f"horoscope_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем предпросмотр с кнопками управления
        preview_markup = create_admin_preview_keyboard("horoscope", post_id)
        
        preview_text = f"""📋 ПРЕДПРОСМОТР ГОРОСКОПА:

{horoscope_text}

🔽 Кнопки, которые будут добавлены:
♈ Овен ♉ Телец ♊ Близнецы ♋ Рак
♌ Лев ♍ Дева ♎ Весы ♏ Скорпион  
♐ Стрелец ♑ Козерог ♒ Водолей ♓ Рыбы
❤️ 🙏 🥹 (реакции)

Опубликовать этот пост в канал?"""
        
        await query.edit_message_text(preview_text, reply_markup=preview_markup)
        
    except Exception as e:
        logging.error(f"Ошибка создания предпросмотра гороскопа: {e}")
        await query.edit_message_text(f"❌ Ошибка создания предпросмотра: {e}")

async def preview_evening_post(query, context: ContextTypes.DEFAULT_TYPE):
    """Показывает предпросмотр вечернего поста"""
    try:
        evening_text = random.choice(EVENING_MESSAGES)
        post_id = f"evening_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем предпросмотр с кнопками управления
        preview_markup = create_admin_preview_keyboard("evening", post_id)
        
        preview_text = f"""📋 ПРЕДПРОСМОТР ВЕЧЕРНЕГО ПОСТА:

{evening_text}

🔽 Кнопки, которые будут добавлены:
♈ Овен ♉ Телец ♊ Близнецы ♋ Рак
♌ Лев ♍ Дева ♎ Весы ♏ Скорпион  
♐ Стрелец ♑ Козерог ♒ Водолей ♓ Рыбы
❤️ 🙏 🥹 (реакции)

Опубликовать этот пост в канал?"""
        
        await query.edit_message_text(preview_text, reply_markup=preview_markup)
        
    except Exception as e:
        logging.error(f"Ошибка создания предпросмотра вечернего поста: {e}")
        await query.edit_message_text(f"❌ Ошибка создания предпросмотра: {e}")

async def publish_post_to_channel(query, context: ContextTypes.DEFAULT_TYPE):
    """Публикует пост в канал после подтверждения"""
    try:
        action = query.data
        if not action:
            return
            
        # Парсим действие: publish_{type}_{post_id}
        parts = action.split('_', 2)
        if len(parts) < 3:
            await query.edit_message_text("❌ Ошибка формата команды")
            return
            
        post_type = parts[1]  # morning/horoscope/evening
        post_id = parts[2]
        
        # Определяем контент и тип клавиатуры
        if post_type == 'morning':
            post_text = """🌅 Доброе утро! ✨

Новый день — новые возможности! 🚀
Пусть этот день принесет вам радость, успех и вдохновение! 💫

Выберите ваш настрой на день:"""
            keyboard = create_admin_post_keyboard(post_id, 'morning')
            
        elif post_type == 'horoscope':
            post_text = random.choice(ZODIAC_MESSAGES)
            keyboard = create_admin_post_keyboard(post_id, 'zodiac')
            
        elif post_type == 'evening':
            post_text = random.choice(EVENING_MESSAGES)  
            keyboard = create_admin_post_keyboard(post_id, 'zodiac')
            
        else:
            await query.edit_message_text("❌ Неизвестный тип поста")
            return
        
        # Отправляем пост в канал
        message = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            reply_markup=keyboard
        )
        
        await query.edit_message_text(f"✅ Пост опубликован в канал!\nТип: {post_type}\nID: {post_id}")
        
    except Exception as e:
        logging.error(f"Ошибка публикации поста: {e}")
        await query.edit_message_text(f"❌ Ошибка публикации: {e}")

async def cancel_post_preview(query, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет публикацию поста"""
    await query.edit_message_text("❌ Публикация отменена. Используйте /admin для новой команды.")

async def cleanup_old_data(query, context: ContextTypes.DEFAULT_TYPE):
    """Очищает старые данные реакций"""
    try:
        # Очищаем данные старше 30 дней
        cleaned_count = reactions_db.cleanup_old_data(30)
        
        await query.edit_message_text(f"✅ Очистка завершена!\nУдалено записей: {cleaned_count}")
        
    except Exception as e:
        logging.error(f"Ошибка очистки данных: {e}")
        await query.edit_message_text(f"❌ Ошибка очистки: {e}")
        evening_text = random.choice(EVENING_MESSAGES)
        post_text = f"🌙 Добрый вечер! ✨\n\n{evening_text}"
        
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
