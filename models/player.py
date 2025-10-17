from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Player:
    user_id: int
    username: str
    first_name: str
    character_class: str = "unknown"
    level: int = 1
    cash: int = 1000
    health: int = 100
    energy: int = 50
    reputation: int = 0
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert player to dictionary for storage"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'character_class': self.character_class,
            'level': self.level,
            'cash': self.cash,
            'health': self.health,
            'energy': self.energy,
            'reputation': self.reputation,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create player from dictionary"""
        return cls(**data)
    
    def get_stats(self):
        """Get formatted player stats"""
        return f"""
👤 **{self.first_name}** ({self.character_class.title()})
⭐ Level: {self.level} | 💰 Cash: ${self.cash}
❤️ Health: {self.health} | ⚡ Energy: {self.energy}
🎯 Reputation: {self.reputation}
        """

# Test the player class
if __name__ == "__main__":
    test_player = Player(123, "ronin", "Ronin")
    print("✅ Player model working!")
    print(test_player.get_stats())
