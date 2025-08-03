"""Кастомные исключения для телеграм бота."""

from typing import Optional


class BotException(Exception):
    """Базовое исключение для бота."""
    
    def __init__(self, message: str, user_message: Optional[str] = None) -> None:
        """
        Инициализация исключения.
        
        Args:
            message: Техническое сообщение для логов
            user_message: Сообщение для показа пользователю
        """
        super().__init__(message)
        self.user_message = user_message or "Произошла ошибка. Попробуйте позже."


class AccessDeniedException(BotException):
    """Исключение для отказа в доступе."""
    
    def __init__(self, user_id: int, action: str) -> None:
        message = f"Пользователь {user_id} попытался выполнить {action} без прав"
        user_message = "❌ У вас нет прав для выполнения этого действия"
        super().__init__(message, user_message)
        self.user_id = user_id
        self.action = action


class InvalidCommandException(BotException):
    """Исключение для неверных команд."""
    
    def __init__(self, command: str, expected_format: Optional[str] = None) -> None:
        message = f"Неверная команда: {command}"
        if expected_format:
            message += f". Ожидаемый формат: {expected_format}"
            user_message = f"❌ Неверный формат команды. Используйте: {expected_format}"
        else:
            user_message = "❌ Неверная команда"
        
        super().__init__(message, user_message)
        self.command = command
        self.expected_format = expected_format


class DatabaseException(BotException):
    """Исключение для ошибок базы данных."""
    
    def __init__(self, operation: str, details: str) -> None:
        message = f"Ошибка БД при {operation}: {details}"
        user_message = "❌ Временные проблемы с данными. Попробуйте позже."
        super().__init__(message, user_message)
        self.operation = operation
        self.details = details


class ValidationException(BotException):
    """Исключение для ошибок валидации данных."""
    
    def __init__(self, field: str, value: str, reason: str) -> None:
        message = f"Ошибка валидации {field}='{value}': {reason}"
        user_message = f"❌ Неверное значение для {field}: {reason}"
        super().__init__(message, user_message)
        self.field = field
        self.value = value
        self.reason = reason


class PostingException(BotException):
    """Исключение для ошибок публикации постов."""
    
    def __init__(self, post_type: str, reason: str) -> None:
        message = f"Ошибка публикации {post_type}: {reason}"
        user_message = f"❌ Не удалось опубликовать {post_type}"
        super().__init__(message, user_message)
        self.post_type = post_type
        self.reason = reason


class ReactionException(BotException):
    """Исключение для ошибок с реакциями."""
    
    def __init__(self, reaction: str, user_id: int, reason: str) -> None:
        message = f"Ошибка реакции {reaction} от пользователя {user_id}: {reason}"
        user_message = "❌ Не удалось добавить реакцию"
        super().__init__(message, user_message)
        self.reaction = reaction
        self.user_id = user_id
        self.reason = reason
