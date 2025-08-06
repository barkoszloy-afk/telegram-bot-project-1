# handlers/chatgpt_commands.py - Команды ChatGPT для бота

import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.openai_client import chatgpt_client

logger = logging.getLogger(__name__)

async def chatgpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Основная команда /chatgpt - показывает главное меню ChatGPT"""
    try:
        if not update.message or not update.effective_user:
            return
        
        user_id = update.effective_user.id
        
        # Проверяем доступность ChatGPT
        if not chatgpt_client.is_available():
            await update.message.reply_text(
                "❌ **ChatGPT недоступен**\n\n"
                "Для использования AI-функций необходимо:\n"
                "1. Добавить OPENAI_API_KEY в переменные окружения\n"
                "2. Перезапустить бота\n\n"
                "🔧 Обратитесь к администратору для настройки.",
                parse_mode='Markdown'
            )
            return
        
        # Создаем клавиатуру с опциями ChatGPT
        keyboard = [
            [
                InlineKeyboardButton("🔮 Гороскоп", callback_data="gpt_horoscope"),
                InlineKeyboardButton("🌅 Доброе утро", callback_data="gpt_morning")
            ],
            [
                InlineKeyboardButton("🌙 Вечернее послание", callback_data="gpt_evening"),
                InlineKeyboardButton("🃏 Карта дня", callback_data="gpt_tarot")
            ],
            [
                InlineKeyboardButton("💬 Задать вопрос", callback_data="gpt_question"),
                InlineKeyboardButton("🧘‍♀️ Духовный совет", callback_data="gpt_spiritual")
            ],
            [
                InlineKeyboardButton("📊 Статистика чата", callback_data="gpt_stats"),
                InlineKeyboardButton("🗑️ Очистить историю", callback_data="gpt_clear")
            ],
            [
                InlineKeyboardButton("🔙 Назад в главное меню", callback_data="back_to_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        conversation_length = chatgpt_client.get_conversation_length(user_id)
        history_text = f"\n\n📝 Сообщений в истории: {conversation_length}" if conversation_length > 0 else ""
        
        await update.message.reply_text(
            f"🤖 **ChatGPT Помощник**\n\n"
            f"Выберите, что вас интересует:\n\n"
            f"🔮 **Эзотерика**: Гороскопы, карты, предсказания\n"
            f"💬 **Общение**: Вопросы и духовные советы\n"
            f"📊 **Управление**: Статистика и настройки{history_text}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"🤖 ChatGPT меню показано пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /chatgpt: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Ошибка при показе ChatGPT меню"
            )

async def handle_chatgpt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик callback запросов ChatGPT"""
    try:
        query = update.callback_query
        if not query or not query.data or not update.effective_user:
            return
        
        await query.answer()
        user_id = update.effective_user.id
        data = query.data
        
        # Проверяем доступность ChatGPT
        if not chatgpt_client.is_available():
            await query.edit_message_text(
                "❌ ChatGPT API недоступен. Обратитесь к администратору."
            )
            return
        
        # Показываем индикатор загрузки
        await query.edit_message_text("🤖 Обрабатываю запрос...")
        
        if data == "gpt_horoscope":
            await handle_horoscope_selection(update, context)
            
        elif data == "gpt_morning":
            response = await chatgpt_client.generate_morning_message(user_id)
            await query.edit_message_text(
                response,
                parse_mode='Markdown'
            )
            
        elif data == "gpt_evening":
            response = await chatgpt_client.generate_evening_message(user_id)
            await query.edit_message_text(
                response,
                parse_mode='Markdown'
            )
            
        elif data == "gpt_tarot":
            await handle_tarot_question(update, context)
            
        elif data == "gpt_question":
            await query.edit_message_text(
                "💬 **Задайте ваш вопрос**\n\n"
                "Просто напишите ваш вопрос следующим сообщением.\n"
                "Я отвечу как мудрый помощник! 🤖\n\n"
                "💡 Пример: 'Как найти смысл жизни?' или 'Что делать при стрессе?'"
            )
            # Устанавливаем режим ожидания вопроса
            context.user_data['waiting_for_gpt_question'] = True
            
        elif data == "gpt_spiritual":
            await query.edit_message_text(
                "🧘‍♀️ **Духовный совет**\n\n"
                "Опишите вашу ситуацию или задайте духовный вопрос.\n"
                "Я дам мудрый совет с точки зрения духовного развития.\n\n"
                "💫 Пример: 'Как простить обиду?' или 'Как найти внутренний покой?'"
            )
            # Устанавливаем режим ожидания духовного вопроса
            context.user_data['waiting_for_spiritual_question'] = True
            
        elif data == "gpt_stats":
            await show_chatgpt_stats(update, context)
            
        elif data == "gpt_clear":
            await handle_clear_history(update, context)
            
        elif data == "confirm_clear_history":
            # Очищаем историю разговора
            chatgpt_client.clear_conversation(user_id)
            await query.edit_message_text(
                "✅ **История очищена!**\n\n"
                "ChatGPT теперь не помнит предыдущие сообщения.\n"
                "Можете начать новый разговор с чистого листа! 🆕"
            )
            
        elif data.startswith("zodiac_gpt_"):
            # Обработка выбора знака зодиака для гороскопа
            zodiac_sign = data.replace("zodiac_gpt_", "")
            response = await chatgpt_client.generate_horoscope(zodiac_sign, user_id)
            await query.edit_message_text(
                response,
                parse_mode='Markdown'
            )
            
        elif data == "back_to_main":
            # Возвращаемся в главное меню ChatGPT
            await chatgpt_command(update, context)
            
    except Exception as e:
        logger.error(f"❌ Ошибка ChatGPT callback: {e}")
        if query:
            await query.edit_message_text(
                f"❌ Ошибка обработки запроса: {str(e)}"
            )

