#!/usr/bin/env python3
import logging
from core.bot import MafiaBot

def main():
    try:
        bot = MafiaBot()
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("💡 Make sure you have created a .env file with BOT_TOKEN!")

if __name__ == '__main__':
    main()
