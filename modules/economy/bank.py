import discord
import textwrap
from discord import File, ButtonStyle
from discord.ext import commands
from datetime import datetime, timedelta
from utils.database import Database
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import sqlite3

def obtener_anime(nombre_personaje):
    """Obtiene la serie de un personaje desde la base de datos personajes.db."""
    try:
        conn = sqlite3.connect("personajes.db")
        cursor = conn.cursor()
        cursor.execute("SELECT serie FROM personajes WHERE nombre = ?", (nombre_personaje,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado[0] if resultado else "Desconocido"
    except Exception as e:
        print(f"Error al obtener anime: {e}")
        return "Desconocido"
    
RARITY_MAP = {
    1: "E",
    2: "D",
    3: "C",
    4: "B",
    5: "A",
    6: "S",
    7: "SS",
    8: "SSS"
}

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

def safe_int(value, default=0):
    """Convierte un valor a entero de forma segura"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

class GridInventoryView(discord.ui.View):
    def __init__(self, characters, total_value, db, user_id):
        super().__init__(timeout=120)
        self.characters = characters
        self.total_value = total_value
        self.db = db
        self.user_id = user_id
        self.page = 0
        self.selected_index = None
        
        # Añadir botones de navegación
        self.add_item(PrevButton())
        self.add_item(NextButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return str(interaction.user.id) == self.user_id

    def create_embed(self):
        embed = discord.Embed(
            title=f"📦 INVENTARIO • Valor Total: {self.total_value:,} monedas",
            color=0x00bfff
        )
        
        # Dividir en 3 columnas
        current_page = self.characters[self.page * 9 : (self.page + 1) * 9]
        columns = [current_page[i::3] for i in range(3)]
        
        for col_idx, column in enumerate(columns):
            field_value = ""
            for idx, char in enumerate(column):
                rarity = char.get("rarity", "E")  # Obtener la rareza como letra
                anime = char.get("anime", "Desconocido")  # Obtener el nombre del anime
                
                field_value += (
                    f"**{char['name']}**\n"
                    f"Rareza: **{rarity}**\n"
                    f"Anime: {anime}\n"
                    f"Valor: {char['value']} monedas\n\n"
                )
            embed.add_field(
                name="\u200b",  # Campo vacío para ocultar "Sección"
                value=field_value or "Vacío",
                inline=True
            )
        
        embed.set_footer(text=f"Página {self.page + 1}/{(len(self.characters) - 1) // 9 + 1}")
        return embed

class PrevButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.blurple, emoji="⬅️", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.page > 0:
            view.page -= 1
            view.selected_index = None
            await interaction.response.edit_message(embed=view.create_embed(), view=view)

class NextButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.blurple, emoji="➡️", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if (view.page + 1) * 9 < len(view.characters):
            view.page += 1
            view.selected_index = None
            await interaction.response.edit_message(embed=view.create_embed(), view=view)

class Bank(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.db = Database()

    @bot.slash_command(name="info_protec", description="Muestra tiempo restante de protección y costo diario.")
    async def protection_info(self, ctx: discord.ApplicationContext):
        try:
            user_id = str(ctx.user.id)
            server_id = str(ctx.guild.id)
            user = self.db.get_user(user_id, server_id)
            characters = self.db.get_characters(user_id, server_id)
            total_value = sum(safe_int(char["value"]) for char in characters) if characters else 0

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
            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error al obtener información: {e}", ephemeral=True)

    @bot.slash_command(name="pagar_banco", description="Paga protección por X días (ajustado por reputación).")
    async def pay_protection(self, ctx: discord.ApplicationContext, dias: int):
        try:
            if dias <= 0:
                await ctx.respond("❌ ¡Debes especificar un número de días válido!", ephemeral=True)
                return

            user_id = str(ctx.user.id)
            server_id = str(ctx.guild.id)
            user = self.db.get_user(user_id, server_id)
            characters = self.db.get_characters(user_id, server_id)
            total_value = sum(safe_int(char["value"]) for char in characters) if characters else 0
            base_fee = total_value * 0.05
            fee_multiplier = 0.85 if user["reputation"] > 0 else 1.15 if user["reputation"] < 0 else 1.0
            total_fee = base_fee * fee_multiplier * dias

            if user["coins"] < total_fee:
                await ctx.respond(f"❌ No tienes suficientes monedas. Necesitas: {total_fee:.2f}", ephemeral=True)
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

            await ctx.respond(f"✅ Protección pagada por {dias} días. Costo: {total_fee:.2f} monedas.", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error al pagar protección: {e}", ephemeral=True)

    @bot.slash_command(name="inventario", description="Muestra tu inventario en formato de cuadrícula 3x3")
    async def show_grid_inventory(self, ctx: discord.ApplicationContext):
        try:
            user_id = str(ctx.user.id)
            server_id = str(ctx.guild.id)
            
            characters = self.db.get_characters(user_id, server_id)
            if not characters:
                await ctx.respond("🎒 Tu inventario está vacío. Usa `/girar` para obtener personajes!", ephemeral=True)
                return
            
            # Procesar personajes
            processed_chars = []
            for char in characters:
                char_dict = dict(char)
                
                # Verificar si rarity es un número y convertirlo a letra
                rarity_value = char_dict.get("rarity", 1)
                if isinstance(rarity_value, int) or rarity_value.isdigit():
                    char_dict["rarity"] = RARITY_MAP.get(int(rarity_value), "E")
                else:
                    char_dict["rarity"] = rarity_value  # Mantener la letra si ya es una rareza válida
                
                # Obtener el anime desde personajes.db si no está en la base de datos principal
                char_dict["anime"] = obtener_anime(char_dict.get("name", "Desconocido"))
                char_dict["value"] = int(char_dict.get("value", 0))  # Asegurar que el valor sea un entero
                processed_chars.append(char_dict)
            
            total_value = sum(c["value"] for c in processed_chars)
            view = GridInventoryView(processed_chars, total_value, self.db, user_id)
            
            await ctx.respond(embed=view.create_embed(), view=view, ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error al mostrar inventario: {e}", ephemeral=True)

    @bot.slash_command(name="perfil", description="Muestra tu perfil con reputación, monedas y valor.")
    async def show_profile(self, ctx: discord.ApplicationContext):
        try:
            user_id = str(ctx.user.id)
            server_id = str(ctx.guild.id)
            user = self.db.get_user(user_id, server_id)
            characters = self.db.get_characters(user_id, server_id)
            total_characters_value = sum(safe_int(char["value"]) for char in characters) if characters else 0

            rep_emoji = "😇" if user["reputation"] > 0 else "😈" if user["reputation"] < 0 else "😐"

            embed = discord.Embed(
                title=f"📊 Perfil de {ctx.user.display_name}",
                color=0x7289DA
            )
            embed.add_field(name="💎 Monedas", value=f"{user['coins']}", inline=False)
            embed.add_field(name="🎭 Reputación", value=f"{user['reputation']} pts {rep_emoji}", inline=False)
            embed.add_field(name="🧑‍🎨 Valor en personajes", value=f"{total_characters_value}", inline=False)

            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.respond(f"❌ Error al mostrar perfil: {e}", ephemeral=True)

def setup(bot: discord.Bot):
    print("✅ Bank cargado")
    bot.add_cog(Bank(bot))