from discord import utils as discord_utils
from discord.ext.commands import check


class Checks:
    def __init__(self, utils):
        self.utils = utils
        self.bot = utils.bot

    @staticmethod
    def can_ban_member(target):
        if not target:
            return False
        perm = target.guild.me.guild_permissions.ban_members
        hierarchy = target.guild.me.top_role > target.top_role
        return perm and hierarchy

    @staticmethod
    def can_kick_member(target):
        if not target:
            return False
        perm = target.guild.me.guild_permissions.kick_members
        hierarchy = target.guild.me.top_role > target.top_role
        return perm and hierarchy

    @staticmethod
    def can_apply_role(role):
        if not role:
            return False
        perm = role.guild.me.guild_permissions.manage_roles
        hierarchy = role.guild.me.top_role > role
        return perm and hierarchy

    @staticmethod
    def can_send_message(channel, embed=False):
        if not channel:
            return False
        perm = channel.permissions_for(channel.guild.me)
        if not embed:
            return bool(perm.send_messages)
        else:
            return bool(perm.send_messages and perm.embed_links)

    def can_manage_guild(self, member):
        if not member:
            return False
        if member.guild_permissions.manage_guild:
            return True
        admin_role_list = []
        admin_role_id_list = self.utils.bot.settings_entry(member.guild.id).admin_roles
        for role_id in admin_role_id_list:
            try:
                admin_role = discord_utils.get(member.guild.roles, id=role_id)
            except ValueError:
                continue
            if not admin_role:
                continue
            else:
                admin_role_list.append(admin_role)
        for role in member.roles:
            if role in admin_role_list:
                return True
            else:
                continue
        else:
            return False

    @staticmethod
    def has_mod_permission():
        def predicate(ctx):
            return Checks.is_mod(ctx.bot, ctx.author)
        return check(predicate)

    @staticmethod
    def has_admin_permission():
        def predicate(ctx):
            return Checks.is_admin(ctx.bot, ctx.author)
        return check(predicate)

    def is_mod(self, member):
        bot = getattr(self, 'bot', self)
        mod_roles = bot.settings_entry(member.guild.id).mod_roles
        return Checks.is_mod_or_admin(member, mod_roles)

    def is_admin(self, member):
        bot = getattr(self, 'bot', self)
        admin_roles = bot.settings_entry(member.guild.id).admin_roles
        return Checks.is_mod_or_admin(member, admin_roles)

    def is_both(self, member):
        bot = getattr(self, 'bot', self)
        mod_roles = bot.settings_entry(member.guild.id).mod_roles
        admin_roles = bot.settings_entry(member.guild.id).admin_roles
        return Checks.is_mod_or_admin(member, (mod_roles + admin_roles))

    @staticmethod
    def is_mod_or_admin(member, role_list=None):
        if member.guild_permissions.manage_guild:
            return True
        for role_id in role_list:
            role = discord_utils.get(member.guild.roles, id=role_id)
            if role in member.roles:
                return True
        else:
            return False
