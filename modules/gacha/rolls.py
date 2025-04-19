import discord
import sqlite3
import random
import asyncio
from discord.ext import commands
from utils.databasechar import obtener_todos_los_personajes, precio_por_rareza
from utils.database import Database
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

class GachaRolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_rolls = {}  # {user_id: personaje}
        self.claim_cooldowns = {}  # {user_id: timestamp}
        self.protected_rolls = {}  # {roll_id: (user_id, expiration_time)}
        self.roll_prices = {}  # {roll_id: price}

    async def check_expired_protections(self):
        while True:
            now = datetime.now()
            expired = [k for k, v in self.protected_rolls.items() if v[1] < now]
            for roll_id in expired:
                del self.protected_rolls[roll_id]
            await asyncio.sleep(10)

    def probabilidad_personaje_roll(self, personajes):
        probabilidades = {
            "SSS": 0.0001,
            "SS": 0.001,
            "S": 0.01,
            "A": 0.07,
            "B": 0.13,
            "C": 0.18,
            "D": 0.28,
            "E": 0.3299
        }
        pool = []
        for personaje in personajes:
            rareza = personaje["rareza"]
            if rareza in probabilidades:
                pool.extend([personaje] * int(probabilidades[rareza] * 1000000))
        return random.choice(pool)

    @bot.slash_command(name="girar", description="🎰 Gira la ruleta gacha para obtener un personaje")
    async def roll(self, ctx: discord.ApplicationContext):
        user_id = str(ctx.user.id)
        server_id = str(ctx.guild.id)
        db = Database()
    
        roll_price = 500
        user = db.get_user(user_id, server_id)
        if user["coins"] < roll_price:
            await ctx.respond(f"❌ No tienes suficientes monedas para tirar un roll. Necesitas {roll_price} monedas.", ephemeral=True)
            return
    
        db.update_user(user_id, server_id, {"coins": user["coins"] - roll_price})
    
        personajes = obtener_todos_los_personajes()
        if not personajes:
            await ctx.respond("❌ No hay personajes disponibles en el gacha.", ephemeral=True)
            return
    
        personaje = self.probabilidad_personaje_roll(personajes)
        self.user_rolls[user_id] = personaje
    
        # Añadir protección de 20 segundos
        roll_id = f"{user_id}_{datetime.now().timestamp()}"
        self.protected_rolls[roll_id] = (user_id, datetime.now() + timedelta(seconds=20))
        self.roll_prices[roll_id] = roll_price
    
        embed = discord.Embed(
            title=f"⭐ ¡Has obtenido a {personaje['nombre']}!",
            description=f"Serie: {personaje['serie']}\nRareza: {personaje['rareza']}",
            color=0x00ff00
        )
        if personaje.get("imagen"):
            embed.set_image(url=personaje["imagen"])
    
        view = self.ClaimView(personaje, user_id, db, roll_id, self)
        await ctx.respond(embed=embed, view=view)

    class ClaimView(discord.ui.View):
        def __init__(self, personaje, user_id, db, roll_id, parent_cog):
            super().__init__(timeout=60)
            self.personaje = personaje
            self.user_id = user_id
            self.db = db
            self.roll_id = roll_id
            self.parent_cog = parent_cog
            self.claimed = False

        @discord.ui.button(label="¡Reclamar!", style=discord.ButtonStyle.success)
        async def claim_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            if self.claimed:
                await interaction.response.defer()
                return

            current_user = str(interaction.user.id)
            roll_data = self.parent_cog.protected_rolls.get(self.roll_id)
            
            # Verificar protección de 20 segundos
            if roll_data:
                owner_id, expiration = roll_data
                if owner_id != current_user and datetime.now() < expiration:
                    remaining = int((expiration - datetime.now()).total_seconds())
                    await interaction.response.send_message(
                        f"⏳ Este personaje está protegido por {remaining} segundos. Solo puede reclamarlo quien lo obtuvo.",
                        ephemeral=True
                    )
                    return

            # Verificar cooldown de 30 minutos
            if current_user in self.parent_cog.claim_cooldowns:
                remaining = (datetime.now() - self.parent_cog.claim_cooldowns[current_user]).total_seconds()
                if remaining < 5:
                    await interaction.response.send_message(
                        f"⏳ Debes esperar {int((1800 - remaining)/60)} minutos antes de reclamar otro personaje.",
                        ephemeral=True
                    )
                    return

            # Verificar si ya existe el personaje
            existing_chars = self.db.get_characters(current_user, str(interaction.guild.id))
            for char in existing_chars:
                if char["name"] == self.personaje["nombre"]:
                    button.disabled = True
                    button.label = "¡Ya reclamado!"
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(
                        f"❌ Ya tienes a {self.personaje['nombre']} en tu inventario.",
                        ephemeral=True
                    )
                    return

            # Añadir personaje a la base de datos
            self.db.add_character({
                "id": f"{self.personaje['nombre']}_{current_user}_{datetime.now().timestamp()}",
                "owner_id": current_user,
                "server_id": str(interaction.guild.id),
                "name": self.personaje["nombre"],
                "rarity": self.personaje["rareza"],
                "value": precio_por_rareza(self.personaje["rareza"]),
                "image_url": self.personaje.get("imagen", "")
            })

            # Actualizar mensaje original
            button.disabled = True
            button.label = "¡Reclamado!"
            button.style = discord.ButtonStyle.secondary
            await interaction.response.edit_message(view=self)

            # Establecer cooldown
            self.parent_cog.claim_cooldowns[current_user] = datetime.now()
            
            # Eliminar protección
            if self.roll_id in self.parent_cog.protected_rolls:
                del self.parent_cog.protected_rolls[self.roll_id]
            
            # Reembolsar si no fue reclamado por el dueño original
            if current_user != self.user_id and self.roll_id in self.parent_cog.roll_prices:
                refund = self.parent_cog.roll_prices[self.roll_id]
                self.db.update_user(
                    self.user_id,
                    str(interaction.guild.id),
                    {"coins": self.db.get_user(self.user_id, str(interaction.guild.id))["coins"] + refund}
                )
                await interaction.followup.send(
                    f"✅ ¡Has reclamado a {self.personaje['nombre']}!\n"
                    f"💰 Se han reembolsado {refund} monedas al dueño original del roll.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"✅ ¡Has reclamado a {self.personaje['nombre']}!",
                    ephemeral=True
                )

def setup(bot):
    cog = GachaRolls(bot)
    bot.add_cog(cog)
    bot.loop.create_task(cog.check_expired_protections())