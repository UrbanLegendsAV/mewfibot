import os
import logging
import pandas as pd
import requests
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
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
async def start(update, context):
    chat_type = update.message.chat.type
    context_filter = 'private' if chat_type == 'private' else 'group'
    
    # Determine the command being handled
    command = update.message.text.split('@')[0].split()[0][1:]  # Extracts the command (e.g., 'help' from '/help@MewFiBot')
    logger.info(f"Command invoked: /{command}, Chat Type: {chat_type}, Context Filter: {context_filter}")
    
    command_entry = commands[(commands['Command'] == f'/{command}') & (commands['Context'] == context_filter)]
    
    if not command_entry.empty:
        description = command_entry.iloc[0]['Description'].replace('\\n', '\n')
        # Special case for /help in group chat: append a list of all commands
        if command == 'help' and context_filter == 'group':
            all_commands = commands[commands['Menu Level'] == 'main']
            description += "\n\n📋 *Available Commands:*\n"
            for _, row in all_commands.iterrows():
                if row['Context'] == 'group':
                    description += f"- {row['Command']}@MewFiBot: {row['Main Category']}\n"
                else:
                    description += f"- {row['Command']}: {row['Main Category']}\n"
    else:
        description = "🐱 *Welcome to MewFi Bot!* 🐱\n\nUse the menu below to navigate."
    
    main_items = commands[(commands['Menu Level'] == 'main') & (commands['Context'] == context_filter)]
    keyboard = [
        [InlineKeyboardButton(row['Main Category'], callback_data=row['Command'])]
        for _, row in main_items.iterrows()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send start.gif before the menu, with error handling
    try:
        with open('start.gif', 'rb') as gif:
            await update.message.reply_animation(gif)
    except Exception as e:
        logger.error(f"Failed to send start.gif: {str(e)}")
    await update.message.reply_text(description, reply_markup=reply_markup, parse_mode='Markdown')

# Handle button clicks
async def button(update, context):
    query = update.callback_query
    cmd = query.data
    logger.info(f"Button clicked with callback data: {cmd}")  # Log the callback data
    
    chat_type = query.message.chat.type
    context_filter = 'private' if chat_type == 'private' else 'group'
    
    if cmd == "back_to_main":
        # Rebuild the main menu with context filter
        main_items = commands[(commands['Menu Level'] == 'main') & (commands['Context'] == context_filter)]
        keyboard = [
            [InlineKeyboardButton(row['Main Category'], callback_data=row['Command'])]
            for _, row in main_items.iterrows()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🐱 *Welcome to MewFi Bot!* 🐱\n\nUse the menu below to navigate.", 
                                      reply_markup=reply_markup, parse_mode='Markdown')
    elif cmd == "/pricexrp":
        # Call the pricexrp() function directly
        price_data = fetch_xrp_price()
        source = "CoinMarketCap" if os.getenv("CMC_API_KEY") and price_data.get('success') else "CoinGecko"
        response = format_price_message(price_data, source)
        await query.edit_message_text(response, parse_mode='Markdown')
    else:
        row = commands[commands['Command'] == cmd]
        if not row.empty:
            row = row.iloc[0]
            if row['Menu Level'] == 'main':
                sub_items = commands[(commands['Main Category'] == row['Main Category']) & (commands['Menu Level'] == 'submenu') & (commands['Context'] == context_filter)]
                if not sub_items.empty:
                    keyboard = [
                        [InlineKeyboardButton(row['Submenu Item'], callback_data=row['Command'])]
                        for _, row in sub_items.iterrows()
                    ]
                    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(f"*{row['Main Category']}*\nSelect an option below:", 
                                                 reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    description = row['Description'].replace('\\n', '\n')
                    await query.edit_message_text(description, parse_mode='Markdown')
            else:
                logger.info(f"Displaying description for command: {cmd}, Description: {row['Description']}")
                description = row['Description'].replace('\\n', '\n')
                await query.edit_message_text(description, parse_mode='Markdown')
        else:
            await query.edit_message_text(f"Command {cmd} not found in commands.csv", parse_mode='Markdown')
    await query.answer()

# Command handler for /pricexrp
async def pricexrp(update, context):
    chat_type = update.message.chat.type
    context_filter = 'private' if chat_type == 'private' else 'group'
    command_entry = commands[(commands['Command'] == '/pricexrp') & (commands['Context'] == context_filter)]
    
    price_data = fetch_xrp_price()
    source = "CoinMarketCap" if os.getenv("CMC_API_KEY") and price_data.get('success') else "CoinGecko"
    response = format_price_message(price_data, source)
    await update.message.reply_text(response, parse_mode='Markdown')

# Setup bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pricexrp", pricexrp))
app.add_handler(CommandHandler("wallets", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("dexs", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("cexs", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("xrpltools", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("airdrops", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("nfts", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("buy_meowrp", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("antirug_scan", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("merch", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("terminology", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("influencers", lambda update, context: start(update, context)))
app.add_handler(CommandHandler("help", lambda update, context: start(update, context)))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
