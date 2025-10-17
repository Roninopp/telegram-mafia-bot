from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from core.database import Database
from handlers.combat_core import combat_core
from handlers.animation import CombatAnimations
import asyncio

db = Database()
animations = CombatAnimations()

class CombatHandlers:
    def __init__(self):
        self.pending_battles = {}
    
    async def combat_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main combat menu - called from your existing button handler"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        player = db.get_player(user.id)
        
        if not player:
            await query.edit_message_text(
                "❌ You need to create a character first!",
                parse_mode='Markdown'
            )
            return
        
        if player.energy < 10:
            await query.edit_message_text(
                f"⚡ Not enough energy! You have {player.energy}/50 energy.\n\n"
                f"Wait for energy to regenerate or use energy drinks from the shop!",
                parse_mode='Markdown'
            )
            return
        
        keyboard = [
            [InlineKeyboardButton("⚔️ 1v1 Quick Match", callback_data="combat_quick")],
            [InlineKeyboardButton("🤖 Practice vs Bot", callback_data="combat_bot")],
            [InlineKeyboardButton("👥 Gang War (Coming Soon)", callback_data="combat_gang")],
            [InlineKeyboardButton("📊 My Combat Stats", callback_data="combat_stats")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⚔️ **Combat Arena** ⚔️\n\n"
            f"Welcome, {player.first_name}!\n\n"
            f"**Your Stats:**\n"
            f"{animations.generate_health_bar(player.health)}\n"
            f"⚡ Energy: {player.energy}/50\n"
            f"⭐ Level: {player.level}\n"
            f"🎯 Class: {player.character_class.title()}\n\n"
            f"**Choose your battle type:**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def start_quick_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start quick PvP match with NPC fallback"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        player = db.get_player(user.id)
        
        if not player or player.energy < 10:
            await query.edit_message_text("❌ Cannot start battle!")
            return
        
        # Show searching animation
        await query.edit_message_text(
            f"🔍 **Searching for opponent...**\n\n"
            f"Looking for players with similar skill level...",
            parse_mode='Markdown'
        )
        
        # Start battle (PvP with NPC fallback)
        battle_data = await combat_core.start_1v1_battle(user.id)
        
        if 'error' in battle_data:
            await query.edit_message_text(
                f"❌ {battle_data['error']}",
                parse_mode='Markdown'
            )
            return
        
        # Store battle info
        self.pending_battles[user.id] = battle_data
        
        # Show battle intro
        if battle_data['type'] == 'pvp':
            opponent = battle_data['players'][1]
            battle_text = f"🎯 **MATCH FOUND!**\n\n**Opponent:** {opponent.first_name}\n⭐ Level: {opponent.level}\n🎭 Class: {opponent.character_class.title()}"
        else:
            npc_data = battle_data['npc_data']
            battle_text = f"🤖 **BOT BATTLE**\n\n**Opponent:** {npc_data['name']}\n⭐ Level: {npc_data['level']}\n🎯 Difficulty: {npc_data['difficulty'].title()}"
        
        # Show battle actions
        keyboard = [
            [InlineKeyboardButton("💥 Attack", callback_data=f"battle_attack_{battle_data['battle_id']}")],
            [InlineKeyboardButton("🛡️ Defend", callback_data=f"battle_defend_{battle_data['battle_id']}")],
            [InlineKeyboardButton("✨ Special", callback_data=f"battle_special_{battle_data['battle_id']}")],
            [InlineKeyboardButton("🏃 Escape", callback_data=f"battle_escape_{battle_data['battle_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send battle intro animation
        for frame in battle_data['intro_animation']:
            await query.message.reply_text(frame, parse_mode='Markdown')
            await asyncio.sleep(1.5)
        
        await query.message.reply_text(
            f"{battle_text}\n\n"
            f"**Battle Started!** Choose your action:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def start_bot_battle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start battle against NPC bot"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        player = db.get_player(user.id)
        
        if not player or player.energy < 10:
            await query.edit_message_text("❌ Cannot start battle!")
            return
        
        await query.edit_message_text(
            f"🤖 **Creating bot opponent...**",
            parse_mode='Markdown'
        )
        
        # Start NPC battle
        battle_data = await combat_core.start_1v1_battle(user.id, is_bot=True)
        
        if 'error' in battle_data:
            await query.edit_message_text(f"❌ {battle_data['error']}")
            return
        
        # Store battle info
        self.pending_battles[user.id] = battle_data
        
        # Show battle actions
        keyboard = [
            [InlineKeyboardButton("💥 Attack", callback_data=f"battle_attack_{battle_data['battle_id']}")],
            [InlineKeyboardButton("🛡️ Defend", callback_data=f"battle_defend_{battle_data['battle_id']}")],
            [InlineKeyboardButton("✨ Special", callback_data=f"battle_special_{battle_data['battle_id']}")],
            [InlineKeyboardButton("🏃 Escape", callback_data=f"battle_escape_{battle_data['battle_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send battle intro animation
        for frame in battle_data['intro_animation']:
            await query.message.reply_text(frame, parse_mode='Markdown')
            await asyncio.sleep(1.5)
        
        npc_data = battle_data['npc_data']
        await query.message.reply_text(
            f"🤖 **BOT BATTLE STARTED!**\n\n"
            f"**Opponent:** {npc_data['name']}\n"
            f"⭐ Level: {npc_data['level']}\n"
            f"🎯 Difficulty: {npc_data['difficulty'].title()}\n"
            f"🧠 Personality: {npc_data['personality'].title()}\n\n"
            f"{animations.generate_health_bar(npc_data['health'])}\n\n"
            f"**Choose your action:**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def battle_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle battle actions"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        data = query.data
        
        # Extract action and battle_id
        action_parts = data.split('_')
        action = action_parts[1]
        battle_id = '_'.join(action_parts[2:])
        
        # Execute player's turn
        result = await combat_core.execute_player_turn(battle_id, action)
        
        if 'error' in result:
            await query.edit_message_text(f"❌ {result['error']}")
            return
        
        # Show action result
        response_text = ""
        
        # Player's action
        if 'animation' in result:
            await query.message.reply_text(result['animation'], parse_mode='Markdown')
            await asyncio.sleep(1)
        
        if 'damage_text' in result:
            await query.message.reply_text(result['damage_text'], parse_mode='Markdown')
            await asyncio.sleep(1)
        
        # NPC's action (for PvE)
        if 'npc_animation' in result:
            await query.message.reply_text(result['npc_animation'], parse_mode='Markdown')
            await asyncio.sleep(1)
        
        if 'npc_damage_text' in result:
            await query.message.reply_text(result['npc_damage_text'], parse_mode='Markdown')
            await asyncio.sleep(1)
        
        # Check if battle ended
        if result.get('battle_ended'):
            if result.get('rewards'):
                # Victory with rewards
                rewards = result['rewards']
                victory_frames = animations.victory_celebration(user.first_name, rewards.get('cash', 0))
                
                for frame in victory_frames:
                    await query.message.reply_text(frame, parse_mode='Markdown')
                    await asyncio.sleep(1.5)
                
                # Show rewards
                keyboard = [
                    [InlineKeyboardButton("🛒 Spend Rewards", callback_data="shop")],
                    [InlineKeyboardButton("⚔️ Fight Again", callback_data="combat_quick")],
                    [InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    f"🎊 **BATTLE COMPLETE!**\n\n"
                    f"**Rewards Earned:**\n"
                    f"💰 +${rewards.get('cash', 0)} Gold\n"
                    f"⭐ +{rewards.get('reputation', 0)} Reputation\n"
                    f"📈 +{rewards.get('exp', 0)} Experience\n\n"
                    f"**What would you like to do?**",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                # Defeat
                keyboard = [
                    [InlineKeyboardButton("⚔️ Try Again", callback_data="combat_quick")],
                    [InlineKeyboardButton("🏥 Heal Up", callback_data="shop")],
                    [InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    f"💀 **DEFEAT!**\n\n"
                    f"You were defeated in battle...\n\n"
                    f"**Don't give up!** Heal up and try again!",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
            # Clear pending battle
            self.pending_battles.pop(user.id, None)
            return
        
        # Battle continues - show next actions
        player = db.get_player(user.id)
        battle = combat_core.active_battles.get(battle_id, {})
        
        if battle.get('type') == 'pve':
            npc = battle.get('npc', {})
            npc_health = getattr(npc, 'health', 0)
            npc_max_health = getattr(npc, 'max_health', 100)
            
            keyboard = [
                [InlineKeyboardButton("💥 Attack", callback_data=f"battle_attack_{battle_id}")],
                [InlineKeyboardButton("🛡️ Defend", callback_data=f"battle_defend_{battle_id}")],
                [InlineKeyboardButton("✨ Special", callback_data=f"battle_special_{battle_id}")],
                [InlineKeyboardButton("🏃 Escape", callback_data=f"battle_escape_{battle_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                f"⚔️ **Battle Continues!**\n\n"
                f"**Your Health:** {animations.generate_health_bar(player.health)}\n"
                f"**{npc.name}'s Health:** {animations.generate_health_bar(npc_health, npc_max_health)}\n\n"
                f"**Choose your next action:**",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

# Create handler instance
combat_handlers = CombatHandlers()

# Handler registration function
def get_combat_handlers():
    return [
        CallbackQueryHandler(combat_handlers.combat_menu, pattern="^combat$"),
        CallbackQueryHandler(combat_handlers.start_quick_match, pattern="^combat_quick$"),
        CallbackQueryHandler(combat_handlers.start_bot_battle, pattern="^combat_bot$"),
        CallbackQueryHandler(combat_handlers.battle_action, pattern="^battle_"),
    ]
