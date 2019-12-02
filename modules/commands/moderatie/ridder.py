from discord.ext.commands import command, Cog, has_permissions, Greedy
from typing import Union
from discord import Member, HTTPException
from ...helpers.dateconvert import DateConverter
from ...helpers.get_roles import Roles
from babel.dates import format_datetime
from datetime import datetime
import ujson as json


class Ridderen(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(usage='[member]', category='Moderatie', aliases=['r'], permissions='MANAGE ROLES')
    @has_permissions(manage_roles=True)
    async def ridderen(self, ctx, members: Greedy[Member], expire: Union[DateConverter, str] = None, *,
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
                await member.remove_roles(rollen.stadthouder, reason=f";r door {ctx.author} {reason}") \
                    if rollen.stadthouder in member.roles else None
            await member.remove_roles(rollen.spanjool, reason=f";r door {ctx.author} {reason}")\
                if rollen.spanjool not in member.roles else None
            await member.remove_roles(rollen.alva, reason=f";r door {ctx.author} {reason}")\
                if rollen.alva in member.roles else None
            await member.remove_roles(rollen.kop_dicht, reason=f";r door {ctx.author} {reason}")\
                if rollen.kop_dicht in member.roles else None
            if rollen.ridder not in member.roles:
                await member.add_roles(rollen.ridder, reason=f";r door {ctx.author} {reason}")
                straf_bericht = f'{member} is ridder '
                infraction = {"user": member.id, "punishment": "ridder", "time": datetime.utcnow()}
                punished.append(str(member))
                if expire:
                    ftime = format_datetime(expire, "EEEE, d-MM-yyyy 'om' H:mm",  locale="nl")
                    straf_bericht = straf_bericht + f'tot {ftime} '
                    infraction['expire'] = expire
                if reason:
                    straf_bericht = straf_bericht + reason
                    infraction['reason'] = reason
                self.bot.mongo.infractions.insert_one(infraction)
                straf_berichten.append(straf_bericht)
                self.bot.redis.set(f'user:{member.id}:current_punishment', 'ridder')
                if expire:
                    self.bot.redis.hset(f'punishments', str(member.id),
                                        json.dumps({"expire": int(expire.timestamp()), "punishment": "ridder"}))
        try:
            straf = await rollen.straffen.send('\n'.join(straf_berichten))
        except HTTPException:
            await ctx.send('Ik kon deze leden niet ridderen!')
        self.bot.redis.hmset(f'straf_berichten', {"message": f"{straf.id},{datetime.utcnow().timestamp()}"})
        await ctx.message.add_reaction("👍")


def setup(bot):
    bot.add_cog(Ridderen(bot))
