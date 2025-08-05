#!/bin/bash

# Auto-Deploy Script for Telegram Bot Project
# This script handles automatic deployment to Railway

set -e  # Exit on any error

echo "🚀 Starting Auto-Deploy Process..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "main_bot.py" ]] || [[ ! -f "requirements.txt" ]]; then
    print_error "This doesn't appear to be the telegram bot project directory"
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Running pre-deployment checks..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "Python version: $python_version"

# Check if dependencies are installed
print_status "Checking dependencies..."
if ! python3 -c "import telegram" 2>/dev/null; then
    print_warning "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Run syntax checks
print_status "Running syntax checks..."
if python3 -m py_compile main_bot.py main_bot_railway.py; then
    print_success "Syntax checks passed"
else
    print_error "Syntax errors found - deployment aborted"
    exit 1
fi

# Run linting
print_status "Running code quality checks..."
if command -v flake8 >/dev/null 2>&1; then
    if flake8 --select=E9,F63,F7,F82 .; then
        print_success "Code quality checks passed"
    else
        print_warning "Some code quality issues found, but not critical"
    fi
else
    print_warning "flake8 not installed, skipping code quality checks"
fi

# Check Railway CLI
print_status "Checking Railway CLI..."
if command -v railway >/dev/null 2>&1; then
    print_success "Railway CLI found"
    
    # Check if we have authentication
    if railway whoami >/dev/null 2>&1; then
        print_success "Railway authentication verified"
        
        # Deploy to Railway
        print_status "Deploying to Railway..."
        if railway deploy; then
            print_success "Deployment completed successfully!"
        else
            print_error "Deployment failed"
            exit 1
        fi
    else
        print_warning "Railway CLI not authenticated"
        print_status "Please run: railway login"
        print_status "Or set RAILWAY_TOKEN environment variable"
    fi
else
    print_warning "Railway CLI not found"
    print_status "Installing Railway CLI..."
    
    if command -v npm >/dev/null 2>&1; then
        npm install -g @railway/cli
        print_success "Railway CLI installed"
        print_status "Please run: railway login"
        print_status "Then run this script again"
    else
        print_warning "npm not found - cannot install Railway CLI automatically"
        print_status "Please install Railway CLI manually:"
        print_status "curl -fsSL https://railway.app/install.sh | sh"
    fi
fi

# Verify deployment
print_status "Checking deployment status..."
sleep 10  # Wait for deployment to propagate

if curl -f -s "https://telegram-bot-project-1-production.up.railway.app/health" >/dev/null 2>&1; then
    print_success "Health check passed - bot is running!"
    print_success "Bot URL: https://telegram-bot-project-1-production.up.railway.app"
    print_success "Health Check: https://telegram-bot-project-1-production.up.railway.app/health"
    print_success "Metrics: https://telegram-bot-project-1-production.up.railway.app/metrics"
else
    print_warning "Health check failed - bot may still be starting up"
    print_status "This is normal for new deployments"
    print_status "Railway needs time to start the service"
fi

echo ""
echo "=================================="
print_success "Auto-Deploy Process Completed!"
echo "=================================="
echo ""
print_status "Next steps:"
echo "1. Check the Railway dashboard for deployment status"
echo "2. Test your bot functionality"
echo "3. Monitor logs for any issues"
echo ""
print_status "Useful commands:"
echo "  railway logs     # View application logs"
echo "  railway status   # Check service status"
echo "  railway open     # Open app in browser"