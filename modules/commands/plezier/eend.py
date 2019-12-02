from discord import Embed
from discord.ext.commands import command, Cog


class Eend(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(category='Plezier', usage='')
    async def eend(self, ctx):
        """Haha eent"""
        async with self.bot.web.get('https://random-d.uk/api/v1/quack') as r:
            response = await r.json()
            embed = Embed(title='haha eent')
            embed.set_image(url=response['url'])
            embed.set_footer(text=response['message'])
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Eend(bot))

