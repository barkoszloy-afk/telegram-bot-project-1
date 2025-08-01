const formatMessage = (message) => {
    return message.trim().charAt(0).toUpperCase() + message.slice(1);
};

const validateUserInput = (input) => {
    return input && input.length > 0;
};

const logError = (error) => {
    console.error('Error:', error);
};

module.exports = {
    formatMessage,
    validateUserInput,
    logError,
};