import discord
import textwrap
from discord import File, ButtonStyle
from discord.ext import commands
from datetime import datetime, timedelta
from utils.database import Database
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

class GridInventoryView(discord.ui.View):
    def __init__(self, characters, total_value, db):
        super().__init__(timeout=120)
        self.characters = characters
        self.total_value = total_value
        self.db = db
        self.page = 0
        self.selected_index = None
        
        # Añadir botones de navegación
        self.add_item(PrevButton())
        self.add_item(NextButton())

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
                global_idx = self.page * 9 + col_idx * 3 + idx
                emoji = "🔹" if global_idx == self.selected_index else "▫️"
                rarity = char.get("rarity", "E")  # Obtener la rareza como letra
                anime = char.get("anime", "Desconocido")  # Obtener el nombre del anime
                field_value += (
                    f"{emoji} **{char['name']}** ({rarity})\n"
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

class ProtectButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.green, label="Proteger", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.selected_index is not None:
            selected_char = view.characters[view.selected_index]
            # Lógica de protección existente
            characters = view.db.get_characters(str(interaction.user.id), str(interaction.guild.id))
            total_value = sum(int(c["value"]) for c in characters)
            protection_cost = int(total_value * 0.05)
            user = view.db.get_user(str(interaction.user.id), str(interaction.guild.id))
            
            if user["coins"] >= protection_cost:
                view.db.update_user(
                    str(interaction.user.id), 
                    str(interaction.guild.id),
                    {"coins": user["coins"] - protection_cost}
                )
                await interaction.response.send_message(
                    f"🛡️ ¡Protección activada por {protection_cost} monedas!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ No tienes suficientes monedas. Necesitas {protection_cost}",
                    ephemeral=True
                )

class SellButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=ButtonStyle.red, label="Vender", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if view.selected_index is not None:
            selected_char = view.characters[view.selected_index]
            # Lógica de venta (puedes implementarla según tus necesidades)
            await interaction.response.send_message(
                f"💰 ¿Vender {selected_char['name']} por {selected_char['value']} monedas?",
                ephemeral=True
            )

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
            total_value = sum(int(char["value"]) for char in characters) if characters else 0

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
        except Exception as e:
            await ctx.respond(f"❌ Error al obtener información: {e}")

    @bot.slash_command(name="pagar_banco", description="Paga protección por X días (ajustado por reputación).")
    async def pay_protection(self, ctx: discord.ApplicationContext, dias: int):
        try:
            if dias <= 0:
                await ctx.respond("❌ ¡Debes especificar un número de días válido!")
                return

            user_id = str(ctx.user.id)
            server_id = str(ctx.guild.id)
            user = self.db.get_user(user_id, server_id)
            characters = self.db.get_characters(user_id, server_id)
            total_value = sum(int(char["value"]) for char in characters) if characters else 0
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
        except Exception as e:
            await ctx.respond(f"❌ Error al pagar protección: {e}")

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
            rarity_map = {"E":1, "D":2, "C":3, "B":4, "A":5, "S":6, "SS":7, "SSS":8}
            
            for char in characters:
                char_dict = dict(char)
                char_dict["rarity"] = rarity_map.get(char_dict.get("rarity", "E"), 1)
                char_dict["value"] = int(char_dict.get("value", 0))
                processed_chars.append(char_dict)
            
            total_value = sum(c["value"] for c in processed_chars)
            view = GridInventoryView(processed_chars, total_value, self.db)
            
            await ctx.respond(embed=view.create_embed(), view=view)
        except Exception as e:
            await ctx.respond(f"❌ Error al mostrar inventario: {e}")

    @bot.slash_command(name="perfil", description="Muestra tu perfil con reputación, monedas y valor.")
    async def show_profile(self, ctx: discord.ApplicationContext):
        try:
            user_id = str(ctx.user.id)
            server_id = str(ctx.guild.id)
            user = self.db.get_user(user_id, server_id)
            characters = self.db.get_characters(user_id, server_id)
            total_characters_value = sum(int(char["value"]) for char in characters) if characters else 0

            rep_emoji = "😇" if user["reputation"] > 0 else "😈" if user["reputation"] < 0 else "😐"

            embed = discord.Embed(
                title=f"📊 Perfil de {ctx.user.display_name}",
                color=0x7289DA
            )
            embed.add_field(name="💎 Monedas", value=f"{user['coins']}", inline=False)
            embed.add_field(name="🎭 Reputación", value=f"{user['reputation']} pts {rep_emoji}", inline=False)
            embed.add_field(name="🧑‍🎨 Valor en personajes", value=f"{total_characters_value}", inline=False)

            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond(f"❌ Error al mostrar perfil: {e}")

def setup(bot: discord.Bot):
    print("✅ Bank cargado")
    bot.add_cog(Bank(bot))