# MewFi Bot
A Telegram bot for XRPL insights, powered by a dynamic CSV command system and Python.

## Overview
MewFi Bot delivers real-time XRP prices, wallet info, DEX tools, airdrop alerts, and more via Telegram. It uses polling with `python-telegram-bot` and a CSV file (`commands.csv`) to manage commands dynamically.

## Features
- **Live XRP Price**: Fetch prices via CoinMarketCap API (coming soon).
- **DEXs & Wallets**: Explore Sologenic, Magnetic, Xaman, and more.
- **Inline Menus**: Navigate via buttons, no typing needed.
- **Context-Aware**: Different responses for private chats vs. groups.

## Setup
1. Clone this repo: `git clone https://github.com/UrbanLegendsAV/mewfibot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Telegram bot token:
4. Run the bot: `python bot.py`

## Files
- `.gitignore`: Ignores Python junk files.
- `LICENSE`: MIT License.
- `README.md`: This file.
- `IMPLEMENTATION_PLAN.md`: Development roadmap.
- `bot.py`: Main bot script.
- `commands.csv`: Command definitions.
- `requirements.txt`: Dependencies.
- `assets/`: Tutorial videos and GIFs.

## License
MIT License
