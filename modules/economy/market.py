import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = discord.Bot(intents=intents)

class Market(commands.Cog):
    """Sistema de mercado y comercio entre usuarios."""
    def __init__(self, bot):
        self.bot = bot
        self.market_items = []  # Lista de personajes en el mercado
        self.blackmarket_items = []  # Lista de personajes en el mercado negro
        self.users = {}  # Diccionario de usuarios con su información (dinero, reputación, personajes)

    # Métodos de la clase Market...
    def sell_character(self, user_id, character_name, price):
        """
        Registra un personaje en el mercado sin eliminarlo del inventario del vendedor.
        """
        user = self.users.get(user_id)
        if not user:
            return "❌ Usuario no encontrado. Asegúrate de estar registrado en el sistema."
    
        # Verificar si el personaje está en el inventario del usuario
        character = next((c for c in user['characters'] if c['name'] == character_name), None)
        if not character:
            return f"❌ No tienes al personaje '{character_name}' en tu inventario."
    
        # Verificar si el personaje ya está en el mercado
        if any(item['character']['name'] == character_name and item['seller'] == user_id for item in self.market_items):
            return f"❌ El personaje '{character_name}' ya está en el mercado."
    
        # Registrar el personaje en el mercado
        self.market_items.append({
            'character': character,
            'price': price,
            'seller': user_id
        })
    
        return f"✅ El personaje '{character_name}' ha sido puesto a la venta por {price} monedas."
    
        return f"✅ El personaje '{character_name}' ha sido puesto a la venta por {price} monedas."

    def view_market(self):
        if not self.market_items:
            return "El mercado está vacío."
        return "\n".join([f"{item['character']['name']} - {item['price']} monedas (Vendedor: {item['seller']})" for item in self.market_items])

    def buy_character(self, buyer_id, character_name):
        buyer = self.users.get(buyer_id)
        if not buyer:
            return "Usuario no encontrado."
        item = next((i for i in self.market_items if i['character']['name'] == character_name), None)
        if not item:
            return "Personaje no encontrado en el mercado."
        if buyer['money'] < item['price']:
            return "No tienes suficiente dinero."
        seller = self.users.get(item['seller'])
        if seller:
            seller['money'] += item['price']
        buyer['money'] -= item['price']
        buyer['characters'].append(item['character'])
        item['character']['purchase_price'] = item['price']
        self.market_items.remove(item)
        return f"Has comprado a {character_name} por {item['price']} monedas."

    def sell_in_blackmarket(self, user_id, character_name, price):
        user = self.users.get(user_id)
        if not user:
            return "Usuario no encontrado."
        character = next((c for c in user['characters'] if c['name'] == character_name), None)
        if not character or not character['stolen']:
            return "Solo puedes vender personajes robados en el mercado negro."
        self.blackmarket_items.append({'seller': user_id, 'character': character, 'price': price})
        user['characters'].remove(character)
        return f"Personaje {character_name} puesto a la venta en el mercado negro por {price} monedas."

    def view_blackmarket(self, user_id):
        user = self.users.get(user_id)
        if not user:
            return "Usuario no encontrado."
        if user['reputation'] > -300:
            return "No tienes acceso al mercado negro."
        if not self.blackmarket_items:
            return "El mercado negro está vacío."
        return "\n".join([f"{item['character']['name']} - {item['price']} monedas (Vendedor: {item['seller']})" for item in self.blackmarket_items])

    def open_lootbox(self, user_id, rarity):
        lootbox_prices = {'SSS': 1000, 'SS': 750, 'S': 500, 'A': 250, 'B': 100, 'C': 50}
        lootbox_chances = {'SSS': 1, 'SS': 5, 'S': 10, 'A': 20, 'B': 30, 'C': 34}
        user = self.users.get(user_id)
        if not user:
            return "Usuario no encontrado."
        if rarity not in lootbox_prices:
            return "Rareza inválida."
        if user['money'] < lootbox_prices[rarity]:
            return "No tienes suficiente dinero."
        user['money'] -= lootbox_prices[rarity]
        roll = random.randint(1, 100)
        for r, chance in lootbox_chances.items():
            if roll <= chance:
                character = {'name': f"Personaje {r}", 'rarity': r, 'purchase_price': lootbox_prices[r], 'stolen': False}
                user['characters'].append(character)
                return f"¡Has obtenido a {character['name']} de rareza {r}!"
            roll -= chance
        return "No obtuviste ningún personaje."

    def gift_character(self, giver_id, character_name, receiver_id):
        giver = self.users.get(giver_id)
        receiver = self.users.get(receiver_id)
        if not giver or not receiver:
            return "Usuario no encontrado."
        character = next((c for c in giver['characters'] if c['name'] == character_name), None)
        if not character:
            return "Personaje no encontrado."
        giver['characters'].remove(character)
        receiver['characters'].append(character)
        return f"Has regalado a {character_name} a {receiver_id}."

    def gift_money(self, giver_id, amount, receiver_id):
        giver = self.users.get(giver_id)
        receiver = self.users.get(receiver_id)
        if not giver or not receiver:
            return "Usuario no encontrado."
        if giver['money'] < amount:
            return "No tienes suficiente dinero."
        giver['money'] -= amount
        receiver['money'] += amount
        return f"Has regalado {amount} monedas a {receiver_id}."

    @bot.slash_command(name="vender", description="🛒 Pon un personaje a la venta en el mercado.")
    async def vender(self, ctx, character_name: str, price: int):
        """
        Comando para poner un personaje a la venta en el mercado.
        """
        try:
            user_id = ctx.author.id
    
            # Registrar el personaje en el mercado
            resultado = self.sell_character(user_id, character_name, price)
            await ctx.respond(resultado)
    
        except Exception as e:
            print(f"Error en comando /vender: {e}")
            await ctx.respond("❌ Ocurrió un error al intentar poner el personaje a la venta.", ephemeral=True)

    @bot.slash_command(name="mercado", description="📜 Muestra los personajes disponibles en el mercado.")
    async def mercado(self, ctx):
        resultado = self.view_market()
        await ctx.respond(resultado)

    @bot.slash_command(name="regalar_monedas", description="🎁 Regala monedas a otro usuario.")
    async def regalar_monedas(self, ctx, receiver: discord.Member, amount: int):
        giver_id = ctx.author.id
        receiver_id = receiver.id
        resultado = self.gift_money(giver_id, amount, receiver_id)
        await ctx.respond(resultado)

    @bot.slash_command(name="lootbox", description="🎁 Abre una lootbox para obtener un personaje.")
    async def lootbox(self, ctx, rarity: str):
        user_id = ctx.author.id
        resultado = self.open_lootbox(user_id, rarity)
        await ctx.respond(resultado)

def setup(bot: discord.Bot):
    print("✅ Market cargado")
    bot.add_cog(Market(bot))