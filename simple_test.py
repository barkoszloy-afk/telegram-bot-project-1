# simple_test.py - Простой тест без импортов
import os
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return {"status": "ok", "test": "simple"}

@app.route('/')
def root():
    return {"message": "Simple test server", "bot_token": bool(os.environ.get('BOT_TOKEN'))}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
