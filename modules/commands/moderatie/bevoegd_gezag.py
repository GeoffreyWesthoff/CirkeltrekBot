from discord.ext.commands import command, Cog, has_permissions
from discord import Embed, Colour
from datetime import datetime


class BevoegdGezag(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='[member]', category='Moderatie', aliases=['bg'], permissions='MANAGE ROLES')
    @has_permissions(manage_roles=True)
    async def bevoegdgezag(self, ctx, *, bericht: str = None):
        """Officieel moderatie bericht!"""
        if not bericht:
            return await ctx.send('Voer een bericht in kut!')
        em = Embed(title='Bevoegd Gezag', description=bericht + '\n\n**Bevoegd Gezag is een officieel en serieus Stadthouder bericht!\n'
                           'Naar de opdracht in dit bericht moet worden geluisterd!**', timestamp=datetime.utcnow(), color=Colour.from_rgb(30, 151, 39))
        em.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        em.set_footer(icon_url=ctx.guild.icon_url, text=ctx.guild.name)
        await ctx.message.delete()
        return await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(BevoegdGezag(bot))
