#!/usr/bin/env python3
"""
Deployment Status Checker
Quick script to check the status of the deployed Telegram bot
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://telegram-bot-project-1-production.up.railway.app"
ENDPOINTS = {
    "health": f"{BASE_URL}/health",
    "metrics": f"{BASE_URL}/metrics"
}

def check_endpoint(name, url):
    """Check if an endpoint is responding"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            try:
                data = response.json()
                if name == "health":
                    print(f"   Status: {data.get('status', 'Unknown')}")
                    print(f"   Uptime: {data.get('uptime', 'Unknown')}")
                elif name == "metrics":
                    print(f"   Uptime: {data.get('uptime_hours', 'Unknown')} hours")
                    print(f"   Memory: {data.get('memory_usage_mb', 'Unknown')} MB")
            except json.JSONDecodeError:
                print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ {name}: Error ({response.status_code})")
            return False
    except requests.RequestException as e:
        print(f"❌ {name}: Connection failed - {e}")
        return False

def main():
    """Main deployment status check"""
    print("🔍 Checking Telegram Bot Deployment Status")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("-" * 50)
    
    all_ok = True
    
    # Check each endpoint
    for name, url in ENDPOINTS.items():
        if not check_endpoint(name, url):
            all_ok = False
        print()
    
    # Overall status
    print("-" * 50)
    if all_ok:
        print("🎉 All systems operational!")
        print("🤖 Bot is running and responding correctly")
        sys.exit(0)
    else:
        print("⚠️  Some issues detected")
        print("📋 Check Railway logs for more details")
        print("🔧 Run: railway logs (if Railway CLI is installed)")
        sys.exit(1)

if __name__ == "__main__":
    main()