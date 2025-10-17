#!/usr/bin/env python3
import sys
import os
import logging

# FIX: Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    try:
        from core.bot import MafiaBot
        bot = MafiaBot()
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("💡 Make sure you have created a .env file with BOT_TOKEN!")

if __name__ == '__main__':
    main()
