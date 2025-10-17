from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from core.database import Database
from models.player import Player

# Initialize database
db = Database()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if player already exists
    existing_player = db.get_player(user.id)
    
    if existing_player:
        # Welcome back existing player
        welcome_text = f"""
👋 **Welcome back, {user.first_name}!**

{existing_player.get_stats()}

**Available Commands:**
/profile - View your stats
/attack - Fight other players
/create - Reset your character
        """
    else:
        # New player
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
    print(f"✅ User accessed: {user.first_name} (ID: {user.id})")

async def create_character_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start character creation process"""
    user = update.effective_user
    
    # Check if player already exists
    existing_player = db.get_player(user.id)
    if existing_player:
        await update.message.reply_text(
            f"⚠️ You already have a character!\n\n"
            f"Use /profile to see your stats.\n"
            f"Use /create again to reset your character (this will delete your progress!).",
            parse_mode='Markdown'
        )
        return
    
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
    
    # Set state to wait for class selection
    context.user_data['awaiting_class'] = True

async def handle_class_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user selects a character class"""
    if not context.user_data.get('awaiting_class'):
        return
    
    user = update.effective_user
    text = update.message.text
    class_map = {
        "🎯 Enforcer": "enforcer",
        "💻 Hacker": "hacker", 
        "🚗 Smuggler": "smuggler"
    }
    
    if text in class_map:
        class_name = class_map[text]
        
        # Create new player
        new_player = Player(
            user_id=user.id,
            username=user.username or "Unknown",
            first_name=user.first_name,
            character_class=class_name
        )
        
        # Save to database
        db.save_player(new_player)
        
        # Clear the state
        context.user_data['awaiting_class'] = False
        
        await update.message.reply_text(
            f"🎉 **Character Created!**\n\n"
            f"Welcome, {new_player.first_name} the {class_name.title()}!\n\n"
            f"{new_player.get_stats()}\n\n"
            f"Use /profile to check your stats anytime!\n"
            f"Use /attack to find opponents!",
            parse_mode='Markdown',
            reply_markup=None  # Remove keyboard
        )
        print(f"✅ New character created: {user.first_name} as {class_name}")
    else:
        await update.message.reply_text(
            "❌ Please select a valid class from the options!",
            reply_markup=None
        )

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show player profile"""
    user = update.effective_user
    player = db.get_player(user.id)
    
    if player:
        await update.message.reply_text(
            f"📊 **Your Criminal Profile**\n\n"
            f"{player.get_stats()}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ You don't have a character yet! Use /create to start your criminal journey.",
            parse_mode='Markdown'
        )

# Handler registration function
def register_handlers(application):
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("create", create_character_handler))
    application.add_handler(CommandHandler("profile", profile_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_class_selection))
