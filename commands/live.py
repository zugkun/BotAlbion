import discord
import requests
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from core.bot import AlbionGoldBot

class LiveCommands(commands.Cog):
    def __init__(self, bot: AlbionGoldBot):
        self.bot = bot
        self.active_sessions = {}

    async def update_live_message(self, message):
        try:
            while True:
                response = requests.get(f"{self.bot.config['api_url']}?count=1")
                data = response.json()
                
                if data and len(data) > 0:
                    latest = data[0]
                    price = latest['price']
                    time = datetime.strptime(latest['timestamp'], "%Y-%m-%dT%H:%M:%S")
                    nilai_rupiah = self.bot.config['konstanta_c'] / price
                    
                    embed = discord.Embed(
                        title="📊 LIVE UPDATE",
                        color=0x00FF00,
                        description=f"Update terakhir: {time.strftime('%H:%M:%S')}"
                    )
                    embed.add_field(name="Harga Silver", value=f"🪙 {price:,}", inline=False)
                    embed.add_field(name="Konversi Rupiah", value=f"🇮🇩 Rp {nilai_rupiah:,.2f}", inline=False)
                    
                    await message.edit(embed=embed)
                
                await asyncio.sleep(300)  # Update setiap 5 menit
                
        except Exception as e:
            self.bot.logger.error(f"Live session error: {str(e)}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def live(self, ctx, channel: discord.TextChannel = None):
        """Mulai live update di channel tertentu"""
        if not channel:
            return await ctx.send("❌ Harap tag channel yang valid!")
            
        try:
            message = await channel.send("🔄 Memulai live session...")
            task = self.bot.loop.create_task(self.update_live_message(message))
            self.active_sessions[channel.id] = task
            await ctx.send(f"✅ Live session aktif di {channel.mention}")
            
        except Exception as e:
            await ctx.send("⚠️ Gagal memulai live session")
            self.bot.logger.error(f"Live start error: {str(e)}")

async def setup(bot: AlbionGoldBot):
    await bot.add_cog(LiveCommands(bot))