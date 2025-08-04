# Telegram Bot Project

A comprehensive Telegram bot built with Python and the python-telegram-bot library. This bot features a modular architecture with organized handlers, interactive keyboards, reaction systems, and administrative capabilities.

## 🚀 Features

- **Modular Architecture**: Well-organized handlers and utilities
- **Interactive Keyboards**: Inline keyboards for better user experience
- **Reaction System**: Users can react to posts with emojis
- **Admin Panel**: Administrative commands and controls
- **Content Management**: Support for various content types (text, images, documents)
- **Statistics**: Built-in analytics and user statistics
- **Multilingual Support**: Localization system for international users
- **Railway Deployment**: Optimized for Railway cloud platform

## 📁 Project Structure

```
telegram-bot-project-1/
├── handlers/                    # Command handlers (modular structure)
│   ├── admin.py                # Administrative commands
│   ├── user_commands.py        # User interaction commands
│   ├── content_commands.py     # Content management
│   ├── reactions.py            # Reaction system
│   ├── stats.py                # Statistics and analytics
│   └── diagnostics.py          # System diagnostics
├── utils/                      # Utility functions
│   ├── keyboards.py            # Keyboard creation utilities
│   ├── database.py             # Database operations
│   ├── localization.py         # Language support
│   └── exceptions.py           # Custom exceptions
├── tests/                      # Test suite
│   ├── handlers/               # Handler tests
│   └── utils/                  # Utility tests
├── locales/                    # Language files
├── config.py                   # Configuration management
├── main_bot.py                 # Main bot entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── Procfile                    # Railway deployment config
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/barkoszloy-afk/telegram-bot-project-1.git
   cd telegram-bot-project-1
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your values:
   # BOT_TOKEN=your_telegram_bot_token
   # ADMIN_ID=your_telegram_user_id
   ```

4. **Run the bot:**
   ```bash
   python main_bot.py
   ```

## ⚙️ Configuration

Edit the `.env` file with your configuration:

```env
# Telegram Bot Token from @BotFather
BOT_TOKEN=your_bot_token_here

# Your Telegram ID (get from @userinfobot)
ADMIN_ID=your_telegram_id_here

# Optional: Channel ID for posting
CHANNEL_ID=@your_channel_username

# Optional: Port for webhook (Railway deployment)
PORT=8000
```

## 🚀 Deployment

### Railway Deployment
This project is optimized for [Railway](https://railway.app/) deployment:

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically with each push

### Docker Deployment
```bash
docker build -t telegram-bot .
docker run -d --env-file .env telegram-bot
```

## 📋 Available Commands

### User Commands
- `/start` - Welcome message and bot introduction
- `/help` - Detailed help and command list
- `/about` - Information about the bot
- `/profile` - User profile and statistics
- `/feedback` - Submit feedback and suggestions
- `/settings` - User preferences and settings

### Admin Commands (Admin only)
- `/admin` - Administrative panel
- `/stats` - Bot usage statistics
- `/logs` - View recent bot logs
- `/broadcast` - Send message to all users
- `/users` - List registered users

### Content Commands
- `/post` - Create and publish posts
- `/categories` - Browse content categories
- `/random` - Get random content
- `/popular` - Most popular posts
- `/recent` - Latest posts

### System Commands
- `/ping` - Check bot responsiveness
- `/status` - System status information
- `/uptime` - Bot uptime statistics
- `/health` - Health check endpoint

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific test categories:
```bash
python -m pytest tests/handlers/
python -m pytest tests/utils/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- Create an [issue](https://github.com/barkoszloy-afk/telegram-bot-project-1/issues) for bug reports
- Use `/feedback` command in the bot for suggestions
- Check the [documentation](docs/) for detailed guides

## 🔧 Technology Stack

- **Python 3.11+**
- **python-telegram-bot** - Telegram Bot API wrapper
- **python-dotenv** - Environment variable management
- **psutil** - System monitoring
- **Railway** - Cloud deployment platform