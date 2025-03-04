MewFi Bot
A Telegram bot for XRPL insights, powered by a dynamic CSV command system, Python, and Fine.dev AI agents. Chat with me at [@MewFiBot](https://t.me/MewFiBot)!

Overview
MewFi Bot delivers real-time cryptocurrency prices, wallet info, DEX tools, airdrop alerts, and more via Telegram. It uses polling with python-telegram-bot and a CSV file (commands.csv) to dynamically manage commands. Designed for both private chats and group interactions, it offers a seamless, cat-themed UX for XRPL enthusiasts.

Features
- Live Crypto Prices: Displays XRP, BTC, ETH prices with 24h changes via /pricexrp (powered by CoinMarketCap and CoinGecko).
- DEXs & Wallets: Explore Sologenic, Magnetic, Xaman, and more through detailed menus.
- Interactive Menus: Navigate with inline keyboards in private chats and groups—no typing needed for most actions.
- Context-Aware: Tailored responses for private chats (e.g., /start) vs. groups (e.g., /start@MewFiBot), driven by commands.csv’s Context column.
- Fine.dev Integration: Planned AI agent support to enhance development by generating code and PRs on GitHub.
- Media Support: Includes tutorial videos and GIFs (help.gif, start.gif) for user guidance.

Setup
1. Clone this repo: `git clone https://github.com/UrbanLegendsAV/mewfibot.git`
2. Navigate to the project directory: `cd mewfibot`
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables:
   - For local runs, create a `.env` file and add:
     ```
     BOT_TOKEN=your_telegram_bot_token
     CMC_API_KEY=your_coinmarketcap_api_key
     ```
   - For Heroku deployment, set variables with:
     ```
     heroku config:set BOT_TOKEN=your_telegram_bot_token --app mewfibot
     heroku config:set CMC_API_KEY=your_coinmarketcap_api_key --app mewfibot
     ```
5. Deploy to Heroku (optional):
   - Create a Heroku app: `heroku create mewfibot`
   - Push to Heroku: `git push heroku main`
   - Scale the worker: `heroku ps:scale worker=1 --app mewfibot`
6. Run locally (optional): `python bot.py`
