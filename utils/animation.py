import random
import time
from typing import List

class CombatAnimations:
    @staticmethod
    def generate_health_bar(health: int, max_health: int = 100, bar_length: int = 15) -> str:
        """Generate a beautiful visual health bar with emojis"""
        percentage = health / max_health
        filled = int(percentage * bar_length)
        
        # Different colors based on health percentage
        if percentage > 0.7:
            filled_char = '🟩'  # Green
        elif percentage > 0.3:
            filled_char = '🟨'  # Yellow
        else:
            filled_char = '🟥'  # Red
            
        empty_char = '⬜'
        bar = filled_char * filled + empty_char * (bar_length - filled)
        return f"{bar} {health}/{max_health} ❤️"

    @staticmethod
    def combat_intro(attacker_name: str, defender_name: str) -> List[str]:
        """EPIC combat intro sequence with multiple frames"""
        return [
            f"🌃 *Night falls over the city...*",
            f"🔍 **{attacker_name}** spots their target...",
            f"🎯 **{defender_name}** senses danger...",
            f"⚡ **TENSION RISES** ⚡",
            f"🔥 **BATTLE BEGIN!** {attacker_name} vs {defender_name} 🔥"
        ]

    @staticmethod
    def class_specific_attack(attacker_name: str, character_class: str) -> str:
        """Special animated attacks for each class"""
        class_animations = {
            'enforcer': [
                f"💥 **{attacker_name}** lands a **DEVASTATING PUNCH!** 🤜💥",
                f"🔫 **{attacker_name}** unloads a **SHOTGUN BLAST!** 💥🔫", 
                f"💣 **{attacker_name}** throws a **GRENADE!** 🎯💣",
                f"🦾 **{attacker_name}** uses **BRUTE FORCE!** 💪✨"
            ],
            'hacker': [
                f"💻 **{attacker_name}** **HACKS THE SYSTEM!** 🖥️⚡",
                f"📡 **{attacker_name}** **JAMS COMMUNICATIONS!** 📶❌",
                f"🦠 **{attacker_name}** deploys **DIGITAL VIRUS!** 💾🔥",
                f"🔐 **{attacker_name}** **CRACKS DEFENSES!** 🛡️💥"
            ],
            'smuggler': [
                f"🚗 **{attacker_name}** performs **HIT-AND-RUN!** 🏎️💨",
                f"🎯 **{attacker_name}** makes **PRECISE STRIKE!** ✨🎯",
                f"💨 **{attacker_name}** uses **QUICK MOVES!** 🏃‍♂️⚡", 
                f"🛡️ **{attacker_name}** uses **IMPROVISED WEAPONS!** 🔧💥"
            ]
        }
        return random.choice(class_animations.get(character_class, class_animations['enforcer']))

    @staticmethod
    def damage_animation(damage: int, critical: bool = False) -> str:
        """Visual damage display"""
        if critical:
            return f"💥 **CRITICAL HIT!** {damage} damage! 💫✨"
        else:
            return f"⚡ **{damage} damage!** 💢"

    @staticmethod
    def victory_celebration(winner_name: str, cash_won: int) -> List[str]:
        """EPIC victory sequence"""
        return [
            f"🎆 **BATTLE END!** 🎆",
            f"⭐ **{winner_name}** **STANDS VICTORIOUS!** 🏆",
            f"💰 **LOOT:** ${cash_won} collected! 💵",
            f"🎉 **REPUTATION INCREASED!** 📈",
            f"✨ **The streets will remember this victory!** 🌃"
        ]

    @staticmethod
    def escape_sequence(escapee_name: str) -> List[str]:
        """Cool escape animation"""
        return [
            f"🚨 **{escapee_name}** tries to escape! 🏃‍♂️",
            f"💨 **GETAWAY IN PROGRESS...** 🌪️",
            f"🎯 **ESCAPE SUCCESSFUL!** ✨",
            f"🏙️ **{escapee_name}** vanishes into the city! 🌃"
        ]

    @staticmethod
    def level_up_animation(player_name: str, new_level: int) -> List[str]:
        """EPIC level up sequence"""
        return [
            f"✨ **LEVEL UP!** ✨",
            f"🌟 **{player_name}** reaches level **{new_level}!** 🎯",
            f"💪 **STATS INCREASED!** 📊",
            f"🎊 **NEW POWERS UNLOCKED!** 🔓",
            f"🏆 **You're moving up in the criminal world!** 🌃"
        ]

    @staticmethod
    def create_character_animation(class_name: str, player_name: str) -> str:
        """Special animation for character creation"""
        class_descriptions = {
            'enforcer': f"🎯 **{player_name}**, you are now an **ENFORCER!**\n💪 Brute strength and combat mastery!",
            'hacker': f"💻 **{player_name}**, you are now a **HACKER!**\n🖥️ Digital domination and tech skills!", 
            'smuggler': f"🚗 **{player_name}**, you are now a **SMUGGLER!**\n💨 Speed, stealth, and street smarts!"
        }
        return class_descriptions.get(class_name, "Welcome to the criminal world!")

    @staticmethod
    def territory_conquest(gang_name: str, territory: str) -> List[str]:
        """Animation for capturing territories"""
        return [
            f"🗺️ **TERRITORY CONQUEST!** 🗺️",
            f"🏢 **{gang_name}** moves into **{territory}**...",
            f"⚔️ **Establishing control...**",
            f"🎯 **TERRITORY CAPTURED!** 🏆",
            f"💰 **Weekly income increased!** 💵"
        ]

    @staticmethod
    def heist_animation(heist_name: str, success: bool, loot: int) -> List[str]:
        """EPIC heist sequence"""
        if success:
            return [
                f"🎭 **{heist_name.upper()} HEIST** 🎭",
                f"🕵️‍♂️ **Infiltration in progress...**",
                f"💰 **LOOT ACQUIRED: ${loot}** 💵",
                f"🚗 **GETAWAY CLEAN!** 🏎️",
                f"🎉 **HEIST SUCCESSFUL!** 🏆"
            ]
        else:
            return [
                f"🎭 **{heist_name.upper()} HEIST** 🎭", 
                f"🕵️‍♂️ **Infiltration in progress...**",
                f"🚨 **ALARM TRIGGERED!** 👮",
                f"💨 **ESCAPE UNDER FIRE!** 🔥",
                f"❌ **HEIST FAILED!** 😞"
            ]

    @staticmethod
    def boss_fight_intro(boss_name: str) -> List[str]:
        """EPIC boss fight introduction"""
        return [
            f"👑 **BOSS ENCOUNTER!** 👑",
            f"🌫️ A shadowy figure appears...",
            f"💀 **{boss_name.upper()}** reveals themselves!",
            f"⚡ **THE ULTIMATE CHALLENGE BEGINS!** ⚡"
        ]

    @staticmethod
    def generate_ascii_art(art_type: str) -> str:
        """Generate ASCII art for special moments"""
        arts = {
            'victory': """
            🏆 VICTORY 🏆
            ✨⭐✨⭐✨
            YOU WIN!
            ✨⭐✨⭐✨
            """,
            'defeat': """
            💀 DEFEAT 💀  
            ☠️⚰️☠️⚰️☠️
            TRY AGAIN!
            ☠️⚰️☠️⚰️☠️
            """,
            'mafia': """
            🤵 MAFIA WARS 🤵
            💰🔫💊🏢🚗
            Criminal Empire
            💰🔫💊🏢🚗
            """
        }
        return arts.get(art_type, "✨")

# Test the epic animations
if __name__ == "__main__":
    print("🎬 Testing EPIC Animations...")
    anim = CombatAnimations()
    
    # Test health bar
    print(anim.generate_health_bar(75))
    print(anim.generate_health_bar(25))
    
    # Test combat intro
    for frame in anim.combat_intro("Ronin", "Shadow"):
        print(frame)
    
    print("✅ EPIC Animations are ready to WOW players! 🎉")
