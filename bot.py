import os
import logging
import pandas as pd
import requests
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 📌 Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# 📌 Load bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN not set in environment variables!")
    raise ValueError("BOT_TOKEN environment variable is required")

# 📌 Load commands from CSV
commands = pd.read_csv("commands.csv")

# 📌 Fetch XRP Price from CMC (fallback: CoinGecko)
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
                    "success": True,
                    "prices": {
                        "XRP": {"price": data["XRP"]["quote"]["USD"]["price"], "change": data["XRP"]["quote"]["USD"]["percent_change_24h"]},
                        "BTC": {"price": data["BTC"]["quote"]["USD"]["price"], "change": data["BTC"]["quote"]["USD"]["percent_change_24h"]},
                        "ETH": {"price": data["ETH"]["quote"]["USD"]["price"], "change": data["ETH"]["quote"]["USD"]["percent_change_24h"]},
                    },
                }
            logger.warning(f"CMC API error: {response.status_code}")
        except Exception as e:
            logger.error(f"CMC API error: {str(e)}")

    # Fallback to CoinGecko
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ripple,bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "prices": {
                    "XRP": {"price": data["ripple"]["usd"], "change": data["ripple"]["usd_24h_change"]},
                    "BTC": {"price": data["bitcoin"]["usd"], "change": data["bitcoin"]["usd_24h_change"]},
                    "ETH": {"price": data["ethereum"]["usd"], "change": data["ethereum"]["usd_24h_change"]},
                },
            }
        logger.warning(f"CoinGecko API error: {response.status_code}")
    except Exception as e:
        logger.error(f"CoinGecko API error: {str(e)}")

    return {"success": False, "error": "API fetch failed"}

# 📌 Format price message
def format_price_message(price_data, source="CoinGecko"):
    if not price_data["success"]:
        return "❌ Sorry, couldn't fetch prices right now. Try again later!"
    prices = price_data["prices"]
    return (
        "💰 *Cryptocurrency Prices*\n\n"
        f"💎 XRP: ${prices['XRP']['price']:,.2f} ({'🟢' if prices['XRP']['change'] > 0 else '🔴'} {prices['XRP']['change']:.2f}%)\n"
        f"🟡 BTC: ${prices['BTC']['price']:,.2f} ({'🟢' if prices['BTC']['change'] > 0 else '🔴'} {prices['BTC']['change']:.2f}%)\n"
        f"🟣 ETH: ${prices['ETH']['price']:,.2f} ({'🟢' if prices['ETH']['change'] > 0 else '🔴'} {prices['ETH']['change']:.2f}%)\n\n"
        f"🔗 Powered by {source}"
    )

# 📌 Start Command
async def start(update, context):
    chat_type = update.message.chat.type
    context_filter = "private" if chat_type == "private" else "group"

    command = update.message.text.split("@")[0].split()[0][1:]  # Extract command
    logger.info(f"Command invoked: /{command}, Chat Type: {chat_type}")

    command_entry = commands[(commands["Command"] == f"/{command}") & (commands["Context"] == context_filter)]
    if not command_entry.empty:
        description = command_entry.iloc[0]["Description"].replace("\\n", "\n")
    else:
        description = "🐱 *Welcome to MewFi Bot!* 🐱\n\nUse the commands to explore!"

    await update.message.reply_text(description, parse_mode="Markdown")

# 📌 Handle XRP Price Command
async def pricexrp(update, context):
    price_data = fetch_xrp_price()
    source = "CoinMarketCap" if os.getenv("CMC_API_KEY") else "CoinGecko"
    response = format_price_message(price_data, source)
    await update.message.reply_text(response, parse_mode="Markdown")

# 📌 Callback Query Handler
async def button(update, context):
    query = update.callback_query
    cmd = query.data
    logger.info(f"Button clicked: {cmd}")

    row = commands[commands["Command"] == cmd]
    if not row.empty:
        description = row.iloc[0]["Description"].replace("\\n", "\n")
        await query.edit_message_text(description, parse_mode="Markdown")
    else:
        await query.edit_message_text(f"Command {cmd} not found in CSV", parse_mode="Markdown")

    await query.answer()

# 📌 Register Handlers & Start Bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pricexrp", pricexrp))
app.add_handler(CommandHandler("wallets", start))
app.add_handler(CommandHandler("dexs", start))
app.add_handler(CommandHandler("cexs", start))
app.add_handler(CommandHandler("xrpltools", start))
app.add_handler(CommandHandler("airdrops", start))
app.add_handler(CommandHandler("nfts", start))
app.add_handler(CommandHandler("buy_meowrp", start))
app.add_handler(CommandHandler("antirug_scan", start))
app.add_handler(CommandHandler("merch", start))
app.add_handler(CommandHandler("terminology", start))
app.add_handler(CommandHandler("influencers", start))
app.add_handler(CommandHandler("help", start))
app.add_handler(CallbackQueryHandler(button))
app.run_polling()
