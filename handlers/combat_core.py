# handlers/combat_core.py
from core.database import Database
from handlers.animation import CombatAnimations
from handlers.npc import NPCFactory, NPC
import random
import asyncio
from typing import Dict, List, Optional

class CombatCore:
    def __init__(self):
        self.db = Database()
        self.animations = CombatAnimations()
        self.active_battles = {}  # Track ongoing battles
        self.waiting_players = []  # Players waiting for PvP matches
    
    async def start_1v1_battle(self, player1_id: int, player2_id: Optional[int] = None, is_bot: bool = False):
        """Start a 1v1 battle - PvP or vs NPC"""
        player1 = self.db.get_player(player1_id)
        
        if not player1:
            return {"error": "Player not found"}
        
        if not player2_id and not is_bot:
            # Try to find PvP opponent first
            opponent = await self.find_pvp_opponent(player1_id)
            if opponent:
                return await self.execute_pvp_battle(player1, opponent)
            else:
                # No players found, use NPC
                return await self.execute_npc_battle(player1)
        elif is_bot:
            # Force NPC battle
            return await self.execute_npc_battle(player1)
        else:
            # Specific player battle
            player2 = self.db.get_player(player2_id)
            if player2:
                return await self.execute_pvp_battle(player1, player2)
            else:
                return {"error": "Opponent not found"}
    
    async def find_pvp_opponent(self, player_id: int):
        """Find online player with similar level - uses your waiting system"""
        player = self.db.get_player(player_id)
        
        if not player:
            return None
        
        # Add player to waiting list
        if player_id not in self.waiting_players:
            self.waiting_players.append(player_id)
        
        # Find best match (similar level)
        best_opponent = None
        best_level_diff = float('inf')
        
        for opponent_id in self.waiting_players:
            if opponent_id == player_id:
                continue
                
            opponent = self.db.get_player(opponent_id)
            if opponent and opponent.health > 0 and opponent.energy >= 10:
                level_diff = abs(player.level - opponent.level)
                if level_diff < best_level_diff:
                    best_opponent = opponent
                    best_level_diff = level_diff
        
        # Remove matched players from waiting list
        if best_opponent:
            self.waiting_players.remove(player_id)
            self.waiting_players.remove(best_opponent.user_id)
            return best_opponent
        
        return None
    
    async def execute_pvp_battle(self, player1, player2):
        """Execute player vs player battle with animations"""
        battle_id = f"pvp_{player1.user_id}_{player2.user_id}_{random.randint(1000,9999)}"
        
        self.active_battles[battle_id] = {
            'player1': player1,
            'player2': player2,
            'turn': 'player1',
            'type': 'pvp',
            'round': 1
        }
        
        # Use your epic animations
        intro_frames = self.animations.combat_intro(player1.first_name, player2.first_name)
        
        battle_data = {
            'battle_id': battle_id,
            'players': [player1, player2],
            'type': 'pvp',
            'intro_animation': intro_frames,
            'status': 'ready'
        }
        
        return battle_data
    
    async def execute_npc_battle(self, player):
        """Execute battle against your NPC system"""
        # Create NPC based on player level using your NPCFactory
        if player.level <= 5:
            npc = NPCFactory.create_street_thug(player.level)
        elif player.level <= 10:
            npc = NPCFactory.create_gang_member(player.level)
        elif player.level <= 15:
            npc = NPCFactory.create_police_officer(player.level)
        else:
            npc = NPCFactory.create_mafia_boss(player.level)
        
        battle_id = f"npc_{player.user_id}_{npc.name}_{random.randint(1000,9999)}"
        
        self.active_battles[battle_id] = {
            'player1': player,
            'npc': npc,
            'turn': 'player1',
            'type': 'pve',
            'round': 1
        }
        
        # Use your animations for NPC battle
        intro_frames = self.animations.combat_intro(player.first_name, npc.name)
        
        battle_data = {
            'battle_id': battle_id,
            'players': [player, npc],
            'type': 'pve',
            'intro_animation': intro_frames,
            'status': 'ready',
            'npc_data': {
                'name': npc.name,
                'level': npc.level,
                'health': npc.health,
                'max_health': npc.max_health,
                'personality': npc.personality,
                'difficulty': npc.difficulty
            }
        }
        
        return battle_data
    
    async def execute_player_turn(self, battle_id: str, action: str, target: str = None):
        """Execute player's turn in battle"""
        if battle_id not in self.active_battles:
            return {"error": "Battle not found"}
        
        battle = self.active_battles[battle_id]
        
        if battle['type'] == 'pvp':
            return await self._execute_pvp_turn(battle, action, target)
        else:
            return await self._execute_pve_turn(battle, action, target)
    
    async def _execute_pvp_turn(self, battle, action: str, target: str):
        """Execute turn in PvP battle"""
        player = battle['player1'] if battle['turn'] == 'player1' else battle['player2']
        opponent = battle['player2'] if battle['turn'] == 'player1' else battle['player1']
        
        # Execute action
        result = await self._process_action(player, opponent, action)
        
        # Switch turns
        battle['turn'] = 'player2' if battle['turn'] == 'player1' else 'player1'
        battle['round'] += 1
        
        # Check for battle end
        battle_result = self._check_battle_end(battle)
        if battle_result:
            await self._end_battle(battle, battle_result)
        
        return result
    
    async def _execute_pve_turn(self, battle, action: str, target: str):
        """Execute turn in PvE battle"""
        player = battle['player1']
        npc = battle['npc']
        
        # Player's turn
        player_result = await self._process_action(player, npc, action)
        
        # Check if NPC defeated
        if npc.health <= 0:
            battle_result = {'winner': 'player', 'type': 'victory'}
            rewards = npc.get_rewards()
            await self._end_battle(battle, battle_result, rewards)
            return {**player_result, 'battle_ended': True, 'rewards': rewards}
        
        # NPC's turn (AI decision)
        npc_action = npc.choose_action(player.level)
        npc_result = await self._process_npc_action(npc, player, npc_action)
        
        # Check if player defeated
        if player.health <= 0:
            battle_result = {'winner': 'npc', 'type': 'defeat'}
            await self._end_battle(battle, battle_result)
            return {**player_result, **npc_result, 'battle_ended': True}
        
        battle['round'] += 1
        
        return {**player_result, **npc_result, 'battle_ended': False}
    
    async def _process_action(self, attacker, defender, action: str):
        """Process combat action"""
        if action == "attack":
            damage = self._calculate_damage(attacker, defender)
            defender.health = max(0, defender.health - damage)
            
            # Use your damage animation
            damage_text = self.animations.damage_animation(damage, False)
            attack_animation = self.animations.class_specific_attack(attacker.first_name, getattr(attacker, 'character_class', 'enforcer'))
            
            return {
                'action': 'attack',
                'damage': damage,
                'animation': attack_animation,
                'damage_text': damage_text,
                'attacker_health': getattr(attacker, 'health', 'N/A'),
                'defender_health': defender.health
            }
        
        elif action == "special":
            # Special ability - to be implemented
            return {'action': 'special', 'message': 'Special attack!'}
        
        elif action == "defend":
            # Defense action - to be implemented
            return {'action': 'defend', 'message': 'Defending!'}
        
        elif action == "escape":
            escape_chance = 0.3  # 30% escape chance
            if random.random() < escape_chance:
                escape_frames = self.animations.escape_sequence(attacker.first_name)
                return {'action': 'escape', 'success': True, 'animation': escape_frames}
            else:
                return {'action': 'escape', 'success': False, 'message': 'Escape failed!'}
    
    async def _process_npc_action(self, npc, player, action: str):
        """Process NPC's AI action"""
        if action == "attack":
            damage = npc.calculate_damage()
            player.health = max(0, player.health - damage)
            
            damage_text = self.animations.damage_animation(damage, False)
            attack_animation = self.animations.class_specific_attack(npc.name, npc.character_class)
            
            return {
                'npc_action': 'attack',
                'npc_damage': damage,
                'npc_animation': attack_animation,
                'npc_damage_text': damage_text,
                'player_health': player.health
            }
        
        elif action == "special":
            # NPC special ability
            return {'npc_action': 'special', 'message': f'{npc.name} uses special ability!'}
        
        elif action == "defend":
            return {'npc_action': 'defend', 'message': f'{npc.name} defends!'}
    
    def _calculate_damage(self, attacker, defender):
        """Calculate damage between entities"""
        base_damage = random.randint(8, 15)
        
        # Level advantage
        attacker_level = getattr(attacker, 'level', 1)
        defender_level = getattr(defender, 'level', 1)
        level_bonus = max(0, attacker_level - defender_level) * 2
        
        return base_damage + level_bonus
    
    def _check_battle_end(self, battle):
        """Check if battle should end"""
        if battle['type'] == 'pvp':
            if battle['player1'].health <= 0:
                return {'winner': 'player2', 'type': 'victory'}
            elif battle['player2'].health <= 0:
                return {'winner': 'player1', 'type': 'victory'}
        else:
            if battle['player1'].health <= 0:
                return {'winner': 'npc', 'type': 'defeat'}
            elif battle['npc'].health <= 0:
                return {'winner': 'player', 'type': 'victory'}
        
        return None
    
    async def _end_battle(self, battle, result, rewards=None):
        """End battle and distribute rewards"""
        battle_id = None
        for bid, b in self.active_battles.items():
            if b == battle:
                battle_id = bid
                break
        
        if battle_id:
            del self.active_battles[battle_id]
        
        # Apply rewards to player
        if result['winner'] == 'player' and rewards:
            player = battle['player1']
            player.gold += rewards.get('cash', 0)
            player.reputation += rewards.get('reputation', 0)
            # Add experience to level system
            self.db.save_player(player)
        
        return result

# Global combat instance
combat_core = CombatCore()
