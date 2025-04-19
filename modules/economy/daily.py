import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.database import Database

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

class DailyReward(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @bot.slash_command(name="recompensa_diaria", description="🎁 Reclama tus monedas diarias")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.user.id)
        server_id = str(ctx.guild.id)
        user = self.db.get_user(user_id, server_id)

        # Verificar si ya reclamó hoy
        last_daily = datetime.fromisoformat(user["last_daily"] if "last_daily" in user else "2000-01-01T00:00:00")
        now = datetime.now()

        if (now - last_daily) < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_daily)
            await ctx.respond(f"⏳ Ya reclamaste hoy. Vuelve en {remaining}", ephemeral=True)
            return

        # Dar recompensa (500 monedas base + bonus por reputación)
        base_reward = 500
        bonus = int(base_reward * abs(float(user["reputation"]) * 0.001))
        total = base_reward + bonus

        self.db.update_user(
            user_id,
            server_id,
            {
                "coins": user["coins"] + total,
                "last_daily": now.isoformat()
            }
        )

        await ctx.respond(f"🎉 ¡Recompensa diaria de {total} monedas! (+{bonus} por reputación)")

def setup(bot):
    bot.add_cog(DailyReward(bot))