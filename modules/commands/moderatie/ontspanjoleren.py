from discord.ext.commands import command, Cog, has_permissions, Greedy
from discord import Member
from ...helpers.get_roles import Roles


class OntSpanjoleren(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='[member]', category='Moderatie', aliases=['os'], permissions='MANAGE ROLES')
    @has_permissions(manage_roles=True)
    async def ontspanjoleren(self, ctx, members: Greedy[Member], reason: str = ''):
        settings = self.bot.settings_entry(ctx.guild.id)
        rollen = Roles(ctx.guild.roles, ctx.guild.channels, settings)
        punished = list()
        straf_berichten = list()
        if not reason:
            reason = "voor een onbekende reden!"
        else:
            reason = 'omdat ' + reason
        for member in members:
            if rollen.admin in member.roles:
                await member.add_roles(rollen.stadthouder, reason=f";os door {ctx.author} {reason}")\
                    if rollen.stadthouder not in member.roles else None
                await member.remove_roles(rollen.ridder, reason=f";os door {ctx.author} {reason}")\
                    if rollen.ridder in member.roles else None
            else:
                await member.add_roles(rollen.burgerij, reason=f";os door {ctx.author} {reason}")\
                    if rollen.burgerij not in member.roles else None
            await member.remove_roles(rollen.ridder, reason=f";os door {ctx.author} {reason}")\
                if rollen.ridder in member.roles else None
            await member.remove_roles(rollen.alva, reason=f";os door {ctx.author} {reason}")\
                if rollen.alva in member.roles else None
            await member.remove_roles(rollen.kop_dicht, reason=f";os door {ctx.author} {reason}")\
                if rollen.kop_dicht in member.roles else None
            if rollen.spanjool in member.roles:
                await member.remove_roles(rollen.spanjool, reason=f";os door {ctx.author} {reason}")
                straf_bericht = f'{member} is geen spanjool meer '
                if reason:
                    straf_bericht = straf_bericht + reason
                punished.append(str(member))
                straf_berichten.append(straf_bericht)
                self.bot.redis.set(f'user:{member.id}:current_punishment', 'geen')
        await rollen.straffen.send('\n'.join(straf_berichten))
        await ctx.message.add_reaction("👍")


def setup(bot):
    bot.add_cog(OntSpanjoleren(bot))
