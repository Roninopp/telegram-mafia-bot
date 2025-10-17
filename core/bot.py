from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, Application
from core.database import Database
from models.player import Player
import os
import logging

# Import handlers with proper error handling
try:
    from shop.shop_handlers import get_shop_handlers
    SHOP_AVAILABLE = True
except ImportError:
    print("⚠️ Shop module not available - shop features disabled")
    SHOP_AVAILABLE = False

try:
    from handlers.combat_integration import integrate_combat_system
    COMBAT_AVAILABLE = True
except ImportError:
    print("⚠️ Combat module not available - combat features disabled") 
    COMBAT_AVAILABLE = False

# Initialize database
db = Database()

class MafiaBot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = Database()
        
        # Get bot token from environment
        self.token = os.environ.get("BOT_TOKEN")
        if not self.token:
            raise ValueError("BOT_TOKEN environment variable not set!")
        
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Register handlers
        self.setup_handlers()
        
        print("✅ MafiaBot initialized successfully!")
    
    def setup_handlers(self):
        """Register all handlers"""
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("profile", profile_handler_query))
        self.application.add_handler(CallbackQueryHandler(button_handler, pattern="^(create_char|my_profile|combat|gang_info|shop)$"))
        
        # Add shop handlers if available
        if SHOP_AVAILABLE:
            try:
                shop_handlers = get_shop_handlers()
                for handler in shop_handlers:
                    self.application.add_handler(handler)
                print("✅ Shop handlers integrated")
            except Exception as e:
                print(f"❌ Shop handler integration failed: {e}")
        
        # Add combat system if available
        if COMBAT_AVAILABLE:
            try:
                integrate_combat_system(self.application)
                print("✅ Combat system integrated")
            except Exception as e:
                print(f"❌ Combat system integration failed: {e}")
        
        self.application.add_handler(CallbackQueryHandler(class_selection_handler, pattern="^(class_enforcer|class_hacker|class_smuggler)$"))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
        self.application.add_handler(CallbackQueryHandler(profile_handler_query, pattern="^my_profile$"))
        self.application.add_handler(CallbackQueryHandler(combat_menu, pattern="^find_opponent$"))
    
    def run(self):
        """Start the bot"""
        print("🚀 Starting Mafia Wars Bot...")
        self.application.run_polling()

