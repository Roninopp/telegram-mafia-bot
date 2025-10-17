import random
from models.player import Player

class CombatCalculator:
    @staticmethod
    def calculate_damage(attacker: Player, defender: Player) -> int:
        """Calculate damage based on classes and levels"""
        base_damage = 10
        
        # Class bonuses
        class_bonuses = {
            'enforcer': 15,
            'hacker': 8,
            'smuggler': 10
        }
        
        # Level bonus
        level_bonus = attacker.level * 2
        
        # Random factor (80% to 120%)
        random_factor = random.uniform(0.8, 1.2)
        
        damage = int((base_damage + class_bonuses.get(attacker.character_class, 10) + level_bonus) * random_factor)
        
        return max(5, damage)  # Minimum 5 damage
    
    @staticmethod
    def calculate_escape_chance(attacker: Player, defender: Player) -> bool:
        """Calculate if defender can escape combat"""
        escape_chance = 0.3  # Base 30% chance
        
        # Smugglers have better escape chance
        if defender.character_class == 'smuggler':
            escape_chance += 0.2
        
        # Level difference affects escape chance
        level_diff = defender.level - attacker.level
        escape_chance += level_diff * 0.05
        
        return random.random() < escape_chance
    
    @staticmethod
    def calculate_rewards(attacker: Player, defender: Player, victory: bool) -> dict:
        """Calculate cash and reputation rewards"""
        if victory:
            # Winner gets cash from loser
            cash_stolen = min(defender.cash // 10, 500)  # Steal up to 10% of defender's cash, max 500
            reputation_gain = 5 + (defender.level // 2)
            
            return {
                'cash': cash_stolen,
                'reputation': reputation_gain,
                'experience': 10
            }
        else:
            # Loser still gets some experience
            return {
                'cash': 0,
                'reputation': -2,
                'experience': 5
            }
    
    @staticmethod
    def can_attack(attacker: Player, defender: Player) -> tuple[bool, str]:
        """Check if attack is possible"""
        if attacker.user_id == defender.user_id:
            return False, "❌ You can't attack yourself!"
        
        if attacker.energy < 10:
            return False, "❌ Not enough energy! You need 10 energy to attack."
        
        if defender.health <= 0:
            return False, "❌ This player is already defeated!"
        
        return True, "OK"

# Test the combat calculator
if __name__ == "__main__":
    print("✅ Combat calculator working!")
