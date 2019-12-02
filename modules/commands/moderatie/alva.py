from discord.ext.commands import command, Cog, has_permissions, Greedy
from typing import Union
from discord import Member
from ...helpers.dateconvert import DateConverter
from ...helpers.get_roles import Roles
from babel.dates import format_datetime
from datetime import datetime
import ujson as json

class Alva(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='[member]', category='Moderatie', aliases=['a'], permissions='MANAGE ROLES')
    @has_permissions(manage_roles=True)
    async def alva(self, ctx, members: Greedy[Member], expire: Union[DateConverter, str] = None, *,
                          reason: str = ''):
        if isinstance(expire, str):
            reason = expire + ' ' + reason
            expire = None
        if not reason:
            reason = "voor een onbekende reden"
        else:
            reason = 'omdat ' + reason
        settings = self.bot.settings_entry(ctx.guild.id)
        rollen = Roles(ctx.guild.roles, ctx.guild.channels, settings)
        punished = list()
        straf_berichten = list()
        for member in members:
            if rollen.admin in member.roles:
                await member.remove_roles(rollen.stadthouder, reason=f";a door {ctx.author} {reason}")\
                    if rollen.stadthouder in member.roles else None
                await member.remove_roles(rollen.ridder, reason=f";a door {ctx.author} {reason}")\
                    if rollen.ridder in member.roles else None
            else:
                await member.remove_roles(rollen.burgerij, reason=f";a door {ctx.author} {reason}")\
                    if rollen.burgerij in member.roles else None
            await member.remove_roles(rollen.ridder, reason=f";a door {ctx.author} {reason}")\
                if rollen.ridder in member.roles else None
            await member.remove_roles(rollen.spanjool, reason=f";a door {ctx.author} {reason}")\
                if rollen.spanjool in member.roles else None
            await member.remove_roles(rollen.kop_dicht, reason=f";a door {ctx.author} {reason}")\
                if rollen.kop_dicht in member.roles else None
            if rollen.alva not in member.roles:
                await member.add_roles(rollen.alva, reason=f";a door {ctx.author} {reason}")
                straf_bericht = f'{member} is alva '
                infraction = {"user": member.id, "punishment": "alva", "time": datetime.utcnow()}
                punished.append(str(member))
                if expire:
                    ftime = format_datetime(expire, "EEEE, d MMMM yyyy 'om' H:mm",  locale="nl")
                    straf_bericht = straf_bericht + f'tot {ftime} '
                    infraction['expire'] = expire
                if reason:
                    straf_bericht = straf_bericht + reason
                    infraction['reason'] = reason
                self.bot.mongo.infractions.insert_one(infraction)
                straf_berichten.append(straf_bericht)
                self.bot.redis.set(f'user:{member.id}:current_punishment', 'alva')
                if expire:
                    self.bot.redis.hset(f'punishments', str(member.id),
                                        json.dumps({"expire": int(expire.timestamp()), "punishment": "alva"}))
        straf = await rollen.straffen.send('\n'.join(straf_berichten))
        self.bot.redis.hmset(f'straf_berichten', {"message": f"{straf.id},{datetime.utcnow().timestamp()}"})
        await ctx.message.add_reaction("👍")


def setup(bot):
    bot.add_cog(Alva(bot))
