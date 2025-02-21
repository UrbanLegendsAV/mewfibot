import pandas as pd
import logging
from config import COMMANDS_FILE, ERROR_MESSAGES
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from api_client import get_xrp_price

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self):
        self.commands = self._load_commands()
        
    def _load_commands(self):
        """Load commands from CSV file"""
        try:
            return pd.read_csv(COMMANDS_FILE)
        except Exception as e:
            logger.error(f'Error loading commands: {str(e)}')
            return pd.DataFrame()
    
    def get_main_menu_keyboard(self):
        """Generate main menu keyboard"""
        try:
            main_items = self.commands[self.commands['Menu Level'] == 'main']
            keyboard = [
                [InlineKeyboardButton(row['Main Category'], callback_data=row['Command'])]
                for _, row in main_items.iterrows()
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            logger.error(f'Error creating main menu: {str(e)}')
            return None
    
    def get_submenu_keyboard(self, main_category):
        """Generate submenu keyboard for a category"""
        try:
            sub_items = self.commands[
                (self.commands['Main Category'] == main_category) & 
                (self.commands['Menu Level'] == 'submenu')
            ]
            if sub_items.empty:
                return None
                
            keyboard = [
                [InlineKeyboardButton(row['Submenu Item'], callback_data=row['Command'])]
                for _, row in sub_items.iterrows()
            ]
            return InlineKeyboardMarkup(keyboard)
        except Exception as e:
            logger.error(f'Error creating submenu: {str(e)}')
            return None
    
    def get_command_response(self, command, context='private'):
        """Get response for a command"""
        try:
            row = self.commands[
                (self.commands['Command'] == command) & 
                (self.commands['Context'] == context)
            ].iloc[0]
            
            # Special handling for price command
            if command == '/pricexrp':
                return self._handle_price_command(row)
                
            return row['Description']
        except Exception as e:
            logger.error(f'Error getting command response: {str(e)}')
            return ERROR_MESSAGES['command_error']
    
    def _handle_price_command(self, row):
        """Handle /pricexrp command with live data"""
        price_data = get_xrp_price()
        if not price_data:
            return ERROR_MESSAGES['api_error']
            
        return f"🐱 Current XRP Price: ${price_data['price']:,.4f}\\n" \
               f"24h Change: {price_data['change_24h']}%\\n\\n" \
               f"Powered by CoinMarketCap 📊"
