# utils/openai_client.py - Интеграция с OpenAI ChatGPT

import os
import logging
import asyncio
from typing import List, Dict, Optional, Union
from openai import AsyncOpenAI
import json

logger = logging.getLogger(__name__)

class ChatGPTClient:
    """Клиент для работы с ChatGPT API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY не найден в переменных окружения")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI клиент инициализирован")
        
        # Настройки по умолчанию
        self.default_model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.temperature = 0.7
        self.conversation_history = {}
    
    def is_available(self) -> bool:
        """Проверяет, доступен ли ChatGPT API"""
        return self.client is not None and self.api_key is not None
    
    async def chat_completion(
        self,
        message: str,
        user_id: int,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Union[str, bool, int]]:
        """
        Отправляет запрос в ChatGPT и возвращает ответ
        
        Args:
            message: Сообщение пользователя
            user_id: ID пользователя для истории разговора
            system_prompt: Системный промпт (опционально)
            model: Модель GPT (по умолчанию gpt-3.5-turbo)
            max_tokens: Максимальное количество токенов
            temperature: Температура (креативность) ответа
            
        Returns:
            Dict с ответом, статусом и метаданными
        """
        if not self.is_available():
            return {
                "success": False,
                "response": "❌ ChatGPT API недоступен. Проверьте настройки.",
                "error": "API_NOT_AVAILABLE"
            }
        
        try:
            # Используем значения по умолчанию, если не указаны
            model = model or self.default_model
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature
            
            # Получаем историю разговора для пользователя
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Создаем список сообщений
            messages = []
            
            # Добавляем системный промпт, если есть
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Добавляем историю разговора (последние 10 сообщений)
            history = self.conversation_history[user_id][-10:]
            messages.extend(history)
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})
            
            logger.info(f"🤖 Отправляем запрос в ChatGPT для пользователя {user_id}")
            logger.debug(f"Сообщений в истории: {len(messages)}")
            
            # Отправляем запрос в OpenAI
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Извлекаем ответ
            ai_response = response.choices[0].message.content
            
            # Сохраняем в историю
            self.conversation_history[user_id].append({"role": "user", "content": message})
            self.conversation_history[user_id].append({"role": "assistant", "content": ai_response})
            
            # Ограничиваем размер истории (максимум 20 сообщений)
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            logger.info(f"✅ Получен ответ от ChatGPT для пользователя {user_id}")
            
            return {
                "success": True,
                "response": ai_response,
                "model_used": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "conversation_length": len(self.conversation_history[user_id])
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка ChatGPT API: {e}")
            return {
                "success": False,
                "response": f"❌ Ошибка обработки запроса: {str(e)}",
                "error": str(e)
            }
    
    async def generate_horoscope(self, zodiac_sign: str, user_id: int) -> str:
        """Генерирует персонализированный гороскоп"""
        system_prompt = f"""
        Ты - профессиональный астролог с многолетним опытом. 
        Создай подробный, вдохновляющий гороскоп для знака зодиака {zodiac_sign}.
        
        Включи:
        - Общий прогноз на день
        - Совет по отношениям
        - Рекомендации по карьере
        - Счастливые числа и цвета
        - Эмоциональное настроение
        
        Стиль: теплый, поддерживающий, мистический
        Длина: 150-200 слов
        """
        
        message = f"Создай гороскоп для знака {zodiac_sign} на сегодня"
        result = await self.chat_completion(message, user_id, system_prompt)
        
        if result["success"]:
            return f"🔮 **Гороскоп для {zodiac_sign}**\n\n{result['response']}"
        else:
            return f"❌ Не удалось создать гороскоп: {result.get('error', 'Неизвестная ошибка')}"
    
    async def generate_morning_message(self, user_id: int) -> str:
        """Генерирует доброе утро с мотивацией"""
        system_prompt = """
        Ты - мудрый духовный наставник. Создай вдохновляющее утреннее послание.
        
        Включи:
        - Теплое приветствие
        - Мотивирующую мысль
        - Практический совет на день
        - Положительную энергию
        
        Стиль: добрый, мотивирующий, духовный
        Длина: 100-150 слов
        """
        
        message = "Создай доброе утреннее послание с мотивацией на день"
        result = await self.chat_completion(message, user_id, system_prompt)
        
        if result["success"]:
            return f"🌅 **Доброе утро!**\n\n{result['response']}"
        else:
            return f"❌ Не удалось создать утреннее послание: {result.get('error', 'Неизвестная ошибка')}"
    
    async def generate_evening_message(self, user_id: int) -> str:
        """Генерирует вечернее послание с рефлексией"""
        system_prompt = """
        Ты - мудрый духовный наставник. Создай спокойное вечернее послание.
        
        Включи:
        - Теплое обращение
        - Рефлексию о прошедшем дне
        - Благодарность и принятие
        - Пожелания на ночь
        
        Стиль: спокойный, умиротворяющий, мудрый
        Длина: 100-150 слов
        """
        
        message = "Создай вечернее послание для размышлений и покоя"
        result = await self.chat_completion(message, user_id, system_prompt)
        
        if result["success"]:
            return f"🌙 **Вечернее послание**\n\n{result['response']}"
        else:
            return f"❌ Не удалось создать вечернее послание: {result.get('error', 'Неизвестная ошибка')}"
    
    async def generate_tarot_reading(self, question: str, user_id: int) -> str:
        """Генерирует расклад таро"""
        system_prompt = """
        Ты - опытный таролог с глубоким пониманием символики карт Таро.
        Создай интуитивный расклад на одну карту.
        
        Включи:
        - Название карты и её значение
        - Интерпретацию в контексте вопроса
        - Практические советы
        - Духовное послание
        
        Стиль: мистический, мудрый, вдохновляющий
        Длина: 150-200 слов
        """
        
        message = f"Сделай расклад таро на вопрос: {question}"
        result = await self.chat_completion(message, user_id, system_prompt)
        
        if result["success"]:
            return f"🔮 **Карта дня**\n\n{result['response']}"
        else:
            return f"❌ Не удалось создать расклад: {result.get('error', 'Неизвестная ошибка')}"
    
    async def answer_spiritual_question(self, question: str, user_id: int) -> str:
        """Отвечает на духовные вопросы"""
        system_prompt = """
        Ты - мудрый духовный наставник с глубоким пониманием жизни.
        Отвечай на вопросы с состраданием и мудростью.
        
        Стиль: мудрый, поддерживающий, вдохновляющий
        Избегай: догматизма, категорических суждений
        Фокус: на внутреннем росте и понимании
        """
        
        result = await self.chat_completion(question, user_id, system_prompt)
        
        if result["success"]:
            return f"🧘‍♀️ **Духовный ответ**\n\n{result['response']}"
        else:
            return f"❌ Не удалось обработать вопрос: {result.get('error', 'Неизвестная ошибка')}"
    
    def clear_conversation(self, user_id: int) -> bool:
        """Очищает историю разговора пользователя"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"🗑️ Очищена история разговора для пользователя {user_id}")
            return True
        return False
    
    def get_conversation_length(self, user_id: int) -> int:
        """Возвращает количество сообщений в истории пользователя"""
        return len(self.conversation_history.get(user_id, []))

# Глобальный экземпляр клиента
chatgpt_client = ChatGPTClient()
