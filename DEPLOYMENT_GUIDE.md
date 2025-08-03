# 🚀 Руководство по развертыванию Telegram Bot

## 📋 Предварительные требования

### 1. Подготовка бота в Telegram
```
1. Создайте бота через @BotFather
2. Получите BOT_TOKEN
3. Настройте webhook (будет настроен автоматически)
```

### 2. Подготовка канала
```
1. Создайте канал для публикации постов
2. Добавьте бота как администратора
3. Получите CHANNEL_ID (начинается с -100...)
```

### 3. Определите ADMIN_ID
```
1. Напишите боту @userinfobot
2. Получите ваш ID пользователя
```

## 🌐 Развертывание на Railway

### Шаг 1: Подготовка к развертыванию

```bash
# Убедитесь, что все файлы готовы
ls -la | grep -E "(Procfile|railway.json|requirements.txt|main_bot_railway.py)"

# Проверьте основной файл
python3 -m py_compile main_bot_railway.py
```

### Шаг 2: Railway CLI (рекомендуемый способ)

```bash
# Установите Railway CLI
npm install -g @railway/cli

# Войдите в аккаунт
railway login

# Инициализируйте проект
railway init

# Установите переменные окружения
railway variables set BOT_TOKEN="ваш_токен_бота"
railway variables set ADMIN_ID="ваш_id"
railway variables set CHANNEL_ID="id_канала"

# Деплой
railway up
```

### Шаг 3: Railway Web Dashboard

1. Зайдите на [railway.app](https://railway.app)
2. Подключите GitHub репозиторий
3. Добавьте переменные окружения:
   - `BOT_TOKEN` - токен вашего бота
   - `ADMIN_ID` - ваш ID в Telegram  
   - `CHANNEL_ID` - ID канала для постов
4. Нажмите "Deploy"

### Шаг 4: Настройка webhook

После развертывания Railway предоставит URL вида: `https://yourapp.railway.app`

Webhook настроится автоматически при первом запуске бота.

Или настройте вручную:
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
     -d "url=https://yourapp.railway.app/webhook/<BOT_TOKEN>"
```

## 🔧 Локальная разработка

### Настройка окружения

```bash
# Создайте виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или .venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Установите dev зависимости
pip install pytest pytest-asyncio pytest-cov mypy black isort flake8
```

### Создайте .env файл

```bash
# .env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_admin_id_here
CHANNEL_ID=your_channel_id_here
```

### Запуск локально

```bash
# Запуск с webhook (для production)
python main_bot_railway.py

# Для разработки лучше использовать polling:
python main_bot_minimal.py
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=. --cov-report=html

# Конкретные модули
pytest tests/utils/test_keyboards.py -v
```

### Проверка типов

```bash
# Mypy проверка
mypy --config-file pyproject.toml main_bot_railway.py

# Линтинг
black --check .
isort --check-only .
flake8 .
```

## 📊 Мониторинг

### Эндпоинты для мониторинга

- `GET /health` - Проверка здоровья
- `GET /status` - Статус бота  
- `GET /logs` - Последние логи
- `GET /` - Главная страница

### Пример проверки

```bash
curl https://yourapp.railway.app/health
# Ответ: {"status": "healthy", "bot": "active", ...}
```

## 🔍 Диагностика проблем

### Проверка переменных окружения

```bash
railway variables
```

### Проверка логов

```bash
railway logs
```

### Локальная отладка

```bash
# Проверка webhook
python test_webhook.py

# Проверка функций бота
python simple_test.py
```

## 🎯 CI/CD с GitHub Actions

Workflow уже настроен в `.github/workflows/ci.yml`:

1. **При push в main:**
   - Запускаются тесты
   - Проверяется код (lint, types)
   - Автоматически деплоится на Railway

2. **При pull request:**
   - Полная проверка кода
   - Тесты безопасности

## 🔒 Безопасность

### Переменные окружения
- ❌ Никогда не коммитьте `.env` файлы
- ✅ Используйте Railway variables
- ✅ Регулярно ротируйте токены

### Webhook безопасность
- URL webhook содержит BOT_TOKEN для дополнительной защиты
- Проверка IP адресов Telegram (опционально)

## 📈 Масштабирование

### Railway настройки
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python3 main_bot_railway.py",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Оптимизации
- Кэширование данных (уже реализовано)
- Фоновые задачи через threading
- Graceful shutdown обработка

## 🆘 Поддержка

### Если что-то не работает:

1. **Проверьте логи:** `railway logs`
2. **Проверьте health:** `curl https://yourapp.railway.app/health`
3. **Локальный тест:** `python main_bot_railway.py`
4. **Переустановка webhook:** Перезапустите сервис

### Полезные команды

```bash
# Полная переустановка
railway down
railway up

# Просмотр переменных
railway variables

# Подключение к терминалу
railway shell
```

## ✅ Чек-лист успешного развертывания

- [ ] Bot Token получен от @BotFather
- [ ] Канал создан и бот добавлен как админ  
- [ ] ADMIN_ID определен
- [ ] Переменные окружения установлены на Railway
- [ ] Код успешно деплоится
- [ ] Health check возвращает OK
- [ ] Webhook настроен автоматически
- [ ] Бот отвечает на /start
- [ ] Админ-панель работает (/admin)
- [ ] CI/CD pipeline активен

🎉 **Проект готов к работе!**
