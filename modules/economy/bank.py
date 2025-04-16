import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.database import Database  # Importamos la DB

class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()  # Instancia de la base de datos

    # --- COMANDO: !info protec ---
    @commands.command(name="infoProtec")
    async def protection_info(self, ctx):
        """Muestra tiempo restante de protección y costo diario."""
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        # 1. Obtener datos del usuario y personajes
        user = self.db.get_user(user_id, server_id)
        characters = self.db.get_characters(user_id, server_id)
        total_value = sum(char["value"] for char in characters) if characters else 0

        # 2. Calcular tiempo restante y costo
        now = datetime.now()
        protection_until = datetime.fromisoformat(user["protection_until"]) if user["protection_until"] else now
        remaining_time = max(timedelta(0), protection_until - now)
        remaining_hours = remaining_time.total_seconds() / 3600

        # 3. Ajustar costo por reputación
        base_fee = total_value * 0.05
        fee_multiplier = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
        daily_fee = base_fee * fee_multiplier

        # 4. Embed de respuesta
        embed = discord.Embed(title="🛡️ Estado de Protección", color=0x00ff00)
        embed.add_field(name="💰 Valor de la cartera", value=f"{total_value} monedas", inline=False)
        embed.add_field(name="⏳ Tiempo restante", value=f"{remaining_hours:.1f} horas", inline=False)
        embed.add_field(name="💵 Costo por día", value=f"{daily_fee:.2f} monedas", inline=False)
        await ctx.send(embed=embed)

    # --- COMANDO: !pagar banco <días> ---
    @commands.command(name="pagarBanco")
    async def pay_protection(self, ctx, days: int):
        """Paga protección por X días (con ajuste de reputación)."""
        if days <= 0:
            await ctx.send("❌ ¡Debes especificar un número de días válido!")
            return

        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        # 1. Obtener datos
        user = self.db.get_user(user_id, server_id)
        characters = self.db.get_characters(user_id, server_id)
        total_value = sum(char["value"] for char in characters) if characters else 0

        # 2. Calcular costo total
        base_fee = total_value * 0.05
        fee_multiplier = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
        total_fee = base_fee * fee_multiplier * days

        # 3. Verificar fondos
        if user["coins"] < total_fee:
            await ctx.send(f"❌ No tienes suficientes monedas. Necesitas: {total_fee:.2f}")
            return

        # 4. Actualizar protección
        now = datetime.now()
        if user["protection_until"]:
            new_protection = datetime.fromisoformat(user["protection_until"]) + timedelta(days=days)
        else:
            new_protection = now + timedelta(days=days)

        self.db.update_user(
            user_id, server_id,
            {"protection_until": new_protection.isoformat(), "coins": user["coins"] - total_fee}
        )

        await ctx.send(f"✅ Protección pagada por {days} días. Costo: {total_fee:.2f} monedas.")

    # --- COMANDO: !inventario ---
    @commands.command(name="inventario")
    async def show_inventory(self, ctx):
        """Muestra personajes con imágenes y totales."""
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        # 1. Obtener personajes y total
        characters = self.db.get_characters(user_id, server_id)
        total_value = sum(char["value"] for char in characters) if characters else 0

        # 2. Crear embed
        embed = discord.Embed(
            title=f"📦 Inventario de {ctx.author.display_name}",
            description=f"**Valor total:** {total_value} monedas",
            color=0x00ff00
        )

        # 3. Añadir personajes (hasta 25, límite de Discord)
        for char in characters[:25]:
            embed.add_field(
                name=f"{char['name']} ⭐{'★' * char['rarity']}",
                value=f"Valor: {char['value']} monedas | {'🔒 Protegido' if char['protected'] else '⚠️ Desprotegido'}",
                inline=False
            )
            if char.get("image_url"):
                embed.set_thumbnail(url=char["image_url"])

        await ctx.send(embed=embed)

    # --- COMANDO: !perfil ---
    @commands.command(name="perfil")
    async def show_profile(self, ctx):
        """Muestra tu perfil con reputación, monedas y valor de personajes"""
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)

        # 1. Obtener datos del usuario y personajes
        user = self.db.get_user(user_id, server_id)
        characters = self.db.get_characters(user_id, server_id)
        total_characters_value = sum(char["value"] for char in characters) if characters else 0

        # 2. Determinar emoji de reputación
        if user["reputation"] > 0:
            rep_emoji = "😇"
        elif user["reputation"] < 0:
            rep_emoji = "😈"
        else:
            rep_emoji = "😐"

        # 3. Crear embed
        embed = discord.Embed(
            title=f"📊 Perfil de {ctx.author.display_name}",
            color=0x7289DA
        )
        embed.add_field(name="💎 Monedas", value=f"{user['coins']}", inline=True)
        embed.add_field(name="🎭 Reputación", value=f"{user['reputation']} pts {rep_emoji}", inline=True)
        embed.add_field(name="🧑‍🎨 Valor en personajes", value=f"{total_characters_value}", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bank(bot))