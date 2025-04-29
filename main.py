import discord
import os
import json
from dotenv import load_dotenv
from utils.database import Database
from utils.databasechar import crear_base_de_datos, generar_personajes, TOTAL_PERSONAJES

crear_base_de_datos()
generar_personajes(TOTAL_PERSONAJES) 

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

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

# Inicializa la base de datos y crea las tablas si no existen
if __name__ == "__main__":
    db = Database()
    print("Tablas inicializadas correctamente.")

# --- Arranca el bot ---
bot.run(TOKEN)
