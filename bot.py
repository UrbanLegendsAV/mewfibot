import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd

# Load bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables. Please set it!")

# Load CSV
commands = pd.read_csv('commands.csv')

# Start command with main menu
def start(update, context):
    main_items = commands[commands['Menu Level'] == 'main']
    keyboard = [
        [InlineKeyboardButton(row['Main Category'], callback_data=row['Command'])]
        for _, row in main_items.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to MewFi! Pick a category:", reply_markup=reply_markup)

# Handle button clicks
def button(update, context):
    query = update.callback_query
    cmd = query.data
    row = commands[commands['Command'] == cmd].iloc[0]
    
    if row['Menu Level'] == 'main':
        sub_items = commands[(commands['Main Category'] == row['Main Category']) & (commands['Menu Level'] == 'submenu')]
        if not sub_items.empty:
            keyboard = [
                [InlineKeyboardButton(row['Submenu Item'], callback_data=row['Command'])]
                for _, row in sub_items.iterrows()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(row['Description'], reply_markup=reply_markup)
        else:
            query.edit_message_text(row['Description'])
    else:
        query.edit_message_text(row['Description'])

# Command handler for /pricexrp (example)
def pricexrp(update, context):
    desc = commands[commands['Command'] == '/pricexrp']['Description'].iloc[0]
    update.message.reply_text(desc)  # Add CoinMarketCap API call later

# Setup bot
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("pricexrp", pricexrp))
dp.add_handler(CallbackQueryHandler(button))
updater.start_polling()
updater.idle()
