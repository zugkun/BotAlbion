import discord
import requests
from discord.ext import commands
from datetime import datetime
from core.bot import AlbionGoldBot

class General(commands.Cog):
    def __init__(self, bot: AlbionGoldBot):
        self.bot = bot

    @commands.command()
    async def gold(self, ctx):
        """Menampilkan harga gold terkini"""
        try:
            # Ambil data dari API
            response = requests.get(f"{self.bot.config['api_url']}?count=1")
            if response.status_code != 200:
                return await ctx.send("⚠️ Gagal terhubung ke server")
            
            data = response.json()
            if not data or len(data) < 1:
                return await ctx.send("⚠️ Data tidak tersedia")
                
            latest = data[0]
            price = latest.get('price')
            timestamp_str = latest.get('timestamp')
            
            if not price or not timestamp_str:
                return await ctx.send("⚠️ Format data tidak valid")

            # Konversi waktu
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return await ctx.send("⚠️ Format waktu tidak valid")

            # Hitung konversi
            nilai_rupiah = self.bot.config['konstanta_c'] / price
            
            # Buat embed
            embed = discord.Embed(
                title="💵 HARGA GOLD TERKINI",
                color=0xF1C40F,
                description=f"Update terakhir: {timestamp.strftime('%d/%m/%Y %H:%M UTC')}"
            )
            embed.add_field(
                name="Nilai Tukar", 
                value=(
                    f"🪙 1 Gold = {price:,} Silver\n"
                    f"🇮🇩 1M Silver = Rp {nilai_rupiah:,.2f}"
                ),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"Gold error: {str(e)}")
            await ctx.send("🔥 Terjadi kesalahan sistem")

    @commands.command()
    async def help(self, ctx):
        """Menampilkan menu bantuan"""
        embed = discord.Embed(
            title="📚 BANTUAN BOT ALBION GOLD",
            color=0x7289DA,
            description=(
                "**Daftar Perintah:**\n"
                "```"
                "!gold   - Tampilkan harga terkini\n"
                "!live   - Live update (admin only)\n"
                "!history- Riwayat harga 7 hari\n"
                "!help   - Tampilkan menu ini\n"
                "```"
            )
        )
        embed.set_footer(text="Developed by SANDWICH TECH")
        await ctx.send(embed=embed)

async def setup(bot: AlbionGoldBot):
    await bot.add_cog(General(bot))