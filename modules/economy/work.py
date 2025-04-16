import discord
from discord.ext import commands
import random
from datetime import timedelta
from utils.database import Database

class CrimeSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        
        # Trabajos normales (fachada legal)
        self.jobs = [
            {
                "name": "Fábrica de juguetes",
                "emoji": "🧸",
                "success": [
                    "Fingiste trabajar y robaste {} en piezas de Lego para revender en el mercado negro",
                    "Te pagaron {} por 'probarte' los trajes de peluche en el baño",
                    "Vendiste {} en muñecas inflables 'de prueba' a tus compañeros"
                ],
                "fail": [
                    "Te pillaron cogiéndote un osito en el almacén. Multa de {} y despido por pervertido",
                    "El jefe te encontró usando el vibrador industrial 'para calmar el estrés'. {} de sanción",
                    "Gastaste {} en gasolina para quemar la evidencia de tus 'experimentos' con las muñecas"
                ],
                "min": 100,
                "max": 300
            },
            {
                "name": "Repartidor de OnlyPacks",
                "emoji": "📦",
                "success": [
                    "Robaste {} en contenido premium de clientes y lo vendiste en Telegram",
                    "Extorsionaste a un streamer con sus nudes. Ganaste {} monedas",
                    "Vendiste {} en direcciones falsas a pajeros desesperados"
                ],
                "fail": [
                    "Te cacharon chupándote un paquete literalmente. Multa de {} y terapia obligatoria",
                    "Confundiste un vibrador con walkie-talkie. La policía te decomisó {} monedas",
                    "Un cliente te exigió 'pruebas de calidad'. Perdiste {} en hospital por desgarro"
                ],
                "min": 200,
                "max": 500
            }
        ]
        
        # Crimen real (sin disfraces)
        self.crimes = [
            {
                "name": "Atraco al banco de semen",
                "emoji": "🏦",
                "success": [
                    "Robaste {} en 'material genético premium' y lo vendiste como bebé de Elon Musk",
                    "Chantajeaste a los donantes con sus pajas grabadas. Ganaste {}",
                    "Vendiste {} en muestras falsas de Cristiano Ronaldo"
                ],
                "fail": [
                    "Confundiste el banco con un sex-shop. Ahora debes {} por limpieza de paredes",
                    "Te atrapó seguridad mientras gritabas '¡Esto es un puto robo!'. Multa: {}",
                    "Los frascos explotaron en tu mochila. Gastaste {} en traumas infantiles ajenos"
                ],
                "min": 500,
                "max": 1000,
                "risk": 0.6
            },
            {
                "name": "Secuestro de influencers",
                "emoji": "👙",
                "success": [
                    "Cobraste {} por devolver a una tiktoker sin su filtro de nariz",
                    "Vendiste los nudes de un gamer por {} antes de liberarlo",
                    "Extorsionaste a un político con su OnlyFans secreto. Ganaste {}"
                ],
                "fail": [
                    "El 'influencer' resultó ser un policía encubierto. Fianza: {}",
                    "Te grabaron pidiendo rescate en Twitch. Multa de {} por pena ajena",
                    "El streamer te doxxeó en vivo. Gastaste {} en mudarte a Somalia"
                ],
                "min": 700,
                "max": 1500,
                "risk": 0.7
            }
        ]

    def _calc_risk(self, rep):
        """Más reputación = más probabilidad de que te caguen"""
        return 0.5 + (abs(rep) / 200)  # 50% base + hasta 50% extra

    @bot.slash_command(name="trabajar", description="Trabajo normal (para no morir de hambre)")
    async def work(self, ctx):
        """Trabajo normal (para no morir de hambre)"""
        await self._execute_crime(ctx, self.jobs, is_crime=False)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining = str(timedelta(seconds=int(error.retry_after)))
            await ctx.respond(f"⏳ ¡Estás agotado! Descansa un poco. Podrás trabajar nuevamente en {remaining}")

    @bot.slash_command(name="crimen", description="Dinero fácil, consecuencias difíciles")
    async def crime(self, ctx):
        """Dinero fácil, consecuencias difíciles"""
        await self._execute_crime(ctx, self.crimes, is_crime=True)

    @crime.error
    async def crime_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining = str(timedelta(seconds=int(error.retry_after)))
            await ctx.respond(f"⏳ La policía está vigilando. Vuelve a intentarlo en {remaining}")

    async def _execute_crime(self, ctx, crimes_list, is_crime):
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild.id)
        user = self.db.get_user(user_id, server_id)
        crime = random.choice(crimes_list)
        
        # ¿Éxito o cagada?
        risk = crime.get("risk", 0.3) if is_crime else 0.2
        adjusted_risk = self._calc_risk(user["reputation"]) * risk
        is_success = random.random() > adjusted_risk

        amount = random.randint(crime["min"], crime["max"])
        
        if is_success:
            msg = random.choice(crime["success"]).format(amount)
            new_coins = user["coins"] + amount
            rep_change = -3 if is_crime else 1
            color = 0x00ff00
        else:
            lost = int(amount * (0.8 if is_crime else 0.5))
            msg = random.choice(crime["fail"]).format(lost)
            new_coins = max(0, user["coins"] - lost)
            rep_change = -5 if is_crime else -1
            color = 0xff0000

        new_rep = max(-100, min(100, user["reputation"] + rep_change))
        
        self.db.update_user(
            user_id,
            server_id,
            {"coins": new_coins, "reputation": new_rep}
        )

        embed = discord.Embed(
            title=f"{crime['emoji']} {crime['name']}",
            description=msg,
            color=color
        )
        await ctx.respond(embed=embed)

async def setup(bot):
    await bot.add_cog(CrimeSystem(bot))
