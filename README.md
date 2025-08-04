# Telegram Bot Project

This project is a Telegram bot built using Python and the python-telegram-bot library. It serves as a channel publishing bot with admin panel, reactions system, and zodiac-themed posts.

## Features

- Admin panel with inline keyboard controls
- Post publishing to Telegram channels (text, photos, documents, videos)
- Zodiac signs integration with personalized messages  
- Reaction system for user engagement
- Content moderation with forbidden words filter
- Comprehensive logging system
- Reply keyboard navigation for admins

## Project Structure

```
telegram-bot-project-1/
├── main_bot.py          # Main bot application
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── handlers/           # Additional handlers (if any)
├── locales/            # Localization files
├── utils/              # Utility functions
└── tests/              # Test files
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd telegram-bot-project-1
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` file and add your bot token and admin ID:
   ```
   BOT_TOKEN=your_bot_token_from_botfather
   ADMIN_ID=your_telegram_user_id
   CHANNEL_ID=@your_channel_username
   ```

## Usage

To start the bot, run:
```bash
python main_bot.py
```

## Available Commands

- `/start` - Welcome message and command list
- `/help` - Detailed help information  
- `/post` - Start post publishing process (admin only)
- `/admin` - Access admin panel (admin only)
- `/commands` - Show all available commands
- `/cancel` - Cancel current operation

## Admin Features

- **Post Publishing**: Text, images, documents, and videos
- **Content Moderation**: Automatic filtering of forbidden words
- **Logs Access**: View bot operation logs
- **Statistics**: Basic usage statistics
- **Settings**: Bot configuration options

## Configuration

Key settings in `config.py`:
- `BOT_TOKEN`: Your Telegram bot token
- `ADMIN_ID`: Telegram user ID of the administrator
- `CHANNEL_ID`: Target channel for publishing posts
- `FORBIDDEN_WORDS`: List of words to filter from posts

## Contributing

Feel free to submit issues or pull requests to improve the bot's functionality or add new features.

## License

This project is open source and available under the MIT License.