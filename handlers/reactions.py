# handlers/reactions.py - Обработчики реакций
import logging
from typing import Optional, List, Any

from telegram import Update, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes
from utils.database import reactions_db
from utils.keyboards import get_zodiac_keyboard, get_morning_variants_keyboard, get_reaction_keyboard
from config import REACTION_NAMES, REACTION_MESSAGES

async def handle_reaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик реакций на посты"""
    query = update.callback_query
    if not query or not hasattr(query, 'data') or query.data is None:
        return
    
    data = query.data
    if not isinstance(data, str) or not data.startswith("react_"):
        return
    
    # Логируем для отладки
    chat_type = "КАНАЛ" if query.message and query.message.chat.type == 'channel' else "ЛИЧКА"
    logging.info(f"🔘 Callback реакции из {chat_type}: {data}")
    
    # Парсим callback_data в формате "react_{reaction}_{post_id}"
    parts = data.split('_', 2)
    
    if len(parts) < 3:
        logging.error(f"❌ Неверный формат callback_data: {data}")
        return
    
    reaction = parts[1]
    post_id = parts[2]
    user_id = str(update.effective_user.id) if update.effective_user else None
    
    if not user_id:
        logging.error(f"❌ Нет user_id")
        return
    
    # Проверяем валидность реакции
    try:
        idx = REACTION_NAMES.index(reaction)
    except ValueError:
        logging.error(f"❌ Неизвестная реакция: {reaction}")
        return
    
    # Добавляем реакцию через базу данных
    previous_reaction = reactions_db.add_user_reaction(user_id, reaction, post_id)
    
    # Определяем сообщение для показа
    if previous_reaction:
        message_to_show = "🔄 Вы уже поставили реакцию на этот пост!"
        logging.info(f"🔄 Пользователь {user_id} уже имеет реакцию: {previous_reaction}")
    else:
        # Безопасно получаем сообщение по индексу
        if idx < len(REACTION_MESSAGES):
            message_to_show = f"✅ {REACTION_MESSAGES[idx]}"
        else:
            message_to_show = "✅ Спасибо за реакцию!"
        logging.info(f"✅ Добавлена новая реакция {reaction} для поста {post_id}")
        
        # Обновляем клавиатуру только если реакция была добавлена
        await update_post_keyboard(query, post_id, context)
    
    # Показываем всплывающее сообщение
    try:
        await query.answer(message_to_show, show_alert=True)
        logging.info(f"💬 Показано сообщение пользователю")
    except Exception as e:
        logging.error(f"❌ Ошибка показа сообщения: {e}")
        try:
            await query.answer("✅ Спасибо!")
        except Exception as e2:
            logging.error(f"❌ Критическая ошибка: {e2}")

async def update_post_keyboard(query: CallbackQuery, post_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обновляет клавиатуру поста с новыми счетчиками реакций"""
    try:
        # Определяем тип клавиатуры на основе существующей
        base_keyboard: InlineKeyboardMarkup
        
        if query.message and query.message.reply_markup and query.message.reply_markup.inline_keyboard:
            existing_keyboard = query.message.reply_markup.inline_keyboard
            
            # Проверяем есть ли утренние варианты
            has_morning_variants = any(
                any(hasattr(btn, 'callback_data') and btn.callback_data and 
                    isinstance(btn.callback_data, str) and btn.callback_data.startswith('morning_variant') 
                    for btn in row) 
                for row in existing_keyboard
            )
            
            if has_morning_variants:
                # Утренний пост - добавляем варианты утра
                base_keyboard = get_morning_variants_keyboard()
            else:
                # Гороскоп или вечерний пост - зодиак
                base_keyboard = get_zodiac_keyboard()
        else:
            # По умолчанию - зодиак
            base_keyboard = get_zodiac_keyboard()
        
        # Получаем клавиатуру с реакциями
        reactions_keyboard = get_reaction_keyboard(post_id)
        
        # Объединяем клавиатуры
        combined_keyboard = base_keyboard.inline_keyboard + reactions_keyboard.inline_keyboard
        new_reply_markup = InlineKeyboardMarkup(combined_keyboard)
        
        # Обновляем сообщение
        chat_type = "КАНАЛ" if query.message and query.message.chat and query.message.chat.type == 'channel' else "ЛИЧКА"
        
        if chat_type == "КАНАЛ" and query.message and query.message.chat and hasattr(query.message, 'message_id'):
            # Для канала используем bot.edit_message_reply_markup
            await context.bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=new_reply_markup
            )
            logging.info(f"🔄 Клавиатура КАНАЛА обновлена")
        else:
            # Для личных сообщений используем query.edit_message_reply_markup
            await query.edit_message_reply_markup(reply_markup=new_reply_markup)
            logging.info(f"🔄 Клавиатура ЛИЧНЫХ СООБЩЕНИЙ обновлена")
            
    except Exception as e:
        logging.error(f"❌ Ошибка обновления клавиатуры: {e}")
        
        # Попробуем альтернативный метод
        if "can't be edited" in str(e).lower():
            logging.info(f"⚠️ Сообщение нельзя редактировать, но счетчик обновлен в базе данных")
        else:
            logging.error(f"❌ Не удалось обновить клавиатуру: {e}")
