import discord
from discord.ext import commands
from discord import ApplicationContext
from datetime import datetime, timedelta
from utils.database import Database

class Bank(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = Database()

    # --- SLASH COMMAND: /info_protec ---
    @discord.slash_command(name="info_protec", description="Muestra tiempo restante de protección y costo diario.")
    async def protection_info(self, ctx: ApplicationContext):
        await ctx.defer()  # Opcional: si toma tiempo, evita timeout

        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        user = self.db.get_user(user_id, server_id)
        characters = self.db.get_characters(user_id, server_id)
        total_value = sum(char["value"] for char in characters) if characters else 0

        now = datetime.now()
        protection_until = datetime.fromisoformat(user["protection_until"]) if user["protection_until"] else now
        remaining_time = max(timedelta(0), protection_until - now)
        remaining_hours = remaining_time.total_seconds() / 3600

        base_fee = total_value * 0.05
        fee_multiplier = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
        daily_fee = base_fee * fee_multiplier

        embed = discord.Embed(title="🛡️ Estado de Protección", color=0x00ff00)
        embed.add_field(name="💰 Valor de la cartera", value=f"{total_value} monedas", inline=False)
        embed.add_field(name="⏳ Tiempo restante", value=f"{remaining_hours:.1f} horas", inline=False)
        embed.add_field(name="💵 Costo por día", value=f"{daily_fee:.2f} monedas", inline=False)
        await ctx.respond(embed=embed)

    # --- SLASH COMMAND: /pagar_banco ---
    @discord.slash_command(name="pagar_banco", description="Paga protección por X días (ajustado por reputación).")
    async def pay_protection(self, ctx: ApplicationContext, dias: int):
        if dias <= 0:
            await ctx.respond("❌ ¡Debes especificar un número de días válido!")
            return

        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        user = self.db.get_user(user_id, server_id)
        characters = self.db.get_characters(user_id, server_id)
        total_value = sum(char["value"] for char in characters) if characters else 0

        base_fee = total_value * 0.05
        fee_multiplier = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
        total_fee = base_fee * fee_multiplier * dias

        if user["coins"] < total_fee:
            await ctx.respond(f"❌ No tienes suficientes monedas. Necesitas: {total_fee:.2f}")
            return

        now = datetime.now()
        if user["protection_until"]:
            new_protection = datetime.fromisoformat(user["protection_until"]) + timedelta(days=dias)
        else:
            new_protection = now + timedelta(days=dias)

        self.db.update_user(
            user_id, server_id,
            {"protection_until": new_protection.isoformat(), "coins": user["coins"] - total_fee}
        )

        await ctx.respond(f"✅ Protección pagada por {dias} días. Costo: {total_fee:.2f} monedas.")

    # --- SLASH COMMAND: /inventario ---
    @discord.slash_command(name="inventario", description="Muestra personajes con imágenes y totales.")
    async def show_inventory(self, ctx: ApplicationContext):
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        characters = self.db.get_characters(user_id, server_id)
        total_value = sum(char["value"] for char in characters) if characters else 0

        embed = discord.Embed(
            title=f"📦 Inventario de {ctx.author.display_name}",
            description=f"**Valor total:** {total_value} monedas",
            color=0x00ff00
        )

        for char in characters[:25]:
            embed.add_field(
                name=f"{char['name']} ⭐{'★' * char['rarity']}",
                value=f"Valor: {char['value']} monedas | {'🔒 Protegido' if char['protected'] else '⚠️ Desprotegido'}",
                inline=False
            )
            if char.get("image_url"):
                embed.set_thumbnail(url=char["image_url"])

        await ctx.respond(embed=embed)

    # --- SLASH COMMAND: /perfil ---
    @discord.slash_command(name="perfil", description="Muestra tu perfil con reputación, monedas y valor.")
    async def show_profile(self, ctx: ApplicationContext):
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        user = self.db.get_user(user_id, server_id)
        characters = self.db.get_characters(user_id, server_id)
        total_characters_value = sum(char["value"] for char in characters) if characters else 0

        if user["reputation"] > 0:
            rep_emoji = "😇"
        elif user["reputation"] < 0:
            rep_emoji = "😈"
        else:
            rep_emoji = "😐"

        embed = discord.Embed(
            title=f"📊 Perfil de {ctx.author.display_name}",
            color=0x7289DA
        )
        embed.add_field(name="💎 Monedas", value=f"{user['coins']}", inline=True)
        embed.add_field(name="🎭 Reputación", value=f"{user['reputation']} pts {rep_emoji}", inline=True)
        embed.add_field(name="🧑‍🎨 Valor en personajes", value=f"{total_characters_value}", inline=True)
        
        await ctx.respond(embed=embed)

# CORRECTO: esto se espera por main.py
async def setup(bot):
    await bot.add_cog(Bank(bot))
