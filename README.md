# MewFi Bot
A Telegram bot for XRPL insights, powered by a dynamic CSV command system, Python, and Fine.dev AI agents.

## Overview
MewFi Bot delivers real-time cryptocurrency prices, wallet info, DEX tools, airdrop alerts, and more via Telegram. It uses polling with `python-telegram-bot` and a CSV file (`commands.csv`) to dynamically manage commands, with Fine.dev automating development tasks via GitHub PRs. Designed for both private chats and group interactions, it offers a seamless, cat-themed UX for XRPL enthusiasts.

## Features
- **Live Crypto Prices**: Displays XRP, BTC, ETH prices with 24h changes via `/pricexrp` (powered by CoinGecko; CoinMarketCap integration planned).
- **DEXs & Wallets**: Explore Sologenic, Magnetic, Xaman, and more through detailed menus.
- **Interactive Menus**: Navigate with inline keyboards in private chats and groups—no typing needed for most actions.
- **Context-Aware**: Tailored responses for private chats (e.g., `/start`) vs. groups (e.g., `/start@MewFiBot`), driven by `commands.csv`’s `Context` column.
- **Fine.dev Integration**: AI agents enhance development by generating code and PRs directly on GitHub.
- **Media Support**: Includes tutorial videos and GIFs (`help.gif`, `start.gif`) for user guidance.

## Setup
1. Clone this repo: `git clone https://github.com/UrbanLegendsAV/mewfibot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Telegram bot token:
