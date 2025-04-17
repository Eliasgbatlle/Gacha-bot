import discord
import os
import json
from dotenv import load_dotenv
from utils.databasechar import crear_base_de_datos, generar_personajes

crear_base_de_datos()
generar_personajes(1000) 

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Configuración e intents ---
def load_config():
    with open('config.json','r') as f:
        return json.load(f)

config = load_config()

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
    'modules.gacha.characters',
]

for mod in modules:
    try:
        bot.load_extension(mod)
        print(f'✅ Extensión {mod} cargada')
    except Exception as e:
        print(f'❌ Error cargando {mod}: {e}')

# --- Arranca el bot ---
bot.run(TOKEN)
