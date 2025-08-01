const TelegramBot = require('node-telegram-bot-api');
const { handleCommand } = require('./commands/index');
const { logMessage } = require('./utils/helpers');

const token = 'YOUR_TELEGRAM_BOT_TOKEN'; // Replace with your bot's token
const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, 'Welcome to the bot! Type /help to see available commands.');
});

bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    logMessage(msg); // Log the incoming message
    handleCommand(msg.text, chatId); // Handle the command
});

bot.on('polling_error', (error) => {
    console.error(`Polling error: ${error.code}`);
});