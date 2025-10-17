import random
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class NPC:
    name: str
    level: int
    health: int
    max_health: int
    character_class: str
    personality: str  # "aggressive", "defensive", "tricky"
    difficulty: str   # "easy", "medium", "hard", "boss"
    
    # Stats based on difficulty
    damage_multiplier: float = 1.0
    defense_multiplier: float = 1.0
    escape_chance: float = 0.1
    
    # Special abilities
    special_ability: str = None
    special_cooldown: int = 0
    
    def choose_action(self, player_level: int) -> str:
        """AI decision making based on personality"""
        if self.personality == "aggressive":
            choices = ["attack"] * 8 + ["special"] * 2
        elif self.personality == "defensive":
            choices = ["defend"] * 6 + ["attack"] * 4
        else:  # tricky
            choices = ["attack"] * 5 + ["special"] * 3 + ["defend"] * 2
        
        return random.choice(choices)
    
    def calculate_damage(self) -> int:
        """Calculate NPC damage with randomness"""
        base_damage = self.level * 5
        damage = int(base_damage * self.damage_multiplier * random.uniform(0.8, 1.2))
        return max(5, damage)
    
    def take_damage(self, damage: int) -> int:
        """Apply damage with defense calculation"""
        actual_damage = int(damage / self.defense_multiplier)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def should_escape(self) -> bool:
        """Check if NPC tries to escape"""
        return random.random() < self.escape_chance
    
    def get_rewards(self) -> Dict:
        """Rewards for defeating this NPC"""
        base_cash = self.level * 20
        base_reputation = self.level * 2
        
        if self.difficulty == "easy":
            return {"cash": base_cash, "reputation": base_reputation, "exp": 10}
        elif self.difficulty == "medium":
            return {"cash": base_cash * 2, "reputation": base_reputation * 2, "exp": 20}
        elif self.difficulty == "hard":
            return {"cash": base_cash * 3, "reputation": base_reputation * 3, "exp": 30}
        else:  # boss
            return {"cash": base_cash * 5, "reputation": base_reputation * 5, "exp": 50}

class NPCFactory:
    """Factory to create different types of NPCs"""
    
    @staticmethod
    def create_street_thug(level: int) -> NPC:
        names = ["Street Thug", "Alley Punk", "Backstreet Bully", "Rookie Gangster"]
        return NPC(
            name=random.choice(names),
            level=level,
            health=80 + (level * 5),
            max_health=80 + (level * 5),
            character_class="enforcer",
            personality="aggressive",
            difficulty="easy",
            damage_multiplier=0.8,
            defense_multiplier=0.9
        )
    
    @staticmethod
    def create_gang_member(level: int) -> NPC:
        names = ["Gang Member", "Mafia Soldier", "Crew Enforcer", "Syndicate Thug"]
        return NPC(
            name=random.choice(names),
            level=level + 1,
            health=100 + (level * 6),
            max_health=100 + (level * 6),
            character_class=random.choice(["enforcer", "smuggler"]),
            personality=random.choice(["aggressive", "defensive"]),
            difficulty="medium",
            damage_multiplier=1.0,
            defense_multiplier=1.0,
            special_ability="gang_backup"
        )
    
    @staticmethod
    def create_mafia_boss(level: int) -> NPC:
        bosses = [
            {"name": "Tony 'The Shark'", "class": "enforcer", "personality": "aggressive"},
            {"name": "Vinnie 'The Ghost'", "class": "smuggler", "personality": "tricky"},
            {"name": "Don 'The Brain'", "class": "hacker", "personality": "defensive"}
        ]
        boss = random.choice(bosses)
        return NPC(
            name=boss["name"],
            level=level + 3,
            health=150 + (level * 8),
            max_health=150 + (level * 8),
            character_class=boss["class"],
            personality=boss["personality"],
            difficulty="boss",
            damage_multiplier=1.5,
            defense_multiplier=1.3,
            escape_chance=0.05,
            special_ability="boss_rage"
        )
    
    @staticmethod
    def create_police_officer(level: int) -> NPC:
        ranks = ["Officer", "Detective", "Sergeant", "Lieutenant"]
        return NPC(
            name=f"{random.choice(ranks)} {random.choice(['Miller', 'Johnson', 'Davis', 'Rodriguez'])}",
            level=level + 2,
            health=120 + (level * 7),
            max_health=120 + (level * 7),
            character_class="enforcer",
            personality="defensive",
            difficulty="hard",
            damage_multiplier=1.2,
            defense_multiplier=1.1,
            special_ability="call_backup"
        )

# Test the NPC system
if __name__ == "__main__":
    print("🤖 NPC System Test:")
    thug = NPCFactory.create_street_thug(5)
    boss = NPCFactory.create_mafia_boss(10)
    print(f"✅ {thug.name} (Level {thug.level}) created!")
    print(f"✅ {boss.name} (Level {boss.level}) created!")
