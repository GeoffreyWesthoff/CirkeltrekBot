from discord import Member
from discord.ext.commands import MissingPermissions, BotMissingPermissions, MissingRequiredArgument, BadArgument
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, CommandInvokeError


class Kick(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='[member]', category='Moderatie', aliases=['doei'], permissions='KICK MEMBERS')
    @has_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *reason):
        """Kicks a member"""
        lang = self.bot.utils.get_language(ctx.guild.id)
        if ctx.author.top_role < member.top_role:
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['above'])
            return
        if ctx.author == member:
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['self'])
            return
        if reason:
            reason = ' '.join(reason)
            await member.kick(reason=f'{ctx.author.mention}: {reason}')
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['kick_reason'] % (member, reason))
        else:
            await member.kick()
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['kicked'] % member)

    @kick.error
    async def handle_error(self, ctx, error):
        lang = self.bot.utils.get_language(ctx.guild.id)
        if isinstance(error, CommandInvokeError):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['above_bot'])
        elif isinstance(error, MissingPermissions):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['no_perms'])
        elif isinstance(error, BotMissingPermissions):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['kick']['no_perms_bot'])
        elif isinstance(error, MissingRequiredArgument):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['errors']['no_member'])
        elif isinstance(error, BadArgument):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['errors']['not_found'])


def setup(bot):
    bot.add_cog(Kick(bot))