# Handler functions (keep all your existing functions below)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if player already exists
    existing_player = db.get_player(user.id)
    
    # Create main menu keyboard
    keyboard = [
        [InlineKeyboardButton("🎮 Create Character", callback_data="create_char")],
        [InlineKeyboardButton("📊 My Profile", callback_data="my_profile")],
        [InlineKeyboardButton("⚔️ Fight", callback_data="combat")],
        [InlineKeyboardButton("👥 Gang Info", callback_data="gang_info")],
        [InlineKeyboardButton("🏪 Shop", callback_data="shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if existing_player:
        welcome_text = f"""
👋 **Welcome back, {user.first_name}!**

{existing_player.get_stats()}

**What would you like to do?**
        """
    else:
        welcome_text = f"""
👋 **Welcome to Mafia Wars, {user.first_name}!**

Your criminal empire awaits...

**Choose your action:**
        """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    if data == "create_char":
        await create_character_menu(query)
    elif data == "my_profile":
        await profile_handler_query(query)
    elif data == "combat":
        if COMBAT_AVAILABLE:
            from handlers.combat_handlers import combat_handlers
            await combat_handlers.combat_menu(update, context)
        else:
            await query.edit_message_text("⚔️ **Combat System**\n\nCombat features coming soon! 🔥", parse_mode='Markdown')
    elif data == "gang_info":
        await query.edit_message_text("👥 **Gang System**\n\nForm alliances with other players!\n\n*Coming soon in next update!*", parse_mode='Markdown')
    elif data == "shop":
        if SHOP_AVAILABLE:
            from shop.shop_handlers import shop_main_menu
            await shop_main_menu(update, context)
        else:
            await query.edit_message_text("🏪 **Black Market**\n\nShop features coming soon! 🛍️", parse_mode='Markdown')

async def create_character_menu(query):
    """Show character creation with buttons"""
    keyboard = [
        [InlineKeyboardButton("🎯 Enforcer - Combat Specialist", callback_data="class_enforcer")],
        [InlineKeyboardButton("💻 Hacker - Tech Master", callback_data="class_hacker")],
        [InlineKeyboardButton("🚗 Smuggler - Stealth Expert", callback_data="class_smuggler")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎭 **Character Creation**

Choose your criminal specialty:

**🎯 Enforcer**
• Extra health and damage
• Perfect for direct combat
• Strong and intimidating

**💻 Hacker**  
• Better income from operations
• Stealth and intelligence
• Tech and cyber skills

**🚗 Smuggler**
• More energy for actions
• Better escape chances
• Logistics and transport
    """
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def class_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    class_map = {
        "class_enforcer": ("enforcer", "🎯 Enforcer"),
        "class_hacker": ("hacker", "💻 Hacker"),
        "class_smuggler": ("smuggler", "🚗 Smuggler")
    }
    
    if data in class_map:
        class_name, display_name = class_map[data]
        
        # Check if player already exists
        existing_player = db.get_player(user.id)
        if existing_player:
            await query.edit_message_text(
                f"⚠️ You already have a character!\n\n"
                f"**{existing_player.first_name}** ({existing_player.character_class.title()})\n\n"
                f"Use /reset to create a new character (loses all progress).",
                parse_mode='Markdown'
            )
            return
        
        # Create new player
        new_player = Player(
            user_id=user.id,
            username=user.username or "Unknown",
            first_name=user.first_name,
            character_class=class_name
        )
        
        # Save to database
        db.save_player(new_player)
        
        # Success message with menu
        keyboard = [
            [InlineKeyboardButton("📊 View Profile", callback_data="my_profile")],
            [InlineKeyboardButton("⚔️ Start Fighting", callback_data="combat")],
            [InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎉 **Character Created!**\n\n"
            f"Welcome, **{new_player.first_name}** the **{display_name}**!\n\n"
            f"{new_player.get_stats()}\n\n"
            f"Your criminal journey begins now!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def profile_handler_query(query):
    """Show profile with inline keyboard"""
    user = query.from_user
    player = db.get_player(user.id)
    
    if player:
        keyboard = [
            [InlineKeyboardButton("⚔️ Fight", callback_data="combat")],
            [InlineKeyboardButton("🏪 Shop", callback_data="shop")],
            [InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📊 **Criminal Profile**\n\n"
            f"{player.get_stats()}\n\n"
            f"**Available Actions:**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("🎮 Create Character", callback_data="create_char")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❌ You don't have a character yet!\n\nCreate your character to start your criminal journey.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def combat_menu(query):
    """Show combat menu"""
    user = query.from_user
    player = db.get_player(user.id)
    
    if not player:
        await query.edit_message_text("❌ Create a character first!", parse_mode='Markdown')
        return
    
    keyboard = [
        [InlineKeyboardButton("🎯 Find Opponent", callback_data="find_opponent")],
        [InlineKeyboardButton("📊 My Stats", callback_data="my_profile")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚔️ **Combat Arena**\n\n"
        f"Ready for some action, {player.first_name}?\n\n"
        f"**Your Combat Stats:**\n"
        f"❤️ Health: {player.health}/100\n"
        f"⚡ Energy: {player.energy}/50\n"
        f"⭐ Level: {player.level}\n\n"
        f"Find an opponent to test your skills!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    existing_player = db.get_player(user.id)
    
    keyboard = [
        [InlineKeyboardButton("🎮 Create Character", callback_data="create_char")],
        [InlineKeyboardButton("📊 My Profile", callback_data="my_profile")],
        [InlineKeyboardButton("⚔️ Fight", callback_data="combat")],
        [InlineKeyboardButton("👥 Gang Info", callback_data="gang_info")],
        [InlineKeyboardButton("🏪 Shop", callback_data="shop")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if existing_player:
        text = f"👋 **Welcome back, {user.first_name}!**\n\nWhat would you like to do?"
    else:
        text = f"👋 **Welcome to Mafia Wars!**\n\nStart your criminal journey!"
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

# Keep the old register_handlers function for compatibility
def register_handlers(application):
    """Legacy function for main.py compatibility"""
    bot = MafiaBot()
    # Handlers are already registered in MafiaBot.__init__
    return bot
