import os
import logging
import pandas as pd
import requests
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from datetime import datetime

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

# Load commands from CSV and strip whitespace from all string columns
commands = pd.read_csv('commands.csv')
commands = commands.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

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
    utc_time = datetime.utcnow().strftime('%H:%M:%S UTC')
    return (
        "💰 *Cryptocurrency Prices*\n\n"
        f"💎 XRP: ${prices['XRP']['price']:,.2f} ({'🟢' if prices['XRP']['change'] > 0 else '🔴'} {prices['XRP']['change']:.2f}%)\n"
        f"🟡 BTC: ${prices['BTC']['price']:,.2f} ({'🟢' if prices['BTC']['change'] > 0 else '🔴'} {prices['BTC']['change']:.2f}%)\n"
        f"🟣 ETH: ${prices['ETH']['price']:,.2f} ({'🟢' if prices['ETH']['change'] > 0 else '🔴'} {prices['ETH']['change']:.2f}%)\n\n"
        f"Updated: {utc_time}\nPowered by {source} 📊"
    )

# Utility function to split long messages into chunks
def split_message(text, max_length=4000):
    """Split a message into chunks of max_length characters, ensuring not to split in the middle of a word."""
    if len(text.encode('utf-8')) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        if len((current_chunk + line + '\n').encode('utf-8')) <= max_length:
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + '\n'
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

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
    
    # Handle the menu based on chat type
    main_items = commands[(commands['Menu Level'] == 'main') & (commands['Context'] == context_filter)]
    
    if chat_type == 'private':
        # Use ReplyKeyboardMarkup for private chats (DMs)
        keyboard = [
            [row['Main Category']] for _, row in main_items.iterrows()
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            one_time_keyboard=False  # Makes the keyboard persistent
        )
        # Send start.gif before the menu
        try:
            with open('start.gif', 'rb') as gif:
                await update.message.reply_animation(gif)
        except Exception as e:
            logger.error(f"Failed to send start.gif: {str(e)}")
        await update.message.reply_text(description, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        # Use InlineKeyboardMarkup for group chats
        keyboard = [
            [InlineKeyboardButton(row['Main Category'], callback_data=row['Command'])]
            for _, row in main_items.iterrows()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send start.gif before the menu
        try:
            with open('start.gif', 'rb') as gif:
                await update.message.reply_animation(gif)
        except Exception as e:
            logger.error(f"Failed to send start.gif: {str(e)}")
        await update.message.reply_text(description, reply_markup=reply_markup, parse_mode='Markdown')

# Generic handler for commands that should show a submenu (e.g., /xrpltools, /wallets, etc.)
async def show_submenu(update, context, command_name):
    chat_type = update.message.chat.type
    context_filter = 'private' if chat_type == 'private' else 'group'
    
    logger.info(f"Command invoked: /{command_name}, Chat Type: {chat_type}, Context Filter: {context_filter}")
    
    # Find the main category for this command
    command_entry = commands[(commands['Command'] == f'/{command_name}') & (commands['Context'] == context_filter)]
    if command_entry.empty:
        await update.message.reply_text(f"Command /{command_name} not found.", parse_mode='Markdown')
        return
    
    main_category = command_entry.iloc[0]['Main Category']
    
    # Fetch submenu items for this main category
    sub_items = commands[(commands['Main Category'] == main_category) & (commands['Menu Level'] == 'submenu') & (commands['Context'] == context_filter)]
    if sub_items.empty:
        description = command_entry.iloc[0]['Description'].replace('\\n', '\n')
        # Split the description if it's too long
        chunks = split_message(description)
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode='Markdown')
        return
    
    # Create inline menu for submenu items
    keyboard = [
        [InlineKeyboardButton(row['Submenu Item'], callback_data=row['Command'])]
        for _, row in sub_items.iterrows()
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"*{main_category}*\nSelect an option below:", reply_markup=reply_markup, parse_mode='Markdown')

# Handle button clicks (for InlineKeyboardMarkup)
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
        row = commands[(commands['Command'] == cmd) & (commands['Context'] == context_filter)]
        if not row.empty:
            row = row.iloc[0]
            if row['Menu Level'] == 'main':
                # Show submenu for this main category
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
                    # Split the description if it's too long
                    chunks = split_message(description)
                    await query.edit_message_text(chunks[0], parse_mode='Markdown')
                    for chunk in chunks[1:]:
                        await query.message.reply_text(chunk, parse_mode='Markdown')
            else:
                # Display the description for the submenu item
                description = row['Description'].replace('\\n', '\n')
                # Split the description if it's too long
                chunks = split_message(description)
                await query.edit_message_text(chunks[0], parse_mode='Markdown')
                for chunk in chunks[1:]:
                    await query.message.reply_text(chunk, parse_mode='Markdown')
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

# New MessageHandler to handle ReplyKeyboardMarkup button clicks in private chats
async def handle_reply_keyboard(update, context):
    chat_type = update.message.chat.type
    if chat_type != 'private':
        return  # Only handle ReplyKeyboardMarkup in private chats
    
    # Get the text from the button click (e.g., "Live XRP Price 📈") and strip whitespace
    button_text = update.message.text.strip()
    logger.info(f"ReplyKeyboardMarkup button clicked: {button_text}")
    
    # Look up the Main Category in commands.csv to find the corresponding Command
    command_entry = commands[(commands['Main Category'] == button_text) & (commands['Menu Level'] == 'main') & (commands['Context'] == 'private')]
    if command_entry.empty:
        await update.message.reply_text(f"Option {button_text} not found.", parse_mode='Markdown')
        return
    
    command = command_entry.iloc[0]['Command'].lstrip('/')  # Remove the leading '/' (e.g., 'pricexrp')
    
    # Call the appropriate handler based on the command
    if command == 'pricexrp':
        await pricexrp(update, context)
    elif command == 'start':
        await start(update, context)
    elif command == 'help':
        await start(update, context)  # /help uses the start handler
    else:
        # For all other commands, use show_submenu (e.g., /dexs, /wallets, etc.)
        await show_submenu(update, context, command)

# Setup bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pricexrp", pricexrp))
app.add_handler(CommandHandler("wallets", lambda update, context: show_submenu(update, context, "wallets")))
app.add_handler(CommandHandler("dexs", lambda update, context: show_submenu(update, context, "dexs")))
app.add_handler(CommandHandler("cexs", lambda update, context: show_submenu(update, context, "cexs")))
app.add_handler(CommandHandler("xrpltools", lambda update, context: show_submenu(update, context, "xrpltools")))
app.add_handler(CommandHandler("airdrops", lambda update, context: show_submenu(update, context, "airdrops")))
app.add_handler(CommandHandler("nfts", lambda update, context: show_submenu(update, context, "nfts")))
app.add_handler(CommandHandler("buy_meowrp", lambda update, context: show_submenu(update, context, "buy_meowrp")))
app.add_handler(CommandHandler("antirug_scan", lambda update, context: show_submenu(update, context, "antirug_scan")))
app.add_handler(CommandHandler("merch", lambda update, context: show_submenu(update, context, "merch")))
app.add_handler(CommandHandler("terminology", lambda update, context: show_submenu(update, context, "terminology")))
app.add_handler(CommandHandler("influencers", lambda update, context: show_submenu(update, context, "influencers")))
app.add_handler(CommandHandler("help", lambda update, context: start(update, context)))
app.add_handler(CallbackQueryHandler(button))
# Add the MessageHandler for ReplyKeyboardMarkup clicks
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_keyboard))
app.run_polling()
