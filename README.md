# MewFi Bot
A Telegram bot for XRPL insights, powered by a dynamic CSV command system and Python.

## Overview
MewFi Bot delivers real-time XRP prices, wallet info, DEX tools, airdrop alerts, and more via Telegram. It uses polling with `python-telegram-bot` and a CSV file (`commands.csv`) to manage commands dynamically.

## Features
- **Live XRP Price**: Fetch prices via CoinMarketCap API.
- **DEXs & Wallets**: Explore Sologenic, Magnetic, Xaman, and more.
- **Inline Menus**: Navigate via buttons, no typing needed.
- **Context-Aware**: Different responses for private chats vs. groups.

## Setup
1. Clone this repo: `git clone https://github.com/yourusername/mewfibot.git`
2. Install dependencies: `pip install python-telegram-bot pandas requests`
3. Add your bot token to `bot.py`.
4. Run: `python bot.py`

## Files
- `commands.csv`: Command definitions.
- `bot.py`: Main bot script.

## License
MIT License
