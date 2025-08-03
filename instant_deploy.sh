#!/bin/bash

# 🚀 Мгновенный автоматический деплой
# Этот скрипт для быстрого деплоя без интерактивных вопросов

set -e

echo "⚡ Запускаем мгновенный деплой..."

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Проверяем Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI не установлен. Запустите ./deploy.sh для полной установки"
    exit 1
fi

# Проверяем авторизацию
if ! railway whoami &> /dev/null; then
    echo "❌ Не авторизованы в Railway. Запустите ./deploy.sh для авторизации"
    exit 1
fi

# Коммитим изменения если есть
if [[ -n $(git status --porcelain) ]]; then
    print_step "Коммитим изменения..."
    git add .
    git commit -m "🚀 Quick deploy: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Отправляем в GitHub
if git remote get-url origin &> /dev/null; then
    print_step "Отправляем в GitHub..."
    git push origin main 2>/dev/null || echo "⚠️ Не удалось отправить в GitHub"
fi

# Деплоим
print_step "Деплоим в Railway..."
railway up --detach

print_success "🎉 Мгновенный деплой завершен!"

# Показываем полезную информацию
echo ""
echo "📊 Полезные команды:"
echo "   railway logs     - логи в реальном времени"
echo "   railway status   - статус проекта"
echo "   railway open     - открыть в браузере"
echo ""

# Получаем URL если возможно
URL=$(railway domain 2>/dev/null | head -n 1 | awk '{print $2}' || echo "")
if [[ -n "$URL" ]]; then
    echo "🌐 URL: https://$URL"
    echo "❤️ Health: https://$URL/health"
fi
