#!/bin/bash

# 🚀 Автоматический скрипт деплоя на Railway
# Этот скрипт автоматически развернет ваш Telegram Bot на Railway

set -e  # Остановка при любой ошибке

echo "🚀 Начинаем автоматический деплой Telegram Bot на Railway..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для красивого вывода
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка установки Railway CLI
check_railway_cli() {
    print_step "Проверяем установку Railway CLI..."
    
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI не установлен. Устанавливаем..."
        
        # Установка Railway CLI
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install railway
            else
                curl -fsSL https://railway.app/install.sh | sh
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            curl -fsSL https://railway.app/install.sh | sh
        else
            print_error "Неподдерживаемая операционная система. Установите Railway CLI вручную: https://docs.railway.app/develop/cli"
            exit 1
        fi
        
        # Добавляем в PATH
        export PATH="$HOME/.railway/bin:$PATH"
        
        print_success "Railway CLI установлен"
    else
        print_success "Railway CLI уже установлен"
    fi
}

# Авторизация в Railway
login_railway() {
    print_step "Проверяем авторизацию в Railway..."
    
    if ! railway whoami &> /dev/null; then
        print_step "Необходима авторизация в Railway..."
        print_warning "Сейчас откроется браузер для авторизации в Railway"
        read -p "Нажмите Enter для продолжения..."
        
        railway login
        
        if railway whoami &> /dev/null; then
            print_success "Успешно авторизованы в Railway"
        else
            print_error "Ошибка авторизации в Railway"
            exit 1
        fi
    else
        RAILWAY_USER=$(railway whoami)
        print_success "Уже авторизованы как: $RAILWAY_USER"
    fi
}

# Создание или связывание проекта
setup_project() {
    print_step "Настраиваем проект в Railway..."
    
    # Проверяем, есть ли уже связанный проект
    if railway status &> /dev/null; then
        PROJECT_INFO=$(railway status)
        print_success "Проект уже связан с Railway"
        echo "$PROJECT_INFO"
    else
        print_step "Создаем новый проект в Railway..."
        
        # Создаем новый проект
        railway project create telegram-bot-project-1
        
        # Связываем с текущей директорией
        railway link
        
        print_success "Проект создан и связан"
    fi
}

# Настройка переменных окружения
setup_environment() {
    print_step "Настраиваем переменные окружения..."
    
    # Проверяем существующие переменные
    print_step "Текущие переменные окружения:"
    railway vars || true
    
    echo ""
    print_warning "Необходимо настроить переменные окружения:"
    echo "1. BOT_TOKEN - токен от @BotFather"
    echo "2. ADMIN_ID - ваш Telegram ID"
    echo "3. CHANNEL_ID - ID канала (опционально)"
    
    read -p "Хотите настроить переменные сейчас? (y/n): " setup_vars
    
    if [[ $setup_vars == "y" || $setup_vars == "Y" ]]; then
        echo ""
        print_step "Настройка BOT_TOKEN:"
        echo "Получите токен от @BotFather в Telegram:"
        echo "1. Напишите @BotFather"
        echo "2. Используйте /newbot"
        echo "3. Следуйте инструкциям"
        read -p "Введите BOT_TOKEN: " bot_token
        railway vars set BOT_TOKEN="$bot_token"
        
        echo ""
        print_step "Настройка ADMIN_ID:"
        echo "Получите ваш Telegram ID от @userinfobot"
        read -p "Введите ADMIN_ID: " admin_id
        railway vars set ADMIN_ID="$admin_id"
        
        echo ""
        read -p "Хотите настроить CHANNEL_ID? (y/n): " setup_channel
        if [[ $setup_channel == "y" || $setup_channel == "Y" ]]; then
            read -p "Введите CHANNEL_ID: " channel_id
            railway vars set CHANNEL_ID="$channel_id"
        fi
        
        # Устанавливаем PORT для Railway
        railway vars set PORT=8000
        
        print_success "Переменные окружения настроены"
    else
        print_warning "Не забудьте настроить переменные позже через 'railway vars set'"
    fi
}

# Деплой проекта
deploy_project() {
    print_step "Запускаем деплой..."
    
    # Убеждаемся, что все изменения закоммичены
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "Есть незакоммиченные изменения. Коммитим автоматически..."
        git add .
        git commit -m "🚀 Auto-deploy: $(date)"
    fi
    
    # Отправляем в GitHub (если настроен remote)
    if git remote get-url origin &> /dev/null; then
        print_step "Отправляем изменения в GitHub..."
        git push origin main || print_warning "Не удалось отправить в GitHub (это не критично)"
    fi
    
    # Деплой в Railway
    print_step "Деплоим в Railway..."
    railway up --detach
    
    print_success "Деплой запущен!"
}

# Проверка деплоя
check_deployment() {
    print_step "Проверяем статус деплоя..."
    
    # Ждем немного для завершения деплоя
    sleep 10
    
    # Получаем URL проекта
    PROJECT_URL=$(railway domain | head -n 1 | awk '{print $2}' 2>/dev/null || echo "")
    
    if [[ -n "$PROJECT_URL" ]]; then
        print_success "Проект развернут по адресу: https://$PROJECT_URL"
        
        # Проверяем healthcheck
        print_step "Проверяем работоспособность..."
        sleep 5
        
        if curl -s "https://$PROJECT_URL/health" > /dev/null; then
            print_success "✨ Бот успешно развернут и работает!"
            echo ""
            echo "🎯 Полезные ссылки:"
            echo "   🌐 Основной URL: https://$PROJECT_URL"
            echo "   ❤️  Healthcheck: https://$PROJECT_URL/health"
            echo "   📋 Логи: https://$PROJECT_URL/logs"
            echo "   🏗️  Railway Dashboard: https://railway.app/dashboard"
            echo ""
            echo "📱 Протестируйте бота в Telegram:"
            echo "   1. Найдите вашего бота"
            echo "   2. Отправьте /start"
            echo "   3. Проверьте работу меню"
        else
            print_warning "Деплой завершен, но healthcheck недоступен"
            print_warning "Проверьте логи в Railway Dashboard"
        fi
    else
        # Если URL не получен, показываем статус
        print_step "Статус проекта:"
        railway status
        print_success "Деплой завершен! Проверьте статус в Railway Dashboard"
    fi
}

# Главная функция
main() {
    echo "🎯 Автоматический деплой Telegram Bot на Railway"
    echo "================================================="
    echo ""
    
    # Проверяем, что мы в правильной директории
    if [[ ! -f "main_bot_railway.py" ]]; then
        print_error "Файл main_bot_railway.py не найден. Убедитесь, что вы в правильной директории."
        exit 1
    fi
    
    # Выполняем все шаги
    check_railway_cli
    login_railway
    setup_project
    setup_environment
    deploy_project
    check_deployment
    
    echo ""
    print_success "🎉 Автоматический деплой завершен!"
    echo ""
    echo "📚 Дополнительные команды:"
    echo "   railway logs     - просмотр логов"
    echo "   railway status   - статус проекта"
    echo "   railway vars     - переменные окружения"
    echo "   railway open     - открыть в браузере"
    echo ""
}

# Запуск скрипта
main "$@"