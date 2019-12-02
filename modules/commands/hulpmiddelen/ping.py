from discord.ext.commands import command, Cog


class Ping(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(category='Hulpmiddelen')
    async def ping(self, ctx):
        """Honestly every bot just needs this"""
        if self.bot.utils.checks.can_send_message(ctx.channel):
            lang = self.bot.utils.get_language(ctx.guild.id)
            await ctx.send(lang['commands']['ping'] % round(self.bot.latency*1000))


def setup(bot):
    bot.add_cog(Ping(bot))
