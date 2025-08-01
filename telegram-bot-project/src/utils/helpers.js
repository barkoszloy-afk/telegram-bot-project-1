function formatMessage(text) {
    return text.trim().replace(/\s+/g, ' ');
}

function validateInput(input, type) {
    switch (type) {
        case 'text':
            return typeof input === 'string' && input.length > 0;
        case 'number':
            return !isNaN(input);
        default:
            return false;
    }
}

function sendResponse(chatId, message, bot) {
    bot.sendMessage(chatId, formatMessage(message));
}

export { formatMessage, validateInput, sendResponse };