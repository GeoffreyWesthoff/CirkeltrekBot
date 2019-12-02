from sys import version_info

from discord import Embed, __version__ as discord_version
from discord.ext.commands import command, Cog


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(category='Hulpmiddelen')
    async def info(self, ctx):
        """Bot statistics and information"""
        user_count = int(self.bot.redis.get('user_count'))
        guild_count = int(self.bot.redis.get('guild_count'))
        lang = self.bot.utils.get_language(ctx.author.guild.id)
        owner = self.bot.get_user(self.bot.owner_id)
        em = Embed(description=lang['commands']['info']['desc'])
        em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        em.add_field(name=lang['commands']['info']['python'],
                     value=f'{version_info.major}.{version_info.minor}.{version_info.micro}')
        em.add_field(name=lang['commands']['info']['guilds'], value=f'{guild_count}')
        em.add_field(name=lang['commands']['info']['d_py_version'], value=f'{discord_version}')
        em.add_field(name=lang['commands']['info']['cluster'], value=f'{self.bot.cluster_name} ({self.bot.cluster_id})')
        em.add_field(name=lang['commands']['info']['shards'], value=f"{ctx.guild.shard_id}/{self.bot.shard_count} {lang['commands']['info']['shard_info']}")
        em.add_field(name=lang['commands']['info']['owner'], value=f'{owner}')
        em.add_field(name=lang['commands']['info']['ping'], value=f'{round(self.bot.latency*1000)}ms')
        em.add_field(name=lang['commands']['info']['users'], value=f'{user_count}')
        em.add_field(name=lang['commands']['info']['support'], value='<https://altdentifier.com/support>', inline=False)
        em.add_field(name=lang['commands']['info']['site'], value='https://altdentifier.com', inline=False)
        em.set_footer(text=lang['commands']['info']['id'] % self.bot.user.id)
        if self.bot.utils.checks.can_send_message(ctx.channel, True):
            await ctx.send(embed=em)
        elif self.bot.utils.checks.can_send_message(ctx.channel):
            await ctx.send(self.bot.utils.embed_to_codeblock(em))


def setup(bot):
    bot.add_cog(Info(bot))
