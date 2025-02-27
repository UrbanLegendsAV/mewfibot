import os
import logging
import pandas as pd
import requests
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Load bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set in environment variables!")
    raise ValueError("BOT_TOKEN environment variable is required")

# Load commands from CSV
commands = pd.read_csv('commands.csv')

# Utility function to fetch XRP price from CoinMarketCap (or CoinGecko as fallback)
def fetch_xrp_price():
    CMC_API_KEY = os.getenv("CMC_API_KEY")
    if CMC_API_KEY:
        try:
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
            params = {"symbol": "XRP,BTC,ETH", "convert": "USD"}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()["data"]
                return {
                    'success': True,
                    'prices': {
                        'XRP': {'price': data['XRP']['quote']['USD']['price'], 'change': data['XRP']['quote']['USD']['percent_change_24h']},
                        'BTC': {'price': data['BTC']['quote']['USD']['price'], 'change': data['BTC']['quote']['USD']['percent_change_24h']},
                        'ETH': {'price': data['ETH']['quote']['USD']['price'], 'change': data['ETH']['quote']['USD']['percent_change_24h']}
                    }
                }
            logger.warning(f"CMC API error: {response.status_code}")
        except Exception as e:
            logger.error(f"CMC error: {str(e)}")
    # Fallback to CoinGecko
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ripple,bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true')
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'prices': {
                    'XRP': {'price': data['ripple']['usd'], 'change': data['ripple']['usd_24h_change']},
                    'BTC': {'price': data['bitcoin']['usd'], 'change': data['bitcoin']['usd_24h_change']},
                    'ETH': {'price': data['ethereum']['usd'], 'change': data['ethereum']['usd_24h_change']}
                }
            }
        logger.warning(f"CoinGecko API error: {response.status_code}")
        return {'success': False, 'error': 'API fetch failed'}
    except Exception as e:
        logger.error(f"CoinGecko error: {str(e)}")
        return {'success': False, 'error': str(e)}

# Format price message with dynamic source
def format_price_message(price_data, source="CoinGecko"):
    if not price_data['success']:
        return "Sorry, couldn't fetch prices right now. Try again later!"
    prices = price_data['prices']
    from datetime import datetime
    utc_time = datetime.utcnow().strftime('%H:%M:%S UTC')
    return (
        "💰 *Cryptocurrency Prices*\n\n"
        f"💎 XRP: ${prices['XRP']['price']:,.2f} ({'🟢' if prices['XRP']['change'] > 0 else '🔴'} {prices['XRP']['change']:.2f}%)\n"
        f"🟡 BTC: ${prices['BTC']['price']:,.2f} ({'🟢' if prices['BTC']['change'] > 0 else '🔴'} {prices['BTC']['change']:.2f}%)\n"
        f"🟣 ETH: ${prices['ETH']['price']:,.2f} ({'🟢' if prices['ETH']['change'] > 0 else '🔴'} {prices['ETH']['change']:.2f}%)\n\n"
        f"Updated: {utc_time}\nPowered by {source} 📊"
    )

# Start command with main menu
def start(update, context):
    main_items = commands[commands['Menu Level'] == 'main']
    keyboard = [
        [InlineKeyboardButton(row['Main Category'], callback_data=row['Command'])]
        for _, row in main_items.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🐱 *Welcome to MewFi Bot!* 🐱\n\nUse the menu below to navigate.", 
                             reply_markup=reply_markup, parse_mode='Markdown')

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
            keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(f"*{row['Main Category']}*\nSelect an option below:", 
                                  reply_markup=reply_markup, parse_mode='Markdown')
        else:
            query.edit_message_text(row['Description'], parse_mode='Markdown')
    else:
        query.edit_message_text(row['Description'], parse_mode='Markdown')
    query.answer()

# Command handler for /pricexrp
def pricexrp(update, context):
    price_data = fetch_xrp_price()
    source = "CoinMarketCap" if os.getenv("CMC_API_KEY") and price_data.get('success') else "CoinGecko"
    response = format_price_message(price_data, source)
    update.message.reply_text(response, parse_mode='Markdown')

# Setup bot
updater = Updater(BOT_TOKEN)  # Fixed: Removed use_context=True
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("pricexrp", pricexrp))
dp.add_handler(CallbackQueryHandler(button))
updater.start_polling()
updater.idle()
