from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from core.database import Database
from models.player import Player
from models.npc import NPCFactory
from utils.animations import CombatAnimations
from utils.combat_calculator import CombatCalculator
import random

# Initialize systems
db = Database()
combat_calc = CombatCalculator()
animations = CombatAnimations()

class EnhancedCombatHandler:
    def __init__(self):
        self.active_battles = {}  # Track ongoing battles
    
    async def combat_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main combat menu with buttons"""
        user = update.effective_user
        player = db.get_player(user.id)
        
        if not player:
            await update.message.reply_text(
                "❌ You need to create a character first! Use /start",
                parse_mode='Markdown'
            )
            return
        
        # Create combat menu keyboard
        keyboard = [
            [InlineKeyboardButton("🤖 Fight Bots", callback_data="fight_bots")],
            [InlineKeyboardButton("👥 PvP Battle", callback_data="pvp_battle")],
            [InlineKeyboardButton("🏆 Boss Fight", callback_data="boss_fight")],
            [InlineKeyboardButton("🎯 Training", callback_data="training_mode")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚔️ **Combat Arena** ⚔️\n\n"
            f"**{player.first_name}** - Level {player.level}\n"
            f"❤️ {player.health}/100 | ⚡ {player.energy}/50\n\n"
            f"Choose your battle type:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def bot_battle_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """NPC battle difficulty selection"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        player = db.get_player(user.id)
        
        if not player:
            await query.edit_message_text("❌ Player not found!")
            return
        
        keyboard = [
            [InlineKeyboardButton("🥊 Easy - Street Thugs", callback_data="bot_easy")],
            [InlineKeyboardButton("💪 Medium - Gang Members", callback_data="bot_medium")],
            [InlineKeyboardButton("🔥 Hard - Police Officers", callback_data="bot_hard")],
            [InlineKeyboardButton("🔙 Back", callback_data="combat_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🤖 **Bot Battles**\n\n"
            f"Fight against AI opponents!\n\n"
            f"**Your Level:** {player.level}\n"
            f"**Recommended:** {'Easy' if player.level < 5 else 'Medium' if player.level < 10 else 'Hard'}\n\n"
            f"Choose difficulty:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def start_bot_battle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start a battle against NPC bot"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        player = db.get_player(user.id)
        difficulty = query.data.replace("bot_", "")
        
        if not player:
            await query.edit_message_text("❌ Player not found!")
            return
        
        # Check energy
        if player.energy < 15:
            await query.edit_message_text(
                f"⚡ Not enough energy! You need 15 energy.\n"
                f"Current: {player.energy}/50\n\n"
                f"Wait for energy to regenerate (1 energy per 5 minutes).",
                parse_mode='Markdown'
            )
            return
        
        # Create NPC based on difficulty and player level
        if difficulty == "easy":
            npc = NPCFactory.create_street_thug(player.level)
        elif difficulty == "medium":
            npc = NPCFactory.create_gang_member(player.level)
        else:  # hard
            npc = NPCFactory.create_police_officer(player.level)
        
        # Start the battle
        await self._execute_bot_battle(query, player, npc)
    
    async def _execute_bot_battle(self, query, player: Player, npc):
        """Execute battle against NPC with animations"""
        # Deduct energy
        player.energy -= 15
        db.save_player(player)
        
        battle_log = []
        
        # BATTLE INTRODUCTION
        intro_text = f"🤖 **BOT BATTLE START!** 🤖\n\n" \
                    f"**{player.first_name}** (Level {player.level}) vs\n" \
                    f"**{npc.name}** (Level {npc.level}) - {npc.difficulty.upper()}\n\n" \
                    f"{animations.generate_health_bar(player.health)} - YOU\n" \
                    f"{animations.generate_health_bar(npc.health, npc.max_health)} - {npc.name}"
        
        await query.edit_message_text(intro_text, parse_mode='Markdown')
        
        # BATTLE ROUNDS (3 rounds max)
        for round_num in range(1, 4):
            if player.health <= 0 or npc.health <= 0:
                break
            
            await self._send_round_animation(query, round_num)
            
            # Player turn
            player_damage = combat_calc.calculate_damage(player, npc)
            npc.take_damage(player_damage)
            player_attack_text = animations.class_specific_attack(player.first_name, player.character_class)
            player_damage_text = animations.damage_animation(player_damage)
            
            round_text = f"**Round {round_num}**\n\n" \
                        f"{player_attack_text}\n" \
                        f"{player_damage_text}\n\n" \
                        f"{animations.generate_health_bar(player.health)} - YOU\n" \
                        f"{animations.generate_health_bar(npc.health, npc.max_health)} - {npc.name}"
            
            await query.edit_message_text(round_text, parse_mode='Markdown')
            await self._delay(2)
            
            # Check if NPC defeated
            if npc.health <= 0:
                break
            
            # NPC turn
            npc_action = npc.choose_action(player.level)
            if npc_action == "attack":
                npc_damage = npc.calculate_damage()
                player.health -= npc_damage
                npc_attack_text = f"🤖 **{npc.name}** attacks!"
                npc_damage_text = animations.damage_animation(npc_damage)
            elif npc_action == "defend":
                npc_attack_text = f"🛡️ **{npc.name}** defends! (Damage reduced next round)"
                npc_damage_text = "No damage this round!"
            else:  # special
                npc_damage = int(npc.calculate_damage() * 1.5)
                player.health -= npc_damage
                npc_attack_text = f"💫 **{npc.name}** uses SPECIAL MOVE!"
                npc_damage_text = animations.damage_animation(npc_damage, critical=True)
            
            npc_round_text = f"**{npc.name}'s Turn:**\n\n" \
                            f"{npc_attack_text}\n" \
                            f"{npc_damage_text}\n\n" \
                            f"{animations.generate_health_bar(player.health)} - YOU\n" \
                            f"{animations.generate_health_bar(npc.health, npc.max_health)} - {npc.name}"
            
            await query.edit_message_text(npc_round_text, parse_mode='Markdown')
            await self._delay(2)
        
        # BATTLE RESULTS
        await self._battle_results(query, player, npc)
    
    async def _send_round_animation(self, query, round_num):
        """Send round animation"""
        animations = ["🥊", "💥", "⚡", "🔥", "🎯"]
        anim_text = f"Round {round_num} " + "".join(random.sample(animations, 3))
        await query.edit_message_text(anim_text)
        await self._delay(1)
    
    async def _battle_results(self, query, player: Player, npc):
        """Calculate and display battle results"""
        player_victory = npc.health <= 0
        
        if player_victory:
            rewards = npc.get_rewards()
            player.cash += rewards["cash"]
            player.reputation += rewards["reputation"]
            
            victory_text = f"🎉 **VICTORY!** 🎉\n\n" \
                          f"You defeated **{npc.name}**!\n\n" \
                          f"**Rewards:**\n" \
                          f"💰 +${rewards['cash']}\n" \
                          f"⭐ +{rewards['reputation']} Reputation\n" \
                          f"📈 +{rewards['exp']} Experience\n\n" \
                          f"**Final Health:** {player.health}/100"
            
            # Check level up
            if random.random() < 0.4:  # 40% chance to level up after victory
                player.level += 1
                player.health = 100
                player.energy = 50
                victory_text += f"\n\n✨ **LEVEL UP!** You're now level {player.level}!"
        
        else:
            rewards = {"cash": 0, "reputation": -2, "exp": 5}
            player.reputation += rewards["reputation"]
            player.health = max(1, player.health)  # Don't die completely
            
            victory_text = f"💀 **DEFEAT** 💀\n\n" \
                          f"**{npc.name}** was too strong!\n\n" \
                          f"**You gained:**\n" \
                          f"📈 +{rewards['exp']} Experience\n" \
                          f"📉 {rewards['reputation']} Reputation\n\n" \
                          f"**Final Health:** {player.health}/100\n" \
                          f"Better luck next time!"
        
        # Save player progress
        db.save_player(player)
        
        # Add continue button
        keyboard = [
            [InlineKeyboardButton("⚔️ Fight Again", callback_data="fight_bots")],
            [InlineKeyboardButton("📊 My Profile", callback_data="my_profile")],
            [InlineKeyboardButton("🎮 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            victory_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _delay(self, seconds: int):
        """Utility delay function"""
        import asyncio
        await asyncio.sleep(seconds)

# Create handler instance
combat_handler = EnhancedCombatHandler()

# Handler registration
def register_handlers(application):
    application.add_handler(CallbackQueryHandler(combat_handler.combat_menu, pattern="^combat_menu$"))
    application.add_handler(CallbackQueryHandler(combat_handler.bot_battle_menu, pattern="^fight_bots$"))
    application.add_handler(CallbackQueryHandler(combat_handler.start_bot_battle, pattern="^bot_(easy|medium|hard)$"))
