# utils/exceptions.py - Custom exceptions for the bot

class BotError(Exception):
    """Base exception for bot errors"""
    pass

class ConfigurationError(BotError):
    """Configuration related errors"""
    pass

class DatabaseError(BotError):
    """Database operation errors"""
    pass

class HandlerError(BotError):
    """Handler execution errors"""
    pass

class ValidationError(BotError):
    """Input validation errors"""
    pass