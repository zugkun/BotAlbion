import discord
from discord.ext import commands
from core.bot import AlbionGoldBot
from datetime import datetime
import humanize

class ServerStatus(commands.Cog):
    def __init__(self, bot: AlbionGoldBot):
        self.bot = bot

    @commands.command()
    async def serverstatus(self, ctx):
        """Menampilkan status server bot"""
        try:
            # Hitung statistik
            ping = round(self.bot.latency * 1000)
            guild_count = len(self.bot.guilds)
            member_count = sum(guild.member_count for guild in self.bot.guilds)
            
            # Format uptime
            uptime = humanize.naturaldelta(datetime.now() - self.bot.start_time)
            
            # Buat embed
            embed = discord.Embed(
                title="🖥 STATUS SERVER BOT ALBION GOLD",
                color=0x2ECC71,
                description=(
                    "**Statistik Sistem:**\n"
                    f"🏓 Ping: `{ping}ms`\n"
                    f"⏱ Uptime: `{uptime}`\n"
                    f"🌐 Server: `{guild_count}`\n"
                    f"👥 Total Pengguna: `{member_count:,}`"
                )
            )
            embed.set_footer(text="Developed by SANDWICH TECH")
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"ServerStatus error: {str(e)}")
            await ctx.send("🔥 Terjadi kesalahan sistem")

async def setup(bot: AlbionGoldBot):
    await bot.add_cog(ServerStatus(bot))