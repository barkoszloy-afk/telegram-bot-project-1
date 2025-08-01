const commands = {
    start: (ctx) => {
        ctx.reply('Welcome to the bot! Use /help to see available commands.');
    },
    help: (ctx) => {
        ctx.reply('Available commands:\n/start - Start the bot\n/help - Show this help message');
    },
    echo: (ctx) => {
        ctx.reply(ctx.message.text);
    },
    // Add more command functions as needed
};

module.exports = commands;