# combat/combat_core.py
from core.database import Database
from animation import CombatAnimations
import random
import asyncio

class CombatCore:
    def __init__(self):
        self.db = Database()
        self.animations = CombatAnimations()
        self.active_battles = {}  # Track ongoing battles
    
    async def start_1v1_battle(self, player1_id, player2_id=None, is_bot=False):
        """Start a 1v1 battle - PvP or vs Bot"""
        player1 = self.db.get_player(player1_id)
        
        if not player2_id and not is_bot:
            # Find real opponent
            opponent = await self.find_pvp_opponent(player1_id)
            if opponent:
                return await self.execute_pvp_battle(player1, opponent)
            else:
                # No players found, use bot
                return await self.execute_bot_battle(player1)
        elif is_bot:
            return await self.execute_bot_battle(player1)
        else:
            # Specific player battle
            player2 = self.db.get_player(player2_id)
            return await self.execute_pvp_battle(player1, player2)
    
    async def start_gang_war(self, gang1_id, gang2_id):
        """Start a 5v5 gang battle"""
        # This will connect to your future gang system
        pass
    
    async def find_pvp_opponent(self, player_id):
        """Find online player with similar level"""
        player = self.db.get_player(player_id)
        
        # Get all active players (excluding self) with similar level
        all_players = self.get_online_players()
        potential_opponents = [
            p for p in all_players 
            if p.user_id != player_id 
            and abs(p.level - player.level) <= 3
        ]
        
        return random.choice(potential_opponents) if potential_opponents else None
    
    async def execute_pvp_battle(self, player1, player2):
        """Execute player vs player battle with animations"""
        battle_id = f"{player1.user_id}_{player2.user_id}_{random.randint(1000,9999)}"
        self.active_battles[battle_id] = {
            'player1': player1,
            'player2': player2,
            'turn': 'player1'
        }
        
        # Use your epic animations
        intro_frames = self.animations.combat_intro(player1.first_name, player2.first_name)
        
        battle_data = {
            'battle_id': battle_id,
            'players': [player1, player2],
            'type': 'pvp',
            'intro_animation': intro_frames
        }
        
        return battle_data
    
    async def execute_bot_battle(self, player):
        """Execute battle against AI bot"""
        bot_level = max(1, player.level - 1 + random.randint(0, 2))
        bot_name = random.choice(['Shadow', 'Viper', 'Ghost', 'Phantom', 'Wraith'])
        
        bot_player = {
            'user_id': f"bot_{random.randint(1000,9999)}",
            'first_name': bot_name,
            'level': bot_level,
            'health': 80 + (bot_level * 2),
            'character_class': random.choice(['enforcer', 'hacker', 'smuggler']),
            'is_bot': True
        }
        
        battle_id = f"{player.user_id}_bot_{random.randint(1000,9999)}"
        
        # Use your animations for bot battle too
        intro_frames = self.animations.combat_intro(player.first_name, bot_name)
        
        battle_data = {
            'battle_id': battle_id,
            'players': [player, bot_player],
            'type': 'pve',
            'intro_animation': intro_frames
        }
        
        return battle_data
    
    def get_online_players(self):
        """Get list of players currently online"""
        # This will connect to your player session system
        # For now, return some mock data
        return []  # Will implement properly

# Global combat instance
combat_core = CombatCore()
