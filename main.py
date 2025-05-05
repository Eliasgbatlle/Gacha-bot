import discord
import os
import sys
from dotenv import load_dotenv
from utils.database import Database
from utils.databasechar import crear_base_de_datos, generar_personajes, TOTAL_PERSONAJES
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.auth import get_current_user
import uvicorn
import asyncio
from modules.gacha.rolls import bot, GachaRolls, personaje_actual
import nest_asyncio
from utils.state_manager import StateManager
from discord.ext import commands
import logging
from datetime import timedelta

# Configurar el logger
logger = logging.getLogger(__name__)

# Agregar la carpeta raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Agregar la carpeta 'web/src' al sys.path para que Python pueda encontrar los módulos
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'src'))

# Crear una instancia de FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las solicitudes de origen (puedes restringirlo a dominios específicos)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

@app.post("/api/discord/girar")
async def girar(request: Request, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")  # Obtener el ID del usuario desde la sesión activa

    body = await request.json()
    server_id = body.get("server_id")  # Obtener el server_id directamente del cuerpo de la solicitud
    source = body.get("source")  # Obtener el source directamente del cuerpo de la solicitud
    
    # Log para verificar el cuerpo completo de la solicitud
    print(f"[DEBUG] Cuerpo de la solicitud recibido: {body}")
    
    if not server_id:
        return {"error": "El ID del servidor no fue proporcionado."}

    # Log para verificar si el servidor fue encontrado
    print(f"[DEBUG] Intentando obtener el servidor con ID: {server_id}")
    guild = bot.get_guild(int(server_id))
    if not guild:
        print("[ERROR] No se pudo encontrar el servidor en Discord")
        return {"error": "No se pudo encontrar el servidor en Discord"}

    if not source:
        return {"error": "El origen no fue proporcionado."}

    # Log para verificar si el obtener fue encontrado
    print(f"[DEBUG] Intentando obtener el origen: {source}")

    # Obtener la instancia de GachaRolls
    gacha_rolls = next((cog for cog in bot.cogs.values() if isinstance(cog, GachaRolls)), None)

    # Log para listar canales disponibles
    print("[LOG] Canales disponibles en el servidor:")
    for c in guild.text_channels:
        permisos = c.permissions_for(guild.me)
        print(f"[LOG] - {c.name} (Enviar mensajes: {permisos.send_messages})")

    # Log para verificar si se encontró un canal
    print("[DEBUG] Buscando canal llamado 'general'")
    channel = discord.utils.get(guild.text_channels, name="general")
    if not channel:
        print("[WARNING] No se encontró un canal llamado 'general'. Buscando el primer canal disponible.")
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

    if channel:
        print(f"[DEBUG] Canal seleccionado: {channel.name} (ID: {channel.id})")
    else:
        print("[ERROR] No se pudo seleccionar un canal válido para enviar el mensaje.")
        return {"error": "No se pudo encontrar un canal de texto en el servidor"}

    # Log para verificar si el bot tiene los intents necesarios
    print("[LOG] Verificando intents del bot")
    if not bot.intents.members:
        print("[ERROR] El bot no tiene activado el intent 'members'.")
        return {"error": "El bot no tiene activado el intent 'members'."}

    # Log para listar miembros del servidor (si es posible)
    print("[LOG] Listando miembros del servidor:")
    try:
        for member in guild.members:
            print(f"[LOG] - {member.name} (ID: {member.id})")
    except Exception as e:
        print(f"[ERROR] No se pudo listar los miembros del servidor: {e}")

    # Log para verificar si el usuario está en el servidor
    print(f"[LOG] Buscando miembro con ID: {user_id}")
    member = guild.get_member(int(user_id))
    if not member:
        print(f"[ERROR] Usuario con ID {user_id} no encontrado en el servidor {guild.name} (ID: {guild.id})")
        return {"error": "Usuario no encontrado en el servidor"}

    # Log para crear contexto de interacción
    print("[LOG] Creando contexto de interacción simulado")
    class FakeInteraction:
        def __init__(self, user, guild):
            self.user = user
            self.guild = guild

        async def respond(self, content, ephemeral=False):
            print(f"[LOG] Respuesta simulada: {content}")

    interaction = FakeInteraction(member, guild)

    # Log para verificar si el comando /girar está registrado
    print("[DEBUG] Verificando si el comando /girar está registrado")
    command = bot.get_command("girar")
    if not command:
        print("[ERROR] El comando /girar no está registrado en el bot.")
        return {"error": "El comando /girar no está registrado en el bot."}
    print("[DEBUG] Comando /girar encontrado en el bot.")

    # Log para verificar la ejecución del comando
    try:
        print("[DEBUG] Ejecutando el comando /girar...")
        # Crear un contexto simulado para el comando
        class FakeContext:
            def __init__(self, interaction, source):
                self.interaction = interaction
                self.user = interaction.user
                self.guild = interaction.guild
                self.source = source

                # Ajustar el atributo followup para que sea un objeto directamente accesible
                class Followup:
                    def __init__(self, channel):
                        self.channel = channel

                    async def send(self, *args, **kwargs):
                        # Enviar el mensaje al canal real
                        embed = kwargs.get('embed')
                        view = kwargs.get('view')
                        if embed or view:
                            await self.channel.send(embed=embed, view=view)
                            print(f"[DEBUG] Mensaje enviado al canal {self.channel.name} con embed y view.")
                        else:
                            await self.channel.send(*args, **kwargs)
                            print(f"[DEBUG] Mensaje enviado al canal {self.channel.name} con contenido: {args}")

                self.followup = Followup(channel)

            async def respond(self, *args, **kwargs):
                print(f"[DEBUG] Respuesta simulada: {args}, {kwargs}")

            async def defer(self, ephemeral=False):
                print(f"[DEBUG] defer() llamado con ephemeral={ephemeral}")

        ctx = FakeContext(interaction, source=source)

        # Consumir datos del personaje desde la cola

        await command(ctx)
        print("[DEBUG] Comando /girar ejecutado correctamente.")
        return {"message": "Comando girar ejecutado correctamente"}
    except Exception as e:
        print(f"[ERROR] Error al ejecutar el comando /girar: {e}")
        return {"error": f"Error al ejecutar el comando /girar: {str(e)}"}

@app.get("/api/discord/get-personaje")
async def get_personaje():
    """Endpoint para obtener los datos del personaje desde la cola."""

    # Obtener el personaje desde el contenedor de estado
    personaje_actual = StateManager.get("personaje_actual")

    if personaje_actual is None:
        print("[DEBUG] No hay datos del personaje disponibles actualmente.")
        return {"error": "No hay datos del personaje disponibles. Intenta nuevamente más tarde."}

    print(f"[DEBUG] Datos del personaje obtenidos: {personaje_actual}")
    return personaje_actual

@app.post("/api/recompensa-diaria")
async def recompensa_diaria(request: Request):
    logger.info("Endpoint /api/recompensa-diaria llamado.")
    try:
        body = await request.json()
        user_id = body.get("user_id")
        server_id = body.get("server_id")

        logger.debug(f"Datos recibidos: user_id={user_id}, server_id={server_id}.")

        if not user_id or not server_id:
            logger.error("Faltan user_id o server_id en la solicitud.")
            raise HTTPException(status_code=400, detail="user_id and server_id are required.")

        # Obtener el servidor de Discord
        guild = bot.get_guild(int(server_id))
        if not guild:
            logger.error(f"Servidor con ID {server_id} no encontrado.")
            raise HTTPException(status_code=404, detail="Servidor no encontrado.")

        # Obtener el miembro de Discord
        member = guild.get_member(int(user_id))
        if not member:
            logger.error(f"Usuario con ID {user_id} no encontrado en el servidor {server_id}.")
            raise HTTPException(status_code=404, detail="Usuario no encontrado en el servidor.")

        logger.debug(f"Usuario {user_id} encontrado en el servidor {server_id}.")

        # Crear un contexto simulado para el comando
        class FakeInteraction:
            def __init__(self, user, guild, bot):
                self.user = user
                self.guild = guild
                self.bot = bot
                self.author = user  # Agregar atributo author para compatibilidad con comandos
                self.interaction = self  # Agregar atributo interaction para compatibilidad con comandos
                self.data = {}  # Agregar atributo data para compatibilidad con comandos

            async def respond(self, content, ephemeral=False):
                self.response = content

        interaction = FakeInteraction(member, guild, bot)

        # Obtener el comando recompensa_diaria
        command = bot.get_command("recompensa_diaria")
        if not command:
            logger.error("Comando recompensa_diaria no encontrado.")
            raise HTTPException(status_code=500, detail="Comando recompensa_diaria no encontrado.")

        logger.debug("Ejecutando el comando recompensa_diaria.")

        # Ejecutar el comando respetando la lógica de enfriamiento
        try:
            await command.invoke(interaction)
            logger.info("Comando recompensa_diaria ejecutado correctamente.")
            return {"message": interaction.response}
        except commands.CommandOnCooldown as cooldown_error:
            retry_after = timedelta(seconds=cooldown_error.retry_after)
            hours, remainder = divmod(retry_after.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            logger.warning(f"Comando en cooldown. Tiempo restante: {hours}h {minutes}m {seconds}s.")
            return {
                "error": "Comando en cooldown.",
                "message": f"⏳ Ya reclamaste tu recompensa diaria. Vuelve en {hours} horas, {minutes} minutos y {seconds} segundos."
            }
        except Exception as e:
            logger.error(f"Error inesperado al ejecutar el comando: {e}")
            raise HTTPException(status_code=500, detail=f"Error al ejecutar el comando: {str(e)}")
    except Exception as e:
        logger.critical(f"Error crítico en el endpoint /api/recompensa-diaria: {e}")
        raise HTTPException(status_code=500, detail=f"Error crítico: {str(e)}")

crear_base_de_datos()
generar_personajes(TOTAL_PERSONAJES) 

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

# --- Instancia del bot ---
bot = discord.Bot(intents=intents)

# --- Eventos ---
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user} en {len(bot.guilds)} servidores')
    # Sincroniza los slash commands con Discord
    await bot.sync_commands()
    print('⚡ Slash commands sincronizados')

    # Llenar la tabla 'servers' con los servidores actuales
    db = Database()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for guild in bot.guilds:
            cursor.execute(
                "INSERT OR IGNORE INTO servers (server_id, server_name) VALUES (?, ?)",
                (str(guild.id), guild.name)
            )
        conn.commit()
    print('✅ Tabla servers actualizada con los servidores actuales')

# --- Comando de prueba ---
@bot.slash_command(name="ping", description="Verifica la latencia del bot")
async def ping(ctx: discord.ApplicationContext):
    start = discord.utils.utcnow().timestamp()
    msg = await ctx.respond("🏓 Calculando latencia...")
    end = discord.utils.utcnow().timestamp()
    ms = round((end - start)*1000)
    await msg.edit_original_response(content=f"🏓 Pong! Latencia: {ms}ms")

# --- Carga de extensiones (sin await) ---
modules = [
    'modules.economy.bank',
    'modules.economy.work',
    'modules.economy.daily',
    'modules.economy.market',
    'modules.gacha.characters',
    'modules.gacha.rolls',
]

for mod in modules:
    try:
        bot.load_extension(mod)
        print(f'✅ Extensión {mod} cargada')
    except Exception as e:
        print(f'❌ Error cargando {mod}: {e}')

# Aplicar nest_asyncio para permitir múltiples bucles de eventos
nest_asyncio.apply()

# Crear un bucle de eventos explícito
loop = asyncio.get_event_loop()

async def main():
    # Crear tareas para el bot y el servidor FastAPI
    bot_task = loop.create_task(bot.start(TOKEN))
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # Ejecutar ambas tareas en el mismo bucle de eventos
    await asyncio.gather(bot_task, server.serve())

if __name__ == "__main__":
    loop.run_until_complete(main())
