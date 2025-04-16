import discord
import os
import json
from dotenv import load_dotenv
import asyncio
import time
import traceback

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
print("⚙️ Starting main.py, loading config...")

def load_config():
    print("🔄 load_config called")
    with open('config.json','r') as f:
        cfg = json.load(f)
    print(f"📑 Config loaded: {cfg}")
    return cfg

config = load_config()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
print(f"🎯 Intents set: messages={intents.messages}, guilds={intents.guilds}, message_content={intents.message_content}")

bot = discord.Bot(intents=intents)
print("🤖 Bot instance created")

@bot.event
async def on_ready():
    print("🔔 on_ready triggered")
    print(f"Bot connected as {bot.user} on servers: {[guild.id for guild in bot.guilds]}")
    print("⚡ Comandos slash listos.")

@bot.slash_command(name="ping", description="Verifica la latencia del bot")
async def ping(ctx):
    print("🏓 ping command called")
    start = time.perf_counter()
    message = await ctx.respond("🏓 Calculando latencia...")
    end = time.perf_counter()
    latency = round((end - start)*1000)
    await message.edit_original_response(content=f"🏓 Pong! Latencia: {latency}ms")
    print(f"🏓 ping response sent: {latency}ms")

@bot.event
async def on_application_command_error(ctx, error):
    print("🚨 on_application_command_error triggered")
    traceback.print_exception(type(error), error, error.__traceback__)

async def main():
    modules = [
        'modules.economy.bank',
        'modules.economy.work',
    ]
    print(f"🔌 Loading extensions: {modules}")
    for module in modules:
        print(f"➡️ Loading extension {module}...")
        try:
            await bot.load_extension(module)
            print(f"✅ Extension {module} loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load extension {module}: {e}")
            traceback.print_exc()

    print("🚀 Starting bot...")
    await bot.start(TOKEN)

if __name__ == '__main__':
    print("▶️ Running main via asyncio")
    asyncio.run(main())
