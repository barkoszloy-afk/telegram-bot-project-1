# webhook_debug.py - Диагностика webhook
import logging
import os
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "webhook_debug": "active"})

@app.route('/webhook/<token>', methods=['POST'])
def webhook_debug(token):
    """Отладочный webhook"""
    try:
        logger.info(f"🎯 Webhook получил запрос с токеном: {token[:10]}...")
        
        data = request.get_json()
        logger.info(f"📨 Данные: {data}")
        
        # Простая проверка
        if data and 'message' in data:
            msg = data['message']
            text = msg.get('text', '')
            user_id = msg.get('from', {}).get('id', 'unknown')
            logger.info(f"👤 Пользователь {user_id} написал: {text}")
            
            # Отправляем простой ответ
            if text == '/test':
                import requests
                bot_token = os.environ.get('BOT_TOKEN', token)
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                response_data = {
                    "chat_id": user_id,
                    "text": "✅ Webhook работает! Получена команда /test"
                }
                resp = requests.post(url, json=response_data)
                logger.info(f"📤 Ответ отправлен: {resp.status_code}")
        
        return '', 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка в webhook: {e}")
        return '', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
