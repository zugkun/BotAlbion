from core.bot import AlbionGoldBot
import os

if __name__ == "__main__":
    bot = AlbionGoldBot()
    bot.run(os.getenv("DISCORD_TOKEN"))