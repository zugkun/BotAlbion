# 📁 commands/history.py
import discord
import requests
import matplotlib.pyplot as plt
import io
from discord.ext import commands
from datetime import datetime, timedelta
from core.bot import AlbionGoldBot

class HistoryCommands(commands.Cog):
    def __init__(self, bot: AlbionGoldBot):
        self.bot = bot
        self.history_messages = {}
        self.date_format_api = "%Y-%m-%d"
        self.max_fallback_days = 14  # Maksimal fallback 2 minggu

    async def fetch_available_data(self, target_date: datetime):
        """Cari data yang tersedia dengan rentang dinamis"""
        for days_back in range(0, self.max_fallback_days + 1):
            current_date = target_date - timedelta(days=days_back)
            start_date = current_date - timedelta(days=6)  # Coba 7 hari dari tanggal mundur
            
            url = f"{self.bot.config['api_url']}?date={start_date.strftime(self.date_format_api)}&end_date={current_date.strftime(self.date_format_api)}"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data, current_date
        return None, None

    async def process_data(self, raw_data):
        """Proses data mentah menjadi format yang bisa digunakan"""
        processed = []
        for entry in raw_data:
            try:
                time = datetime.strptime(entry['timestamp'], "%Y-%m-%dT%H:%M:%S")
                price = int(entry['price'])
                processed.append((time, price))
            except (KeyError, ValueError):
                continue
        return sorted(processed, key=lambda x: x[0])

    async def generate_adaptive_chart(self, processed_data, effective_date):
        """Buat grafik dengan data yang tersedia"""
        if len(processed_data) == 0:
            return None
            
        dates, prices = zip(*processed_data)
        
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Tentukan jenis chart berdasarkan jumlah data
        if len(processed_data) > 1:
            ax.plot(dates, prices, 'g-o', linewidth=2, markersize=8)
        else:
            ax.scatter(dates, prices, color='#2ecc71', s=200, zorder=2)
            ax.axhline(prices[0], color='#2ecc71', linestyle='--', alpha=0.5, zorder=1)
        
        # Format sumbu
        date_format = "%d %b" if len(processed_data) <= 7 else "%b %Y"
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter(date_format))
        
        ax.set_title(
            f"TREND HARGA ({len(processed_data)} Hari Terakhir)",
            pad=20,
            fontsize=14,
            fontweight='bold'
        )
        ax.set_xlabel("Tanggal", fontsize=12)
        ax.set_ylabel("Harga Silver", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf

    async def create_embed(self, processed_data, effective_date):
        """Buat embed dengan informasi yang sesuai"""
        if not processed_data:
            return None
            
        latest_date, latest_price = processed_data[-1]
        nilai_rupiah = self.bot.config['konstanta_c'] / latest_price
        
        embed = discord.Embed(
            title=f"📊 DATA HISTORIS - {effective_date.strftime('%d %b %Y')}",
            color=0x2ECC71,
            description=(
                f"**Menampilkan {len(processed_data)} hari data terakhir yang tersedia**\n"
                "⬅️ Hari Sebelumnya | ⏺️ Hari Ini | ➡️ Hari Berikutnya\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        )
        
        embed.add_field(
            name="🪙 Nilai Tukar Terakhir",
            value=f"```1 Gold = {latest_price:,} Silver```",
            inline=False
        )
        
        embed.add_field(
            name="🇮🇩 Konversi Rupiah",
            value=f"```1 Juta Silver = Rp {nilai_rupiah:,.2f}```",
            inline=False
        )
        
        if len(processed_data) < 7:
            embed.add_field(
                name="⚠️ Catatan",
                value="Data historis terbatas, grafik mungkin tidak lengkap",
                inline=False
            )
            
        return embed

    @commands.command()
    async def history(self, ctx):
        """Tampilkan data historis terbaik yang tersedia"""
        try:
            processing_msg = await ctx.send("🔄 Mencari data terbaru yang tersedia...")
            
            # Cari data terbaik
            raw_data, effective_date = await self.fetch_available_data(datetime.now())
            if not raw_data:
                await processing_msg.edit(content="⚠️ Tidak ada data yang tersedia selama 2 minggu terakhir")
                return
                
            processed_data = await self.process_data(raw_data)
            chart_buffer = await self.generate_adaptive_chart(processed_data, effective_date)
            
            if not chart_buffer:
                await processing_msg.edit(content="⚠️ Gagal memproses data yang tersedia")
                return
                
            # Buat dan kirim embed
            embed = await self.create_embed(processed_data, effective_date)
            await processing_msg.delete()
            
            message = await ctx.send(
                embed=embed,
                file=discord.File(chart_buffer, filename="chart.png")
            )
            
            # Tambahkan kontrol navigasi
            for reaction in ['⬅️', '⏺️', '➡️']:
                await message.add_reaction(reaction)
                
            # Simpan state
            self.history_messages[message.id] = {
                'date': effective_date,
                'data': processed_data
            }
            
        except Exception as e:
            self.bot.logger.error(f"History error: {str(e)}")
            await ctx.send("🔥 Terjadi kesalahan saat memproses permintaan")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle navigasi dengan sistem adaptif"""
        if user.bot or reaction.message.id not in self.history_messages:
            return
            
        message = reaction.message
        entry = self.history_messages[message.id]
        
        try:
            # Tentukan arah navigasi
            current_date = entry['date']
            if str(reaction.emoji) == '⬅️':
                new_date = current_date - timedelta(days=1)
            elif str(reaction.emoji) == '➡️':
                new_date = current_date + timedelta(days=1)
            elif str(reaction.emoji) == '⏺️':
                new_date = datetime.now()
            else:
                return
                
            # Cari data baru
            raw_data, effective_date = await self.fetch_available_data(new_date)
            if not raw_data:
                await reaction.remove(user)
                return
                
            processed_data = await self.process_data(raw_data)
            chart_buffer = await self.generate_adaptive_chart(processed_data, effective_date)
            
            if chart_buffer:
                embed = await self.create_embed(processed_data, effective_date)
                await message.edit(
                    embed=embed,
                    attachments=[discord.File(chart_buffer, filename="chart.png")]
                )
                self.history_messages[message.id] = {
                    'date': effective_date,
                    'data': processed_data
                }
                
            await reaction.remove(user)
            
        except Exception as e:
            self.bot.logger.error(f"Reaction error: {str(e)}")

async def setup(bot: AlbionGoldBot):
    await bot.add_cog(HistoryCommands(bot))