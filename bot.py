import logging
from config import BOT_TOKEN, LOG_FORMAT, LOG_FILE, ERROR_MESSAGES
from telegram.ext import Updater, CommandHandler as TelegramCommandHandler, CallbackQueryHandler
from command_handler import CommandHandler

# Configure logging
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO,
                    handlers=[logging.FileHandler(LOG_FILE),
                             logging.StreamHandler()])
logger = logging.getLogger(__name__)

class MewFiBot:
    def __init__(self):
        self.command_handler = CommandHandler()
        
        # Initialize bot
        self.updater = Updater(BOT_TOKEN, use_context=True)
        self.dp = self.updater.dispatcher
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register command and callback handlers"""
        self.dp.add_handler(TelegramCommandHandler('start', self.start))
        self.dp.add_handler(TelegramCommandHandler('pricexrp', self.price_xrp))
        self.dp.add_handler(TelegramCommandHandler('help', self.help))
        self.dp.add_handler(CallbackQueryHandler(self.button))
        
        # Add error handler
        self.dp.add_error_handler(self.error_handler)
    
    def start(self, update, context):
        """Handle /start command"""
        try:
            chat_type = update.effective_chat.type
            context_type = 'private' if chat_type == 'private' else 'group'
            
            keyboard = self.command_handler.get_main_menu_keyboard()
            message = self.command_handler.get_command_response('/start', context_type)
            
            update.message.reply_text(message, reply_markup=keyboard)
        except Exception as e:
            logger.error(f'Error in start command: {str(e)}')
            update.message.reply_text(ERROR_MESSAGES['general_error'])
    
    def price_xrp(self, update, context):
        """Handle /pricexrp command"""
        try:
            message = self.command_handler.get_command_response('/pricexrp')
            update.message.reply_text(message)
        except Exception as e:
            logger.error(f'Error in price command: {str(e)}')
            update.message.reply_text(ERROR_MESSAGES['general_error'])
    
    def help(self, update, context):
        """Handle /help command"""
        try:
            chat_type = update.effective_chat.type
            context_type = 'private' if chat_type == 'private' else 'group'
            
            message = self.command_handler.get_command_response('/help', context_type)
            keyboard = self.command_handler.get_main_menu_keyboard()
            
            update.message.reply_text(message, reply_markup=keyboard)
        except Exception as e:
            logger.error(f'Error in help command: {str(e)}')
            update.message.reply_text(ERROR_MESSAGES['general_error'])
    
    def button(self, update, context):
        """Handle button callbacks"""
        try:
            query = update.callback_query
            chat_type = query.message.chat.type
            context_type = 'private' if chat_type == 'private' else 'group'
            
            cmd = query.data
            row = self.command_handler.commands[self.command_handler.commands['Command'] == cmd].iloc[0]
            
            if row['Menu Level'] == 'main':
                keyboard = self.command_handler.get_submenu_keyboard(row['Main Category'])
                message = row['Description']
                
                if keyboard:
                    query.edit_message_text(message, reply_markup=keyboard)
                else:
                    query.edit_message_text(message)
            else:
                query.edit_message_text(row['Description'])
        except Exception as e:
            logger.error(f'Error in button callback: {str(e)}')
            query.edit_message_text(ERROR_MESSAGES['general_error'])
    
    def error_handler(self, update, context):
        """Handle errors"""
        logger.error(f'Update {update} caused error {context.error}')
    
    def run(self):
        """Start the bot"""
        logger.info('Starting MewFi Bot...')
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    try:
        bot = MewFiBot()
        bot.run()
    except Exception as e:
        logger.critical(f'Failed to start bot: {str(e)}')