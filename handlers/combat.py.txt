from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from core.database import Database
from utils.combat_calculator import CombatCalculator
from utils.animations import CombatAnimations
import random

# Initialize database and calculators
db = Database()
combat_calc = CombatCalculator()
animations = CombatAnimations()

class CombatHandler:
    def __init__(self):
        self.pending_challenges = {}  # Store pending fights
    
    async def attack_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the attack process - find opponents"""
        user = update.effective_user
        player = db.get_player(user.id)
        
        if not player:
            await update.message.reply_text(
                "❌ You need to create a character first! Use /create to start.",
                parse_mode='Markdown'
            )
            return
        
        if player.energy < 10:
            await update.message.reply_text(
                f"⚡ Not enough energy! You have {player.energy}/10 energy.\n"
                f"Wait for energy to regenerate or use items to restore energy.",
                parse_mode='Markdown'
            )
            return
        
        # Get random opponent (excluding self)
        all_players = self._get_potential_opponents(user.id)
        
        if not all_players:
            await update.message.reply_text(
                "👀 No opponents available right now!\n"
                "Try again later or invite friends to join the game.",
                parse_mode='Markdown'
            )
            return
        
        opponent = random.choice(all_players)
        
        # Show opponent selection
        opponent_text = f"""
🎯 **Found an opponent!**

**{opponent.first_name}** (Level {opponent.level})
{class_emoji(opponent.character_class)} {opponent.character_class.title()}

{animations.generate_health_bar(opponent.health)}

