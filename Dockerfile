FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Открываем порт
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app
ENV PORT=8000

# Запускаем бота
CMD ["python", "main_bot_railway.py"]
