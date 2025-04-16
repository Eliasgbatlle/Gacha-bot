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
        """
        Muestra tiempo restante de protección y costo diario.
        """
        try:
            user = self.db.get_user(str(ctx.user.id), str(ctx.guild.id))
            chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
            total = sum(c["value"] for c in chars) if chars else 0

            now = datetime.now()
            until = datetime.fromisoformat(user.get("protection_until")) if user.get("protection_until") else now
            rem = max(timedelta(0), until - now)
            hours = rem.total_seconds() / 3600

            base = total * 0.05
            mult = 0.85 if user.get("reputation", 0) > 0 else 1.15 if user.get("reputation", 0) < 0 else 1.0
            fee = base * mult

            embed = discord.Embed(title="🛡️ Estado de Protección", color=0x00ff00)
            embed.add_field(name="💰 Valor cartera", value=f"{total} monedas", inline=False)
            embed.add_field(name="⏳ Tiempo restante", value=f"{hours:.1f} horas", inline=False)
            embed.add_field(name="💵 Costo/día", value=f"{fee:.2f} monedas", inline=False)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"❌ Error al obtener información: {e}")

    @commands.slash_command(
        name="pagar_banco",
        description="Paga protección por X días (ajustado por reputación)."
    )
    async def pay_protection(self, ctx: discord.ApplicationContext, dias: int):
        """
        Paga la cuota de protección según los días indicados.
        """
        if dias <= 0:
            return await ctx.respond("❌ Debes indicar un número de días válido.")
        try:
            user = self.db.get_user(str(ctx.user.id), str(ctx.guild.id))
            chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
            total = sum(c["value"] for c in chars) if chars else 0

            base = total * 0.05
            mult = 0.85 if user.get("reputation", 0) > 0 else 1.15 if user.get("reputation", 0) < 0 else 1.0
            cost = base * mult * dias

            if user.get("coins", 0) < cost:
                return await ctx.respond(f"❌ Te faltan {cost - user.get('coins', 0):.2f} monedas.")

            now = datetime.now()
            new_until = (
                datetime.fromisoformat(user.get("protection_until")) + timedelta(days=dias)
                if user.get("protection_until") else now + timedelta(days=dias)
            )
            self.db.update_user(
                str(ctx.user.id), str(ctx.guild.id),
                {"protection_until": new_until.isoformat(), "coins": user.get("coins", 0) - cost}
            )
            await ctx.respond(f"✅ Pagaste {cost:.2f} monedas por {dias} días.")
        except Exception as e:
            await ctx.respond(f"❌ Error al pagar protección: {e}")

    @commands.slash_command(
        name="inventario",
        description="Muestra tu inventario de personajes."
    )
    async def show_inventory(self, ctx: discord.ApplicationContext):
        """
        Muestra los personajes del usuario con su valor y estado.
        """
        try:
            chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
            total = sum(c["value"] for c in chars) if chars else 0

            embed = discord.Embed(
                title=f"📦 Inventario de {ctx.user.display_name}",
                description=f"**Valor total:** {total} monedas",
                color=0x00ff00
            )
            for c in chars[:25]:
                embed.add_field(
                    name=f"{c['name']} ⭐{'★'*c['rarity']}",
                    value=(
                        f"Valor: {c['value']} monedas | "
                        f"{'🔒 Protegido' if c.get('protected') else '⚠️ Desprotegido'}"
                    ), inline=False
                )
                if c.get("image_url"):
                    embed.set_thumbnail(url=c["image_url"])
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"❌ Error al mostrar inventario: {e}")

    @commands.slash_command(
        name="perfil",
        description="Muestra tu perfil con reputación, monedas y valor en personajes."
    )
    async def show_profile(self, ctx: discord.ApplicationContext):
        """
        Muestra los datos de perfil: monedas, reputación y valor de personajes.
        """
        try:
            user = self.db.get_user(str(ctx.user.id), str(ctx.guild.id))
            chars = self.db.get_characters(str(ctx.user.id), str(ctx.guild.id))
            total = sum(c["value"] for c in chars) if chars else 0

            rep = user.get("reputation", 0)
            emoji = "😇" if rep > 0 else "😈" if rep < 0 else "😐"

            embed = discord.Embed(
                title=f"📊 Perfil de {ctx.user.display_name}",
                color=0x7289DA
            )
            embed.add_field(name="💎 Monedas", value=f"{user.get('coins', 0)}", inline=True)
            embed.add_field(name="🎭 Reputación", value=f"{rep} pts {emoji}", inline=True)
            embed.add_field(name="🧑‍🎨 Valor personajes", value=f"{total}", inline=True)
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"❌ Error al mostrar perfil: {e}")

# Setup síncrono para py-cord
def setup(bot: discord.Bot):
    bot.add_cog(Bank(bot))
    print("✅ Bank cog registrado")
