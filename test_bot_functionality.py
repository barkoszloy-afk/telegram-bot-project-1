#!/usr/bin/env python3
"""
Test script for the refactored Telegram bot
Tests basic functionality without requiring Telegram credentials
"""

import sys
import os
import asyncio
import logging
from unittest.mock import Mock, AsyncMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock environment variables for testing
os.environ['BOT_TOKEN'] = 'test_token_123456789'
os.environ['ADMIN_ID'] = '123456789'

async def test_bot_imports():
    """Test that all bot components can be imported without errors"""
    print("🧪 Testing bot imports...")
    
    try:
        # Test config import
        from config import validate_config, BOT_TOKEN, ADMIN_ID
        print("✅ Config imported successfully")
        
        # Test handlers import
        from handlers import (
            about_command,
            profile_command,
            admin_command,
            stats_command,
            random_command,
            ping_command,
            show_main_menu
        )
        print("✅ All handlers imported successfully")
        
        # Test utilities import
        from utils.keyboards import create_main_menu_keyboard
        from utils.database import reactions_db
        from utils.exceptions import BotError
        print("✅ All utilities imported successfully")
        
        # Test main bot class
        from main_bot import TelegramBot
        print("✅ Main bot class imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_command_handlers():
    """Test individual command handlers with mock data"""
    print("\n🧪 Testing command handlers...")
    
    try:
        # Import handlers
        from handlers.user_commands import about_command
        from handlers.diagnostics import ping_command
        from handlers.content_commands import random_command
        
        # Create mock update and context
        mock_update = Mock()
        mock_update.effective_user = Mock()
        mock_update.effective_user.id = 123456789
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.message = Mock()
        mock_update.message.reply_text = AsyncMock()
        
        mock_context = Mock()
        mock_context.args = []
        
        # Test about command
        await about_command(mock_update, mock_context)
        print("✅ About command executed successfully")
        
        # Test ping command
        await ping_command(mock_update, mock_context)
        print("✅ Ping command executed successfully")
        
        # Test random command
        await random_command(mock_update, mock_context)
        print("✅ Random command executed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Handler test error: {e}")
        return False

async def test_database_operations():
    """Test database operations"""
    print("\n🧪 Testing database operations...")
    
    try:
        from utils.database import reactions_db
        
        # Test adding reaction
        reactions_db.add_reaction(123, "test_post", "❤️")
        print("✅ Add reaction successful")
        
        # Test getting reaction
        reaction = reactions_db.get_reaction(123, "test_post")
        assert reaction == "❤️", f"Expected ❤️, got {reaction}"
        print("✅ Get reaction successful")
        
        # Test getting post reactions
        post_reactions = reactions_db.get_post_reactions("test_post")
        assert "❤️" in post_reactions, "Reaction not found in post reactions"
        print("✅ Get post reactions successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

async def test_keyboard_generation():
    """Test keyboard generation utilities"""
    print("\n🧪 Testing keyboard generation...")
    
    try:
        from utils.keyboards import (
            create_main_menu_keyboard,
            create_back_to_menu_keyboard,
            get_reaction_keyboard,
            create_zodiac_keyboard
        )
        
        # Test main menu keyboard
        main_keyboard = create_main_menu_keyboard()
        assert main_keyboard is not None, "Main keyboard is None"
        print("✅ Main menu keyboard created successfully")
        
        # Test back button keyboard
        back_keyboard = create_back_to_menu_keyboard()
        assert back_keyboard is not None, "Back keyboard is None"
        print("✅ Back to menu keyboard created successfully")
        
        # Test reaction keyboard
        reaction_keyboard = get_reaction_keyboard("test_post")
        assert reaction_keyboard is not None, "Reaction keyboard is None"
        print("✅ Reaction keyboard created successfully")
        
        # Test zodiac keyboard
        zodiac_keyboard = create_zodiac_keyboard()
        assert zodiac_keyboard is not None, "Zodiac keyboard is None"
        print("✅ Zodiac keyboard created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Keyboard test error: {e}")
        return False

async def test_bot_initialization():
    """Test bot initialization without starting it"""
    print("\n🧪 Testing bot initialization...")
    
    try:
        from main_bot import TelegramBot
        
        # Create bot instance
        bot = TelegramBot()
        assert bot is not None, "Bot instance is None"
        print("✅ Bot instance created successfully")
        
        # Check if app is None initially
        assert bot.app is None, "App should be None before run()"
        print("✅ Bot app is correctly None before initialization")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization test error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Telegram Bot Tests\n")
    
    tests = [
        test_bot_imports,
        test_command_handlers,
        test_database_operations,
        test_keyboard_generation,
        test_bot_initialization
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    # Run tests
    result = asyncio.run(main())
    sys.exit(0 if result else 1)