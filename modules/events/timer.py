from discord.ext.commands import Cog
from discord.ext.tasks import loop
from ..helpers.get_roles import Roles
from time import time
import ujson as json


class Timer(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.punishment_timer.start()

    @loop(seconds=5)
    async def punishment_timer(self):
        guild = self.bot.get_guild(241646621283057665)
        roles = Roles(guild.roles, guild.channels, self.bot.settings_entry(guild.id))
        punishments = self.bot.redis.hgetall('punishments')
        for member_id, obj in punishments.items():
            member = guild.get_member(int(member_id))
            if not member:
                continue
            punishment_obj = json.loads(obj)
            if int(time()) >= punishment_obj['expire']:
                if roles.admin in member.roles and roles.stadthouder not in member.roles:
                    await member.add_roles(roles.stadthouder, reason='Straf Verlopen')
                elif roles.admin not in member.roles and roles.burgerij not in member.roles:
                    await member.add_roles(roles.burgerij, reason='Straf Verlopen')
                if punishment_obj['punishment'] == 'spanjool':
                    if roles.spanjool in member.roles:
                        await member.remove_roles(roles.spanjool, reason='Straf Verlopen')
                        await roles.straffen.send(f'Eindelijk. {member.mention} is geen vuile spanjool meer!')
                if punishment_obj['punishment'] == 'alva':
                    if roles.alva in member.roles:
                        await member.remove_roles(roles.alva, reason='Straf Verlopen')
                        await roles.straffen.send(f'De verrader {member.mention} is vergeven en is geen vieze Alva meer!')
                if punishment_obj['punishment'] == 'ridder':
                    if roles.ridder in member.roles:
                        await member.remove_roles(roles.ridder, reason='Straf Verlopen')
                        await roles.straffen.send(f'Helaas {member.mention}, je behoort niet langer meer tot de Ridderlijke Orde!')
                if punishment_obj['punishment'] == 'kopdicht':
                    if roles.kop_dicht in member.roles:
                        await member.remove_roles(roles.kop_dicht, reason='Straf Verlopen')
                        await roles.straffen.send(f'Helaas mag {member.mention} hun kop weer opentrekken!')
                self.bot.redis.hdel('punishments', str(member.id))
                return

    @punishment_timer.after_loop
    async def after(self):
        print(self.punishment_timer.get_task().exception())

    @punishment_timer.before_loop
    async def before(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Timer(bot))
