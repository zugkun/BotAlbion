# bot.py
import os
import json
import logging
import discord
import sys
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

# Tambahkan path project ke sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

class AlbionGoldBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            help_command=None,
            owner_id=1234567890  # Ganti dengan ID Discord Anda
        )
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = self.load_config()
        self.start_time = datetime.now()
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
        commands_dir = os.path.join(self.base_dir, "commands")
        
        if not os.path.exists(commands_dir):
            self.logger.error("❌ Folder commands tidak ditemukan!")
            return
        
        for filename in os.listdir(commands_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                extension_name = f"commands.{filename[:-3]}"
                try:
                    await self.load_extension(extension_name)
                    self.logger.info(f"✅ Loaded: {extension_name}")
                except Exception as e:
                    self.logger.error(f"❌ Gagal load {extension_name}: {str(e)}")

    async def on_ready(self):
        self.logger.info(f"🤖 Bot {self.user} aktif!")
        self.logger.info(f"⏱ Uptime: {datetime.now() - self.start_time}")

if __name__ == "__main__":
    bot = AlbionGoldBot()
    bot.run(os.getenv("DISCORD_TOKEN"))