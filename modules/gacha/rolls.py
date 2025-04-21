import discord
import sqlite3
import random
import asyncio
import requests
import unicodedata
from discord.ext import commands
from utils.databasechar import obtener_todos_los_personajes, precio_por_rareza
from utils.database import Database
from datetime import datetime, timedelta


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

def obtener_imagen_gelbooru(nombre, anime=None):
    """Busca una imagen NSFW en Gelbooru usando el nombre del personaje y filtra por la etiqueta '1girl', excluyendo ciertas etiquetas."""
    try:
        # Generar variaciones del nombre
        variaciones = [nombre]
        if " " in nombre:  # Si el nombre tiene un espacio, generar variaciones
            partes = nombre.split(" ")
            if len(partes) == 2:  # Asumimos que tiene nombre y apellido
                nombre_completo = f"{partes[0]}_{partes[1]}"
                apellido_primero = f"{partes[1]}_{partes[0]}"
                variaciones.append(nombre_completo)
                variaciones.append(apellido_primero)
                if anime:
                    variaciones.append(f"{nombre_completo} ({anime})")
                    variaciones.append(f"{apellido_primero} ({anime})")
        
        # Etiquetas excluyentes
        etiquetas_excluyentes = "-men+-futa+-erection+-multiple_boys+-penis+-boy+"
        
        # Normalizar y buscar cada variación
        for variacion in variaciones:
            # Normalizar el nombre para eliminar caracteres especiales
            nombre_normalizado = unicodedata.normalize('NFKD', variacion).encode('ascii', 'ignore').decode('ascii')
            # Convertir el nombre a minúsculas y reemplazar espacios por guiones bajos
            nombre_tag = nombre_normalizado.lower().replace(" ", "_")
            api_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={nombre_tag}+rating%3Aexplicit+{etiquetas_excluyentes}&limit=3"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()

                # Verificar si la respuesta contiene imágenes en la clave 'post'
                if "post" in data and isinstance(data["post"], list):  # La respuesta debe contener una lista en 'post'
                    for item in data["post"]:
                        tags = item.get("tags", "").split(" ")  # Dividir las etiquetas en una lista
                        # Verificar que las etiquetas excluyentes no estén presentes
                        etiquetas_excluidas = {"men", "futa", "erection", "multiple", "penis", "boy"}
                        if any(tag in etiquetas_excluidas for tag in tags):
                            continue
                        if "1girl" in tags and "file_url" in item:  # Filtrar por '1girl'
                            return item["file_url"]  # Devolver la URL de la imagen completa
    except Exception:
        pass
    return None

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
    
        # Agrupar personajes por rareza
        personajes_por_rareza = {rareza: [] for rareza in probabilidades}
        for personaje in personajes:
            rareza = personaje["rareza"].upper()  # Convertir a mayúsculas para consistencia
            if rareza in probabilidades:
                personajes_por_rareza[rareza].append(personaje)
    
        # Generar una lista de rarezas basada en las probabilidades
        rarezas = list(probabilidades.keys())
        probabilidades_lista = list(probabilidades.values())
    
        # Seleccionar una rareza basada en las probabilidades
        rareza_seleccionada = random.choices(rarezas, weights=probabilidades_lista, k=1)[0]
    
        # Seleccionar un personaje aleatorio dentro de la rareza seleccionada
        if personajes_por_rareza[rareza_seleccionada]:
            return random.choice(personajes_por_rareza[rareza_seleccionada])
    
        # Si no hay personajes disponibles en la rareza seleccionada, intenta con otra rareza
        for rareza in rarezas:
            if personajes_por_rareza[rareza]:
                return random.choice(personajes_por_rareza[rareza])
    
        # Si no hay personajes disponibles en ninguna rareza, retorna None
        print("⚠️ No hay personajes disponibles en el pool.")
        return None
    
    @bot.slash_command(name="girar", description="🎰 Gira la ruleta gacha para obtener un personaje")
    async def roll(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=False)  # Indicar que el bot está procesando la interacción
    
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
        if personaje is None:
            await ctx.respond("⚠️ No hay personajes disponibles en el pool para este roll. Intenta más tarde.", ephemeral=True)
            return
    
        # Continuar con la lógica si se seleccionó un personaje
        self.user_rolls[user_id] = personaje
    
        # Depuración: imprimir el género del personaje
        print(f"🔍 Género del personaje: {personaje.get('genero', 'No definido')}")
    
        # Buscar imagen del personaje usando Gelbooru solo si es femenino
        if personaje.get("genero", "").lower() == "female":
            imagen_url = obtener_imagen_gelbooru(personaje["nombre"], personaje.get("serie"))
            personaje["imagen"] = imagen_url if imagen_url else personaje.get("imagen", None)
        else:
            personaje["imagen"] = personaje.get("imagen", None)  # Usar la imagen almacenada en la tabla
    
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
        else:
            embed.set_footer(text="No se encontró una imagen para este personaje.")
    
        view = self.ClaimView(personaje, user_id, db, roll_id, self)
        await ctx.followup.send(embed=embed, view=view)  # Usar followup para enviar el mensaje después de defer

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
                if remaining < 1800:
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