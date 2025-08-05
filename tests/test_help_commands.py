"""
Test script to verify help commands functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import main_bot
        import config
        from handlers import admin, reactions
        from utils import database, keyboards
        assert True, "All modules imported successfully"
    except ImportError as e:
        pytest.fail(f"Import error: {e}")

def test_deployment_config():
    """Test deployment configuration files"""
    # Check Procfile exists and is not empty
    procfile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Procfile")
    assert os.path.exists(procfile_path), "Procfile should exist"
    
    with open(procfile_path, "r") as f:
        content = f.read().strip()
        assert content, "Procfile should not be empty"
        assert "python" in content, "Procfile should contain python command"

def test_railway_config():
    """Test Railway configuration"""
    railway_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "railway.json")
    assert os.path.exists(railway_config_path), "railway.json should exist"
    
    import json
    with open(railway_config_path, "r") as f:
        config = json.load(f)
        assert "deploy" in config, "railway.json should have deploy configuration"
        assert "startCommand" in config["deploy"], "railway.json should have startCommand"

def test_requirements():
    """Test requirements.txt has necessary dependencies"""
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")
    assert os.path.exists(requirements_path), "requirements.txt should exist"
    
    with open(requirements_path, "r") as f:
        content = f.read()
        assert "python-telegram-bot" in content, "Should include telegram bot library"
        assert "python-dotenv" in content, "Should include dotenv library"

def test_dockerfile():
    """Test Dockerfile configuration"""
    dockerfile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile should exist"
    
    with open(dockerfile_path, "r") as f:
        content = f.read()
        assert "FROM python:" in content, "Should use Python base image"
        assert "requirements.txt" in content, "Should install requirements"

if __name__ == "__main__":
    test_imports()
    test_deployment_config()
    test_railway_config()
    test_requirements()
    test_dockerfile()
    print("✅ All deployment tests passed!")
