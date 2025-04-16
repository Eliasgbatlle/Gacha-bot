import discord
from discord.ext import commands
import random
from utils.database import Database

class WorkSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # Trabajos legales (para todos)
        self.jobs = [
            {
                "name": "🧸 Fabricante de ositos de peluche",
                "emoji": "🧵",
                "success": [
                    "¡Armaste 50 ositos con caritas adorables! Ganaste {} monedas",
                    "Los niños amarán tus creaciones. Recompensa: {} monedas"
                ],
                "fail": [
                    "Te pillaron cogiendo un osito 'para probar su suavidad'. Multa de {} monedas",
                    "¡Despedido! Usaste peluche de relleno para hacer almohadas 'para adultos'. Pierdes {} monedas"
                ],
                "min": 80,
                "max": 200
            },
            {
                "name": "🍩 Panadero de donas",
                "emoji": "👨‍🍳",
                "success": [
                    "Horneaste donas tan perfectas que Homer Simpson lloró. Ganaste {} monedas",
                    "Vendiste todas tus donas glaseadas. Recaudaste {} monedas"
                ],
                "fail": [
                    "Te comiste toda la mercancía. Debes pagar {} monedas por los ingredientes",
                    "¡Donas con picante! Los clientes demandaron. Multa de {} monedas"
                ],
                "min": 60,
                "max": 180
            }
        ]

    def calculate_success_rate(self, reputation):
        """Calcula probabilidad de éxito basada en reputación (-100 a 100)"""
        # Neutral (0 rep): 80% éxito | Extremos: 30% (muy bueno/malo)
        return 0.8 - (abs(reputation) / 250)

    @commands.command(name="trabajar")
    async def work(self, ctx):
        """Trabaja y gana dinero (con riesgos cómicos!)"""
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)
        user = self.db.get_user(user_id, server_id)
        job = random.choice(self.jobs)
        
        # Calcular éxito/fallo
        success_rate = self.calculate_success_rate(user["reputation"])
        is_success = random.random() < success_rate
        
        # Generar recompensa/pérdida
        amount = random.randint(job["min"], job["max"])
        
        if is_success:
            message = random.choice(job["success"]).format(amount)
            self.db.update_user(user_id, server_id, {"coins": user["coins"] + amount})
            color = 0x00ff00
            footer = f"Prob. éxito: {success_rate*100:.0f}%"
        else:
            lost = int(amount * 0.7)
            message = random.choice(job["fail"]).format(lost)
            self.db.update_user(user_id, server_id, {"coins": max(0, user["coins"] - lost)})
            color = 0xff0000
            footer = f"Prob. fallo: {100-success_rate*100:.0f}%"
            
            # Pequeño cambio de reputación aleatorio
            rep_change = random.choice([-2, -1, 0, 1])
            self.db.update_user(user_id, server_id, {"reputation": user["reputation"] + rep_change})

        # Construir embed
        embed = discord.Embed(
            title=f"{job['emoji']} {job['name']}",
            description=message,
            color=color
        )
        embed.set_footer(text=footer)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WorkSystem(bot))