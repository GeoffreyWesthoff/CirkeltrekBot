from discord import Member
from discord.ext.commands import MissingPermissions, BotMissingPermissions, MissingRequiredArgument, BadArgument
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, CommandInvokeError


class Ban(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='[member] <delete message days> <reason>', category='Moderatie', permissions='BAN MEMBERS')
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, days: int = 1,  *reason):
        """Bans a member"""
        if days > 7:
            days = 7
        if days < 0:
            days = 0
        lang = self.bot.utils.get_language(ctx.guild.id)
        if ctx.author.top_role < member.top_role:
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['ban']['above'])
            return
        if ctx.author == member:
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['ban']['self'])
            return
        if reason:
            reason = ' '.join(reason)
            await member.ban(reason=f'{ctx.author.mention}: {reason}', delete_message_days=days)
            if self.bot.utils.checks.can_send_message(ctx.channel):
                return await ctx.send(lang['commands']['ban']['ban_reason'] % (member, reason))
        else:
            await member.ban(delete_message_days=days)
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['ban']['banned'] % member)

    @ban.error
    async def handle_error(self, ctx, error):
        lang = self.bot.utils.get_language(ctx.guild.id)
        if isinstance(error, CommandInvokeError):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['ban']['above_bot'])
        elif isinstance(error, MissingPermissions):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['ban']['no_perms'])
        elif isinstance(error, BotMissingPermissions):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['commands']['ban']['no_perms'])
        elif isinstance(error, MissingRequiredArgument):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['errors']['no_member'])
        elif isinstance(error, BadArgument):
            if self.bot.utils.checks.can_send_message(ctx.channel):
                await ctx.send(lang['errors']['not_found'])


def setup(bot):
    bot.add_cog(Ban(bot))
