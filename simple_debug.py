# simple_debug.py - Простейшая диагностика без зависимостей
from flask import Flask, request, jsonify
import sys
import traceback

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "simple-debug",
        "python_version": sys.version
    })

@app.route('/webhook/<token>', methods=['POST'])
def webhook_simple(token):
    """Простейший webhook без зависимостей"""
    try:
        print(f"[INFO] Webhook вызван с токеном: {token[:10]}...")
        
        try:
            data = request.get_json()
            print(f"[INFO] JSON данные получены: {data is not None}")
        except Exception as e:
            print(f"[ERROR] Ошибка JSON: {e}")
            return 'JSON Error', 400
        
        if data and 'message' in data:
            msg = data['message']
            text = msg.get('text', '')
            print(f"[INFO] Получен текст: {text}")
            
            if text == '/test':
                print(f"[INFO] Обнаружена команда /test")
                # Простейший ответ через API
                try:
                    import requests
                    chat_id = msg.get('chat', {}).get('id')
                    if chat_id:
                        url = f"https://api.telegram.org/bot{token}/sendMessage"
                        resp = requests.post(url, json={
                            "chat_id": chat_id,
                            "text": "✅ ПРОСТЕЙШИЙ WEBHOOK РАБОТАЕТ!"
                        }, timeout=10)
                        print(f"[INFO] Ответ отправлен: {resp.status_code}")
                except Exception as send_error:
                    print(f"[ERROR] Ошибка отправки: {send_error}")
        
        print(f"[INFO] Webhook завершен успешно")
        return '', 200
        
    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return 'Internal Error', 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"[INFO] Запуск на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
