# handlers/combat_integration.py
"""
COMBAT SYSTEM INTEGRATION
Connects the combat system to your main bot structure
"""

from core.database import Database
from handlers.combat_core import combat_core
from handlers.combat_handlers import get_combat_handlers
from handlers.animation import CombatAnimations
from handlers.npc import NPCFactory

class CombatSystem:
    """Main combat system integration class"""
    
    def __init__(self):
        self.db = Database()
        self.animations = CombatAnimations()
        self.core = combat_core
        self.handlers = get_combat_handlers()
        
        print("✅ Combat System Integrated Successfully!")
    
    def get_handlers(self):
        """Return all combat handlers for bot registration"""
        return self.handlers
    
    async def initialize_player_combat(self, user_id: int):
        """Initialize player for combat - called when character is created"""
        player = self.db.get_player(user_id)
        if player:
            # Ensure player has combat stats
            if not hasattr(player, 'health'):
                player.health = 100
            if not hasattr(player, 'energy'):
                player.energy = 50
            if not hasattr(player, 'level'):
                player.level = 1
            if not hasattr(player, 'gold'):
                player.gold = 100  # Starting gold
            if not hasattr(player, 'reputation'):
                player.reputation = 0
            
            self.db.save_player(player)
            return True
        return False
    
    async def get_player_combat_stats(self, user_id: int):
        """Get formatted combat stats for profile"""
        player = self.db.get_player(user_id)
        if not player:
            return None
        
        stats = f"""
⚔️ **Combat Stats** ⚔️

{self.animations.generate_health_bar(player.health)}
⚡ Energy: {player.energy}/50
⭐ Level: {player.level}
💰 Gold: {player.gold}
🎯 Reputation: {player.reputation}
🎭 Class: {player.character_class.title()}

**Combat Ready:** {'✅' if player.energy >= 10 else '❌'}
"""
        return stats
    
    async def process_energy_regen(self):
        """Process energy regeneration for all players"""
        # This would be called periodically (every hour)
        all_players = self.db.get_all_players()
        for player in all_players:
            if player.energy < 50:
                player.energy = min(50, player.energy + 5)
                self.db.save_player(player)
    
    async def award_victory_rewards(self, user_id: int, rewards: dict):
        """Award combat rewards to player"""
        player = self.db.get_player(user_id)
        if player:
            player.gold += rewards.get('cash', 0)
            player.reputation += rewards.get('reputation', 0)
            
            # Check for level up
            old_level = player.level
            exp_needed = player.level * 100
            # Simple level system - in real implementation, track XP properly
            if player.reputation >= exp_needed:
                player.level += 1
                player.reputation = 0  # Reset for next level
            
            self.db.save_player(player)
            
            # Return level up info if applicable
            if player.level > old_level:
                return {
                    'level_up': True,
                    'old_level': old_level,
                    'new_level': player.level,
                    'rewards': rewards
                }
            
            return {'level_up': False, 'rewards': rewards}
        return None

# Global combat system instance
combat_system = CombatSystem()

# Integration functions for your core/bot.py
def integrate_combat_system(application):
    """Integrate combat system into main bot - call this from core/bot.py"""
    try:
        # Add all combat handlers
        combat_handlers = combat_system.get_handlers()
        for handler in combat_handlers:
            application.add_handler(handler)
        
        print("🎯 Combat System: Handlers integrated successfully!")
        return True
    except Exception as e:
        print(f"❌ Combat System Integration Failed: {e}")
        return False

def get_combat_integration():
    """Return combat system for use in other modules"""
    return combat_system
