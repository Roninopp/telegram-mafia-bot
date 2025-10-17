import sqlite3
import json
from models.player import Player

class Database:
    def __init__(self, db_path="mafia_bot.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                character_class TEXT,
                level INTEGER DEFAULT 1,
                cash INTEGER DEFAULT 1000,
                health INTEGER DEFAULT 100,
                energy INTEGER DEFAULT 50,
                reputation INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def save_player(self, player: Player):
        """Save or update player data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO players 
            (user_id, username, first_name, character_class, level, cash, health, energy, reputation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player.user_id, player.username, player.first_name,
            player.character_class, player.level, player.cash,
            player.health, player.energy, player.reputation, player.created_at
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Player {player.first_name} saved to database!")
    
    def get_player(self, user_id: int) -> Player:
        """Get player data by user ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Convert row to dictionary
            player_data = {
                'user_id': row[0],
                'username': row[1],
                'first_name': row[2],
                'character_class': row[3],
                'level': row[4],
                'cash': row[5],
                'health': row[6],
                'energy': row[7],
                'reputation': row[8],
                'created_at': row[9]
            }
            return Player.from_dict(player_data)
        return None

# Test the database
if __name__ == "__main__":
    db = Database()
    print("✅ Database module working!")
