import os
import json
import logging
import discord
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class AlbionGoldBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            help_command=None
        )
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = self.load_config()
        self.setup_logger()
        
    def load_config(self):
        config_path = os.path.join(self.base_dir, "config", "default.json")
        
        if not os.path.exists(config_path):
            self.create_default_config(config_path)
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def create_default_config(self, path):
        default_config = {
            "api_url": "https://east.albion-online-data.com/api/v2/stats/gold",
            "konstanta_c": 30070000,
            "chart_days": 7,
            "max_history_days": 365
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)

    def setup_logger(self):
        self.logger = logging.getLogger('albion_bot')
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler = logging.FileHandler(
            os.path.join(self.base_dir, "logs", "bot.log"),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    async def setup_hook(self):
        await self.load_extensions()
        
    async def load_extensions(self):
        for extension in ["commands.general", "commands.live", "commands.history"]:
            try:
                await self.load_extension(extension)
                self.logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                self.logger.error(f"Failed to load {extension}: {str(e)}")

    async def on_ready(self):
        self.logger.info(f"Bot {self.user} is ready!")

if __name__ == "__main__":
    bot = AlbionGoldBot()
    bot.run(os.getenv("DISCORD_TOKEN"))