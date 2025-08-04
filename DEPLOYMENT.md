# 🚀 Deployment Guide - Telegram Bot Project

This guide covers deployment options for the Telegram Bot Project on various platforms.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
2. **Admin User ID** (get from [@userinfobot](https://t.me/userinfobot))
3. **Channel ID** (optional, for posting features)

## 🛠️ Environment Variables

Set these environment variables in your deployment platform:

```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id_here
CHANNEL_ID=@your_channel_username  # Optional
PORT=8000  # For Railway/Heroku
ENVIRONMENT=production
```

## 🚂 Railway Deployment (Recommended)

Railway provides the easiest deployment experience:

### 1. Connect Repository
1. Go to [Railway](https://railway.app/)
2. Create new project from GitHub repository
3. Connect your forked repository

### 2. Configure Environment
1. Go to your project dashboard
2. Click on "Variables" tab
3. Add the required environment variables:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `CHANNEL_ID` (optional)

### 3. Deploy
- Railway automatically detects the Python project
- Uses `Procfile` for deployment commands
- Deployment happens automatically on git push

### 4. Custom Domain (Optional)
1. Go to "Settings" > "Domains"
2. Generate a Railway domain or add custom domain
3. Update webhook URL if using webhooks

## 🐳 Docker Deployment

### Local Docker
```bash
# Build the image
docker build -t telegram-bot .

# Run with environment variables
docker run -d \
  --name telegram-bot \
  -e BOT_TOKEN=your_token \
  -e ADMIN_ID=your_id \
  -e CHANNEL_ID=@your_channel \
  -p 8000:8000 \
  telegram-bot
```

### Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  telegram-bot:
    build: .
    environment:
      - BOT_TOKEN=your_token
      - ADMIN_ID=your_id
      - CHANNEL_ID=@your_channel
      - PORT=8000
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      - ./data:/app/data
```

Run: `docker-compose up -d`

## ☁️ Heroku Deployment

### 1. Install Heroku CLI
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

### 2. Create Heroku App
```bash
# Create new app
heroku create your-bot-name

# Set environment variables
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_ID=your_id
heroku config:set CHANNEL_ID=@your_channel
```

### 3. Deploy
```bash
# Deploy to Heroku
git push heroku main

# View logs
heroku logs --tail
```

## 🌐 VPS Deployment

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone https://github.com/your-username/telegram-bot-project-1.git
cd telegram-bot-project-1
```

### 2. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your values
nano .env
```

### 3. Service Setup (systemd)
Create `/etc/systemd/system/telegram-bot.service`:
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-bot-project-1
Environment=PATH=/home/ubuntu/telegram-bot-project-1/venv/bin
ExecStart=/home/ubuntu/telegram-bot-project-1/venv/bin/python main_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

## 🔍 Monitoring & Debugging

### Health Checks
- **Local**: `http://localhost:8000/health`
- **Railway**: `https://your-app.railway.app/health`
- **Heroku**: `https://your-app.herokuapp.com/health`

### Bot Commands for Monitoring
- `/ping` - Check bot responsiveness
- `/status` - System status (admin only)
- `/uptime` - Bot uptime
- `/health` - Health check (admin only)
- `/logs` - View recent logs (admin only)

### Log Files
- Application logs: `bot.log`
- Reaction data: `reactions_data.json`
- Bot statistics: `bot_stats.json`

## 🚨 Troubleshooting

### Common Issues

1. **Bot Token Invalid**
   ```
   Error: Bot token is invalid
   Solution: Verify BOT_TOKEN in environment variables
   ```

2. **Permission Denied**
   ```
   Error: Admin access required
   Solution: Check ADMIN_ID matches your Telegram user ID
   ```

3. **Import Errors**
   ```
   Error: ModuleNotFoundError
   Solution: Ensure all dependencies are installed
   ```

4. **Railway Build Fails**
   ```
   Error: Build failed
   Solution: Check Procfile and requirements.txt are correct
   ```

### Debug Mode
Add to environment variables for detailed logging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🔄 Updates & Maintenance

### Updating the Bot
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart telegram-bot  # VPS
# or redeploy on Railway/Heroku
```

### Database Maintenance
- Use `/cleanup` command to clean old data
- Backup `reactions_data.json` and `bot_stats.json` regularly

### Performance Monitoring
- Monitor memory usage with `/status`
- Check active users with `/stats`
- Review logs with `/logs`

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs for error messages
3. Use bot diagnostic commands
4. Create an issue in the GitHub repository

---

**Happy Deploying! 🚀**