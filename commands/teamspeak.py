# commands/teamspeak.py
import discord
from discord.ext import commands
from core.bot import AlbionGoldBot
import ts3
from datetime import timedelta

class TeamSpeak(commands.Cog):
    def __init__(self, bot: AlbionGoldBot):
        self.bot = bot
        self.ts_conn = None

    async def connect_ts(self):
        """Membuat koneksi ke server TeamSpeak"""
        try:
            self.ts_conn = ts3.query.TS3Connection(
                host=self.bot.config['ts_host'],
                port=self.bot.config.get('ts_port', 10011)  # Default port 10011
            )
            self.ts_conn.login(
                client_login_name=self.bot.config['ts_username'],
                client_login_password=self.bot.config['ts_password']
            )
            self.ts_conn.use(sid=self.bot.config.get('ts_virtualserver_id', 1))
            return True
        except Exception as e:
            self.bot.logger.error(f"TS3 Connection Error: {str(e)}")
            return False

    @commands.command()
    async def tsinfo(self, ctx):
        """Menampilkan informasi server TeamSpeak"""
        try:
            if not await self.connect_ts():
                return await ctx.send("❌ Gagal terhubung ke server TeamSpeak")
            
            server_info = self.ts_conn.serverinfo()
            client_list = self.ts_conn.clientlist()
            
            embed = discord.Embed(
                title=f"🔊 {server_info[0]['virtualserver_name']}",
                color=0x009999
            )
            
            # Format uptime
            uptime_seconds = int(server_info[0]['virtualserver_uptime'])
            uptime = str(timedelta(seconds=uptime_seconds))
            
            embed.add_field(
                name="Server Info",
                value=(
                    f"🆔 **Slot:** {server_info[0]['virtualserver_clientsonline']}"
                    f"/{server_info[0]['virtualserver_maxclients']}\n"
                    f"⏱ **Uptime:** {uptime}\n"
                    f"📁 **Channels:** {server_info[0]['virtualserver_channelsonline']}"
                ),
                inline=False
            )
            
            online_users = []
            for client in client_list:
                if client['client_type'] == '0':
                    channel_name = client.get('client_channel_name', 'Unknown Channel')
                    online_users.append(f"• {client['client_nickname']} ({channel_name})")
            
            embed.add_field(
                name=f"Pengguna Online ({len(online_users)})",
                value="\n".join(online_users[:15]) + ("\n..." if len(online_users) > 15 else "") if online_users else "Tidak ada pengguna online",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.bot.logger.error(f"TSInfo Error: {str(e)}")
            await ctx.send("❌ Gagal mengambil data server")
        finally:
            if self.ts_conn:
                self.ts_conn.quit()

async def setup(bot: AlbionGoldBot):
    await bot.add_cog(TeamSpeak(bot))