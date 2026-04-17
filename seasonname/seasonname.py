from redbot.core import commands, Config
import discord
import asyncio
from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))


class SeasonName(commands.Cog):
    """Đổi tên server theo mùa (chuẩn VN, chỉ đổi khi sang mùa)"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=987654321)

        default_guild = {
            "enabled": False,
            "last_season": None
        }

        self.config.register_guild(**default_guild)
        self.task = bot.loop.create_task(self.season_loop())

    def cog_unload(self):
        self.task.cancel()

    # ================= SEASON LOGIC =================
    def get_season(self):
        now = datetime.now(VN_TZ)
        month = now.month

        if month in [3, 4, 5]:
            return "spring", "🌸 Cafe Mùa Xuân"
        elif month in [6, 7, 8]:
            return "summer", "☀️ Cafe Mùa Hạ"
        elif month in [9, 10, 11]:
            return "autumn", "🍂 Cafe Mùa Thu"
        else:
            return "winter", "❄️ Cafe Mùa Đông"

    # ================= TIME WAIT =================
    async def wait_until_next_day(self):
        now = datetime.now(VN_TZ)
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        wait_time = (tomorrow - now).total_seconds()
        await asyncio.sleep(wait_time)

    # ================= MAIN LOOP =================
    async def season_loop(self):
        await self.bot.wait_until_ready()

        while True:
            current_season, name = self.get_season()

            for guild in self.bot.guilds:
                data = await self.config.guild(guild).all()

                if not data["enabled"]:
                    continue

                if data["last_season"] != current_season:
                    try:
                        if guild.name != name:
                            await guild.edit(name=name)

                        await self.config.guild(guild).last_season.set(current_season)

                        print(f"[SeasonName] Đã đổi tên {guild.name}")

                    except discord.Forbidden:
                        print(f"[SeasonName] Thiếu quyền ở {guild.name}")
                    except Exception as e:
                        print(f"[SeasonName] Lỗi: {e}")

            await self.wait_until_next_day()

    # ================= COMMAND =================
    @commands.group()
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def seasonname(self, ctx):
        """Quản lý đổi tên theo mùa"""
        pass

    @seasonname.command()
    async def on(self, ctx):
        """Bật"""
        await self.config.guild(ctx.guild).enabled.set(True)
        await ctx.send("🌸 Đã bật đổi tên server theo mùa")

    @seasonname.command()
    async def off(self, ctx):
        """Tắt"""
        await self.config.guild(ctx.guild).enabled.set(False)
        await ctx.send("❌ Đã tắt")

    @seasonname.command()
    async def status(self, ctx):
        """Xem trạng thái"""
        data = await self.config.guild(ctx.guild).all()
        season, name = self.get_season()

        await ctx.send(
            f"Trạng thái: {'ON' if data['enabled'] else 'OFF'}\n"
            f"Mùa hiện tại: {name}\n"
            f"Last saved: {data['last_season']}"
          )
