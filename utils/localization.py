"""Локализация бота с поддержкой многих языков."""

import json
import logging
import os
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class Localization:
    """Класс для работы с локализацией."""
    
    def __init__(self, default_locale: str = "ru") -> None:
        """
        Инициализация системы локализации.
        
        Args:
            default_locale: Язык по умолчанию
        """
        self.default_locale = default_locale
        self.locales: Dict[str, Dict[str, Any]] = {}
        self._load_locales()
    
    def _load_locales(self) -> None:
        """Загрузка всех файлов локализации."""
        locales_dir = os.path.join(os.path.dirname(__file__), "..", "locales")
        
        if not os.path.exists(locales_dir):
            logger.warning(f"Директория локализации не найдена: {locales_dir}")
            return
        
        for filename in os.listdir(locales_dir):
            if filename.endswith(".json"):
                locale_code = filename[:-5]  # убираем .json
                file_path = os.path.join(locales_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.locales[locale_code] = json.load(f)
                    logger.info(f"Загружена локализация: {locale_code}")
                except Exception as e:
                    logger.error(f"Ошибка загрузки локализации {locale_code}: {e}")
    
    def get(
        self, 
        key: str, 
        locale: Optional[str] = None, 
        **kwargs: Union[str, int]
    ) -> str:
        """
        Получение локализованной строки.
        
        Args:
            key: Ключ строки в формате "section.subsection.key"
            locale: Код языка (если None, используется default_locale)
            **kwargs: Параметры для форматирования строки
            
        Returns:
            Локализованная строка
        """
        if locale is None:
            locale = self.default_locale
        
        # Если локаль не найдена, используем default
        if locale not in self.locales:
            locale = self.default_locale
        
        # Если и default не найден, возвращаем ключ
        if locale not in self.locales:
            logger.warning(f"Локализация {locale} не найдена")
            return key
        
        # Получаем значение по пути ключа
        try:
            value = self.locales[locale]
            for part in key.split('.'):
                value = value[part]
            
            # Форматируем строку с параметрами
            if kwargs and isinstance(value, str):
                return value.format(**kwargs)
            
            return str(value)
            
        except (KeyError, TypeError) as e:
            logger.warning(f"Ключ локализации не найден: {key} для {locale}: {e}")
            return key
    
    def get_available_locales(self) -> list[str]:
        """Получение списка доступных языков."""
        return list(self.locales.keys())


# Глобальный экземпляр для использования в боте
i18n = Localization()


def _(key: str, locale: Optional[str] = None, **kwargs: Union[str, int]) -> str:
    """
    Сокращенная функция для получения локализованной строки.
    
    Args:
        key: Ключ строки
        locale: Код языка
        **kwargs: Параметры для форматирования
        
    Returns:
        Локализованная строка
    """
    return i18n.get(key, locale, **kwargs)


def get_user_locale(user_id: int) -> str:
    """
    Получение языка пользователя (пока заглушка).
    
    В будущем здесь можно добавить логику определения языка:
    - По настройкам Telegram
    - По сохраненным предпочтениям пользователя
    - По геолокации
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Код языка
    """
    # Пока возвращаем русский для всех
    return "ru"
