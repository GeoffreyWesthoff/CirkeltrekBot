from discord.ext.commands import Cog, command, has_permissions
import discord


class Artikel5(Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permissions(manage_guild=True)
    @command(category='Plezier', usage='')
    async def artikel5(self, ctx):
        """Douw je stadthouderpenis ff lekker naar buiten"""
        return await ctx.send(file=discord.File('artikel5.png'))


def setup(bot):
    bot.add_cog(Artikel5(bot))