async def handle_horoscope_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает выбор знаков зодиака для гороскопа"""
    query = update.callback_query
    if not query:
        return
    
    # Знаки зодиака с эмодзи
    zodiac_signs = [
        ("Овен", "♈"), ("Телец", "♉"), ("Близнецы", "♊"), ("Рак", "♋"),
        ("Лев", "♌"), ("Дева", "♍"), ("Весы", "♎"), ("Скорпион", "♏"),
        ("Стрелец", "♐"), ("Козерог", "♑"), ("Водолей", "♒"), ("Рыбы", "♓")
    ]
    
    # Создаем клавиатуру 3x4
    keyboard = []
    for i in range(0, len(zodiac_signs), 3):
        row = []
        for j in range(3):
            if i + j < len(zodiac_signs):
                name, emoji = zodiac_signs[i + j]
                row.append(InlineKeyboardButton(
                    f"{emoji} {name}",
                    callback_data=f"zodiac_gpt_{name}"
                ))
        keyboard.append(row)
    
    # Кнопка возврата
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔮 **Выберите ваш знак зодиака**\n\n"
        "Я создам персонализированный гороскоп с помощью ChatGPT!",
        reply_markup=reply_markup
    )

async def handle_tarot_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает запрос карты дня"""
    query = update.callback_query
    if not query:
        return
    
    await query.edit_message_text(
        "🃏 **Карта дня**\n\n"
        "Сформулируйте ваш вопрос для карт Таро следующим сообщением.\n\n"
        "💫 Примеры вопросов:\n"
        "• 'Что мне нужно знать о сегодняшнем дне?'\n"
        "• 'Какой совет дают карты по поводу...?'\n"
        "• 'Что ждет меня в ближайшем будущем?'"
    )
    # Устанавливаем режим ожидания вопроса для таро
    context.user_data['waiting_for_tarot_question'] = True

async def show_chatgpt_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает статистику использования ChatGPT"""
    query = update.callback_query
    if not query or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    conversation_length = chatgpt_client.get_conversation_length(user_id)
    
    # Кнопка возврата
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📊 **Ваша статистика ChatGPT**\n\n"
        f"💬 Сообщений в истории: {conversation_length}\n"
        f"🤖 Модель: GPT-3.5-Turbo\n"
        f"🎯 Режим: Эзотерический помощник\n\n"
        f"💡 **Информация:**\n"
        f"• История сохраняется до 20 сообщений\n"
        f"• Контекст используется для лучших ответов\n"
        f"• Данные не передаются третьим лицам",
        reply_markup=reply_markup
    )

async def handle_clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает очистку истории разговора"""
    query = update.callback_query
    if not query or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    
    # Кнопки подтверждения
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, очистить", callback_data="confirm_clear_history"),
            InlineKeyboardButton("❌ Отмена", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    conversation_length = chatgpt_client.get_conversation_length(user_id)
    
    await query.edit_message_text(
        f"🗑️ **Очистить историю разговора?**\n\n"
        f"Сейчас в истории: {conversation_length} сообщений\n\n"
        f"⚠️ После очистки ChatGPT не будет помнить предыдущий контекст разговора.\n"
        f"Это может быть полезно для начала нового тематического разговора.",
        reply_markup=reply_markup
    )

async def process_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Обрабатывает сообщения для ChatGPT
    Возвращает True, если сообщение было обработано ChatGPT
    """
    try:
        if not update.message or not update.message.text or not update.effective_user:
            return False
        
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # Проверяем, ожидается ли ответ для ChatGPT
        waiting_for_question = context.user_data.get('waiting_for_gpt_question', False)
        waiting_for_spiritual = context.user_data.get('waiting_for_spiritual_question', False)
        waiting_for_tarot = context.user_data.get('waiting_for_tarot_question', False)
        
        if waiting_for_question:
            # Обычный вопрос ChatGPT
            context.user_data['waiting_for_gpt_question'] = False
            
            await update.message.reply_text("🤖 Обрабатываю ваш вопрос...")
            result = await chatgpt_client.chat_completion(text, user_id)
            
            if result["success"]:
                response = f"💬 **Ответ ChatGPT:**\n\n{result['response']}"
                if len(response) > 4000:
                    # Разбиваем длинные сообщения
                    await update.message.reply_text(response[:4000])
                    await update.message.reply_text(response[4000:])
                else:
                    await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text(str(result["response"]))
            
            return True
            
        elif waiting_for_spiritual:
            # Духовный вопрос
            context.user_data['waiting_for_spiritual_question'] = False
            
            await update.message.reply_text("🧘‍♀️ Медитирую над вашим вопросом...")
            response = await chatgpt_client.answer_spiritual_question(text, user_id)
            
            await update.message.reply_text(response, parse_mode='Markdown')
            return True
            
        elif waiting_for_tarot:
            # Вопрос для карт Таро
            context.user_data['waiting_for_tarot_question'] = False
            
            await update.message.reply_text("🃏 Тасую карты и читаю знаки...")
            response = await chatgpt_client.generate_tarot_reading(text, user_id)
            
            await update.message.reply_text(response, parse_mode='Markdown')
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки GPT сообщения: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Ошибка при обработке вашего сообщения"
            )
        return True  # Возвращаем True, чтобы показать, что сообщение было "обработано"
