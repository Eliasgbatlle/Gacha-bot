import discord
import os
import sys
from dotenv import load_dotenv
from utils.database import Database
from utils.databasechar import crear_base_de_datos, generar_personajes, TOTAL_PERSONAJES
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from utils.auth import get_current_user
import uvicorn
import asyncio
from modules.gacha.rolls import bot
import nest_asyncio

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

@app.post("/api/discord/girar")
async def girar(request: Request, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")  # Obtener el ID del usuario desde la sesión activa

    body = await request.json()
    server_id = body.get("server_id")  # Obtener el server_id directamente del cuerpo de la solicitud

    if not server_id:
        return {"error": "El ID del servidor no fue proporcionado."}

    # Log para verificar si el servidor fue encontrado
    print(f"[DEBUG] Intentando obtener el servidor con ID: {server_id}")
    guild = bot.get_guild(int(server_id))
    if not guild:
        print("[ERROR] No se pudo encontrar el servidor en Discord")
        return {"error": "No se pudo encontrar el servidor en Discord"}

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
            def __init__(self, interaction):
                self.interaction = interaction
                self.user = interaction.user
                self.guild = interaction.guild

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

        ctx = FakeContext(interaction)
        await command(ctx)
        print("[DEBUG] Comando /girar ejecutado correctamente.")
        return {"message": "Comando girar ejecutado correctamente"}
    except Exception as e:
        print(f"[ERROR] Error al ejecutar el comando /girar: {e}")
        return {"error": f"Error al ejecutar el comando /girar: {str(e)}"}

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
