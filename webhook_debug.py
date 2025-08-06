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
    """Отладочный webhook с улучшенной диагностикой"""
    try:
        logger.info(f"🎯 Webhook получил запрос с токеном: {token[:10]}...")
        
        # Проверяем BOT_TOKEN
        bot_token = os.environ.get('BOT_TOKEN')
        logger.info(f"🔑 BOT_TOKEN из env: {'настроен' if bot_token else 'НЕ НАЙДЕН'}")
        
        # Проверяем соответствие токенов
        if bot_token and token != bot_token:
            logger.warning(f"⚠️ Токен в URL не совпадает с BOT_TOKEN")
            return '', 404
        
        # Получаем данные
        try:
            data = request.get_json()
            logger.info(f"📨 Получены данные: {data is not None}")
            if data:
                logger.info(f"📊 Тип данных: {type(data)}, ключи: {list(data.keys()) if isinstance(data, dict) else 'не dict'}")
        except Exception as json_error:
            logger.error(f"❌ Ошибка парсинга JSON: {json_error}")
            return '', 400
        
        # Обрабатываем сообщение
        if data and 'message' in data:
            try:
                msg = data['message']
                text = msg.get('text', '')
                user_id = msg.get('from', {}).get('id', 'unknown')
                chat_id = msg.get('chat', {}).get('id', user_id)
                logger.info(f"👤 Пользователь {user_id}, чат {chat_id}, текст: '{text}'")
                
                # Отправляем ответ на /test
                if text == '/test':
                    try:
                        import requests
                        use_token = bot_token or token
                        url = f"https://api.telegram.org/bot{use_token}/sendMessage"
                        response_data = {
                            "chat_id": chat_id,
                            "text": "✅ WEBHOOK ИСПРАВЛЕН! Отладочная версия работает корректно!"
                        }
                        resp = requests.post(url, json=response_data, timeout=10)
                        logger.info(f"📤 Ответ отправлен: {resp.status_code}")
                        if resp.status_code != 200:
                            logger.error(f"❌ Ошибка отправки: {resp.text}")
                    except Exception as send_error:
                        logger.error(f"❌ Ошибка отправки сообщения: {send_error}")
            except Exception as msg_error:
                logger.error(f"❌ Ошибка обработки сообщения: {msg_error}")
        
        logger.info("✅ Webhook обработан успешно")
        return '', 200
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка webhook: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return '', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
