import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError('BOT_TOKEN environment variable is required')

COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
if not COINMARKETCAP_API_KEY:
    raise ValueError('COINMARKETCAP_API_KEY environment variable is required')

# API Endpoints
COINMARKETCAP_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

# Command Settings
COMMANDS_FILE = 'commands.csv'

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'mewfi_bot.log'

# Error Messages
ERROR_MESSAGES = {
    'api_error': '😿 Oops! Having trouble fetching prices. Please try again later!',
    'command_error': '😿 Command not found! Try /help for available commands.',
    'general_error': '😿 Something went wrong! Please try again.',
    'group_only': '😿 This command only works in groups!',
    'private_only': '😿 This command only works in private chats!'
}