from typing import Union

from discord import Member, User, Embed, NotFound
from discord.ext.commands import command, Cog, BadUnionArgument


class Userinfo(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='<user>', aliases=['whois', 'wiemst'], category='Hulpmiddelen')
    async def userinfo(self, ctx, *, member: Union[Member, User] = None):
        """Show info about yourself or others"""
        if not member:
            member = ctx.author
        lang = self.bot.utils.get_language(ctx.author.guild.id)
        em = Embed(color=member.color)
        em.set_author(name=str(member), icon_url=member.avatar_url)
        em.set_thumbnail(url=member.avatar_url)
        em.add_field(name=lang['commands']['user_info']['creation'],
                     value=str(member.created_at.strftime(lang['commands']['user_info']['time'])))
        if isinstance(member, Member):
            em.add_field(name=lang['commands']['user_info']['join'],
                         value=str(member.joined_at.strftime(lang['commands']['user_info']['time'])))
        em.add_field(name=lang['commands']['user_info']['status'], value=str(member.status))
        if member.id == member.guild.owner.id:
            em.add_field(name=lang['commands']['user_info']['owner'], value=lang['commands']['user_info']['yes'])
        em.set_footer(text='ID: {}'.format(str(member.id)), icon_url=ctx.guild.icon_url)
        if self.bot.utils.checks.can_send_message(ctx.channel, True):
            await ctx.send(embed=em)
        elif self.bot.utils.checks.can_send_message(ctx.channel):
            await ctx.send(self.bot.utils.embed_to_codeblock(em))

    @userinfo.error
    async def error_handler(self, ctx, error):
        lang = self.bot.utils.get_language(ctx.author.guild.id)
        if isinstance(error, NotFound) and self.bot.utils.checks.can_send_message(ctx.channel):
            return await ctx.send(lang['commands']['errors']['not_found'])
        elif isinstance(error, BadUnionArgument) and self.bot.utils.checks.can_send_message(ctx.channel):
            return await ctx.send(lang['commands']['errors']['not_found'])


def setup(bot):
    bot.add_cog(Userinfo(bot))