**Choose your action:**
/attack_confirm - Engage in combat
/attack_cancel - Look for another target
        """
        
        # Store opponent info for confirmation
        context.user_data['selected_opponent'] = opponent.user_id
        
        await update.message.reply_text(
            opponent_text,
            parse_mode='Markdown'
        )
    
    async def attack_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and execute the attack"""
        user = update.effective_user
        player = db.get_player(user.id)
        
        if not player:
            await update.message.reply_text("❌ Player data not found!")
            return
        
        opponent_id = context.user_data.get('selected_opponent')
        if not opponent_id:
            await update.message.reply_text("❌ No opponent selected! Use /attack first.")
            return
        
        opponent = db.get_player(opponent_id)
        if not opponent:
            await update.message.reply_text("❌ Opponent no longer available!")
            return
        
        # Check if attack is possible
        can_attack, message = combat_calc.can_attack(player, opponent)
        if not can_attack:
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        # Start epic combat sequence!
        await self._execute_combat(update, player, opponent)
        
        # Clear selected opponent
        context.user_data.pop('selected_opponent', None)
    
    async def _execute_combat(self, update: Update, attacker: 'Player', defender: 'Player'):
        """Execute the combat sequence with epic animations"""
        # Energy cost
        attacker.energy -= 10
        db.save_player(attacker)
        
        # COMBAT INTRO SEQUENCE
        intro_frames = animations.combat_intro(attacker.first_name, defender.first_name)
        for frame in intro_frames:
            await update.message.reply_text(frame, parse_mode='Markdown')
            await asyncio.sleep(1.5)
        
        # Check for escape chance
        if combat_calc.calculate_escape_chance(attacker, defender):
            escape_frames = animations.escape_sequence(defender.first_name)
            for frame in escape_frames:
                await update.message.reply_text(frame, parse_mode='Markdown')
                await asyncio.sleep(1)
            
            # Still give some experience for attempted fight
            attacker.reputation += 1
            db.save_player(attacker)
            
            await update.message.reply_text(
                f"🏃 **{defender.first_name} escaped the fight!**\n\n"
                f"You gain +1 reputation for the attempt.",
                parse_mode='Markdown'
            )
            return
        
        # ATTACK SEQUENCE
        await asyncio.sleep(1)
        
        # Attacker's turn
        attack_animation = animations.class_specific_attack(attacker.first_name, attacker.character_class)
        await update.message.reply_text(attack_animation, parse_mode='Markdown')
        await asyncio.sleep(1.5)
        
        damage = combat_calc.calculate_damage(attacker, defender)
        critical = random.random() < 0.1  # 10% critical chance
        
        damage_text = animations.damage_animation(damage, critical)
        if critical:
            damage *= 2  # Double damage for critical
            damage_text = f"💫 **ULTRA CRITICAL!** {damage} damage! 🌟"
        
        await update.message.reply_text(damage_text, parse_mode='Markdown')
        
        # Apply damage
        defender.health -= damage
        defender.health = max(0, defender.health)  # Don't go below 0
        
        # Check if defender is defeated
        if defender.health <= 0:
            victory = True
            # Defender gets some health back after defeat
            defender.health = 50
        else:
            # Defender counter-attacks
            await asyncio.sleep(1.5)
            counter_damage = combat_calc.calculate_damage(defender, attacker)
            counter_animation = animations.class_specific_attack(defender.first_name, defender.character_class)
            
            await update.message.reply_text(counter_animation, parse_mode='Markdown')
            await asyncio.sleep(1)
            
            counter_damage_text = animations.damage_animation(counter_damage, False)
            await update.message.reply_text(counter_damage_text, parse_mode='Markdown')
            
            attacker.health -= counter_damage
            attacker.health = max(0, attacker.health)
            
            victory = attacker.health > defender.health
        
        # COMBAT RESULTS
        await asyncio.sleep(2)
        
        if victory:
            # Victory sequence
            rewards = combat_calc.calculate_rewards(attacker, defender, True)
            
            victory_frames = animations.victory_celebration(attacker.first_name, rewards['cash'])
            for frame in victory_frames:
                await update.message.reply_text(frame, parse_mode='Markdown')
                await asyncio.sleep(1.5)
            
            # Apply rewards
            attacker.cash += rewards['cash']
            attacker.reputation += rewards['reputation']
            defender.cash = max(0, defender.cash - rewards['cash'])  # Don't go below 0
            
            result_text = f"""
🎊 **COMBAT RESULTS - VICTORY!** 🎊

**{attacker.first_name}**
{animations.generate_health_bar(attacker.health)}
💰 +${rewards['cash']} | 🎯 +{rewards['reputation']} Reputation

**{defender.first_name}**  
{animations.generate_health_bar(defender.health)}
💰 -${rewards['cash']} | 📉 Reputation decreased
            """
        else:
            # Defeat sequence
            rewards = combat_calc.calculate_rewards(attacker, defender, False)
            
            await update.message.reply_text(
                f"💀 **DEFEAT!**\n\n"
                f"**{defender.first_name}** defended successfully!\n\n"
                f"You gain {rewards['experience']} experience.",
                parse_mode='Markdown'
            )
            
            result_text = f"""
⚔️ **COMBAT RESULTS - DEFEAT** ⚔️

**{attacker.first_name}**
{animations.generate_health_bar(attacker.health)}
📉 -{abs(rewards['reputation'])} Reputation

**{defender.first_name}**
{animations.generate_health_bar(defender.health)}
🎯 Reputation increased!
            """
        
        # Save player states
        db.save_player(attacker)
        db.save_player(defender)
        
        await update.message.reply_text(result_text, parse_mode='Markdown')
        
        # Check for level up
        if victory and random.random() < 0.3:  # 30% chance to level up after victory
            await self._check_level_up(update, attacker)
    
    async def _check_level_up(self, update: Update, player: 'Player'):
        """Check and handle level up"""
        old_level = player.level
        player.level += 1
        player.health = 100  # Full heal
        player.energy = 50   # Full energy
        
        db.save_player(player)
        
        level_frames = animations.level_up_animation(player.first_name, player.level)
        for frame in level_frames:
            await update.message.reply_text(frame, parse_mode='Markdown')
            await asyncio.sleep(1.5)
    
    def _get_potential_opponents(self, exclude_user_id: int) -> list:
        """Get list of potential opponents (simplified for now)"""
        # In a real implementation, you'd query the database
        # For now, we'll return a limited list or use mock data
        all_players = []
        
        # This is simplified - in real implementation, you'd query the database
        # for active players with similar levels
        return all_players  # Will be implemented fully later

    async def attack_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the current attack selection"""
        context.user_data.pop('selected_opponent', None)
        await update.message.reply_text(
            "🔄 Attack cancelled.\nUse /attack to find another opponent.",
            parse_mode='Markdown'
        )

def class_emoji(character_class: str) -> str:
    """Get emoji for character class"""
    emojis = {
        'enforcer': '🎯',
        'hacker': '💻', 
        'smuggler': '🚗'
    }
    return emojis.get(character_class, '👤')

# Create handler instance
combat_handler = CombatHandler()

# Handler registration function
def register_handlers(application):
    application.add_handler(CommandHandler("attack", combat_handler.attack_command))
    application.add_handler(CommandHandler("attack_confirm", combat_handler.attack_confirm))
    application.add_handler(CommandHandler("attack_cancel", combat_handler.attack_cancel))

# Import asyncio for sleep functions
import asyncio
