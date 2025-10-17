from core.database import Database
from models.player import Player

db = Database()

class ShopCore:
    def __init__(self):
        self.categories = {
            "weapons": {
                "name": "🔫 Weapons",
                "description": "Upgrade your firepower",
                "items": {
                    "brass_knuckles": {
                        "name": "🔩 Brass Knuckles",
                        "description": "Simple but effective",
                        "price": 100,
                        "attack_bonus": 3,
                        "class_restriction": ["enforcer"],
                        "level_required": 1
                    },
                    "baseball_bat": {
                        "name": "⚾ Baseball Bat",
                        "description": "Classic intimidation tool",
                        "price": 250,
                        "attack_bonus": 5,
                        "class_restriction": ["enforcer"],
                        "level_required": 3
                    },
                    "encrypted_laptop": {
                        "name": "💻 Encrypted Laptop",
                        "description": "For cyber operations",
                        "price": 150,
                        "intelligence_bonus": 3,
                        "class_restriction": ["hacker"],
                        "level_required": 1
                    },
                    "silenced_engine": {
                        "name": "🔇 Silenced Engine",
                        "description": "Move without being detected",
                        "price": 200,
                        "stealth_bonus": 3,
                        "class_restriction": ["smuggler"],
                        "level_required": 2
                    }
                }
            },
            "consumables": {
                "name": "💊 Consumables", 
                "description": "Temporary boosts and healing",
                "items": {
                    "health_pack": {
                        "name": "❤️ Health Pack",
                        "description": "Restore 30 HP",
                        "price": 50,
                        "health_restore": 30,
                        "class_restriction": None,
                        "level_required": 1
                    },
                    "energy_drink": {
                        "name": "⚡ Energy Drink", 
                        "description": "Restore 20 Energy",
                        "price": 40,
                        "energy_restore": 20,
                        "class_restriction": None,
                        "level_required": 1
                    }
                }
            }
        }
    
    def get_shop_categories(self):
        """Return available shop categories"""
        return self.categories
    
    def get_category_items(self, category):
        """Return items for a specific category"""
        return self.categories.get(category, {}).get("items", {})
    
    def can_player_afford(self, player, item_price):
        """Check if player has enough gold"""
        return player.gold >= item_price
    
    def meets_requirements(self, player, item_data):
        """Check if player meets item requirements"""
        # Check level
        if player.level < item_data.get("level_required", 1):
            return False, f"Level {item_data['level_required']} required"
        
        # Check class restriction
        class_restriction = item_data.get("class_restriction")
        if class_restriction and player.character_class not in class_restriction:
            return False, f"Only for {', '.join(class_restriction)} class"
        
        return True, "Can purchase"
    
    def purchase_item(self, user_id, category, item_id):
        """Process item purchase"""
        player = db.get_player(user_id)
        if not player:
            return False, "Player not found"
        
        category_data = self.categories.get(category)
        if not category_data:
            return False, "Category not found"
        
        item_data = category_data["items"].get(item_id)
        if not item_data:
            return False, "Item not found"
        
        # Check requirements
        can_purchase, requirement_msg = self.meets_requirements(player, item_data)
        if not can_purchase:
            return False, requirement_msg
        
        # Check affordability
        if not self.can_player_afford(player, item_data["price"]):
            return False, "Not enough gold"
        
        # Process purchase
        player.gold -= item_data["price"]
        
        # Apply item effects
        purchase_message = self._apply_item_effects(player, item_data, item_id)
        
        # Save player
        db.save_player(player)
        
        return True, purchase_message
    
    def _apply_item_effects(self, player, item_data, item_id):
        """Apply item effects to player"""
        message_parts = [f"✅ Purchased {item_data['name']}!"]
        
        # Apply stat bonuses for permanent items
        if "attack_bonus" in item_data:
            player.attack += item_data["attack_bonus"]
            message_parts.append(f"⚔️ Attack +{item_data['attack_bonus']}")
        
        if "intelligence_bonus" in item_data:
            player.intelligence += item_data["intelligence_bonus"]
            message_parts.append(f"🧠 Intelligence +{item_data['intelligence_bonus']}")
            
        if "stealth_bonus" in item_data:
            player.stealth += item_data["stealth_bonus"]
            message_parts.append(f"👤 Stealth +{item_data['stealth_bonus']}")
        
        # Apply consumable effects
        if "health_restore" in item_data:
            player.health = min(100, player.health + item_data["health_restore"])
            message_parts.append(f"❤️ Health +{item_data['health_restore']}")
            
        if "energy_restore" in item_data:
            player.energy = min(50, player.energy + item_data["energy_restore"])
            message_parts.append(f"⚡ Energy +{item_data['energy_restore']}")
        
        message_parts.append(f"💰 Remaining Gold: {player.gold}")
        return "\n".join(message_parts)

# Global shop instance
shop_core = ShopCore()
