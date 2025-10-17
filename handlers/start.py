from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    welcome_text = f"""
👋 **Welcome to Mafia Wars, {user.first_name}!**

Your criminal empire awaits... 

**Choose your path:**
• 🎯 **Enforcer** - Combat specialist
• 💻 **Hacker** - Tech and intelligence  
• 🚗 **Smuggler** - Logistics expert

Use /create to begin your journey!
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )
    print(f"✅ New user started: {user.first_name} (ID: {user.id})")

async def create_character_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle character creation"""
    character_options = [
        ["🎯 Enforcer", "💻 Hacker"],
        ["🚗 Smuggler"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(character_options, one_time_keyboard=True)
    
    await update.message.reply_text(
        "**Choose your criminal specialty:**\n\n"
        "🎯 **Enforcer** - Strong in combat, extra health\n"
        "💻 **Hacker** - Better income, stealth operations\n"  
        "🚗 **Smuggler** - More energy, escape bonuses\n\n"
        "Select your class:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Handler registration function
def register_handlers(application):
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("create", create_character_handler))
