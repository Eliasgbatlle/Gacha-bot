import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.database import Database

class Bank(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = Database()

    @commands.slash_command(
        name="info_protec",
        description="Muestra tiempo restante de protección y costo diario."
    )
    async def protection_info(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        user = self.db.get_user(str(ctx.user.id), str(ctx.guild.id))
        chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
        total = sum(c["value"] for c in chars) if chars else 0

        now = datetime.now()
        until = datetime.fromisoformat(user["protection_until"]) if user["protection_until"] else now
        rem = max(timedelta(0), until - now)
        hours = rem.total_seconds() / 3600

        base = total * 0.05
        mult = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
        fee = base * mult

        embed = discord.Embed(title="🛡️ Protección", color=0x00ff00)
        embed.add_field("💰 Valor cartera", f"{total} monedas", inline=False)
        embed.add_field("⏳ Tiempo restante", f"{hours:.1f} horas", inline=False)
        embed.add_field("💵 Costo/día", f"{fee:.2f} monedas", inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="pagar_banco",
        description="Paga protección por X días (ajustado por reputación)."
    )
    async def pay_protection(self, ctx: discord.ApplicationContext, dias: int):
        if dias <= 0:
            return await ctx.respond("❌ Días inválidos.")
        user = self.db.get_user(str(ctx.user.id), str(ctx.guild.id))
        chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
        total = sum(c["value"] for c in chars) if chars else 0

        base = total * 0.05
        mult = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
        cost = base * mult * dias

        if user["coins"] < cost:
            return await ctx.respond(f"❌ Te faltan {cost - user['coins']:.2f} monedas.")
        now = datetime.now()
        new_until = (
            datetime.fromisoformat(user["protection_until"]) + timedelta(days=dias)
            if user["protection_until"] else now + timedelta(days=dias)
        )

        self.db.update_user(
            str(ctx.user.id), str(ctx.guild.id),
            {"protection_until": new_until.isoformat(),
             "coins": user["coins"] - cost}
        )
        await ctx.respond(f"✅ Pagaste {cost:.2f} monedas por {dias} días.")

    @commands.slash_command(
        name="inventario",
        description="Muestra tu inventario de personajes."
    )
    async def show_inventory(self, ctx: discord.ApplicationContext):
        chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
        total = sum(c["value"] for c in chars) if chars else 0

        embed = discord.Embed(
            title=f"📦 Inventario de {ctx.user.display_name}",
            description=f"Valor total: {total} monedas",
            color=0x00ff00
        )
        for c in chars[:25]:
            embed.add_field(
                name=f"{c['name']} ⭐{'★'*c['rarity']}",
                value=(
                    f"Valor: {c['value']} | "
                    f"{'🔒' if c['protected'] else '⚠️'}"
                ), inline=False
            )
            if c.get("image_url"):
                embed.set_thumbnail(url=c["image_url"])
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="perfil",
        description="Muestra tu perfil con reputación y monedas."
    )
    async def show_profile(self, ctx: discord.ApplicationContext):
        user = self.db.get_user(str(ctx.user.id), str(ctx.guild.id))
        chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
        total = sum(c["value"] for c in chars) if chars else 0
        emoji = "😇" if user["reputation"]>0 else "😈" if user["reputation"]<0 else "😐"

        embed = discord.Embed(title=f"📊 Perfil de {ctx.user.display_name}", color=0x7289DA)
        embed.add_field("💎 Monedas", user["coins"], inline=True)
        embed.add_field("🎭 Reputación", f"{user['reputation']} pts {emoji}", inline=True)
        embed.add_field("🧑‍🎨 Valor personajes", total, inline=True)
        await ctx.respond(embed=embed)

# — Setup Síncrono para py-cord —
def setup(bot: discord.Bot):
    bot.add_cog(Bank(bot))
    print("✅ Bank cog registrado")
