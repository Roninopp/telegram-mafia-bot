import logging
from telegram.ext import Application, CommandHandler
from core.config import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MafiaBot:
    def __init__(self):
        self.token = Config.BOT_TOKEN
        if not self.token:
            logger.error("❌ BOT_TOKEN not found! Please check your .env file")
            raise ValueError("BOT_TOKEN not configured")
        
        # Create bot application
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
        logger.info("✅ MafiaBot initialized successfully!")
    
    def _setup_handlers(self):
        """Register all command handlers"""
        # Basic start command for now
        from handlers.start import start_handler
        self.application.add_handler(CommandHandler("start", start_handler))
        
        logger.info("✅ Handlers registered")
    
    def run(self):
        """Start the bot"""
        logger.info("🤵 Mafia Bot is starting...")
        print("🎮 Bot is running! Press Ctrl+C to stop.")
        self.application.run_polling()

if __name__ == "__main__":
    bot = MafiaBot()
    bot.run()
