from discord.ext.commands import Cog, command, cooldown, BucketType, Cooldown, CommandOnCooldown, CommandError
from io import BytesIO
from discord import File


class Krab(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = self.bot.settings.get('memer_token')

    @command(category='Plezier', usage='')
    @cooldown(1, 30.0, BucketType.default)
    async def krab(self, ctx, top: str, bottom: str = None):
        """:crab: HAAN IS HOOG :crab:"""
        x = await ctx.send(':crab: MEEM AAN HET MAKEN, EVEN GEDULD AUB :crab:')
        if not bottom:
            text = top
        else:
            text = ','.join([top, bottom])
        params = {"text": text}
        auth = {"Authorization": self.token}
        async with self.bot.web.get('https://dankmemer.services/api/crab', params=params, headers=auth) as r:
            if r.status == 429:
                raise CommandOnCooldown(cooldown=Cooldown(1, 30, BucketType.default),
                                                 retry_after=30.0)
            elif r.status != 200:
                raise CommandError
            resp = await r.content.read()
        b = BytesIO(resp)
        f = File(b, filename='krab.mp4')
        await x.delete()
        return await ctx.send(content=':crab: {} :crab:'.format(text.replace(",", " ").upper()), file=f)

    @krab.error
    async def on_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            return await ctx.send('Even geduld a.u.b., je kan over {} seconden dit weer gebruiken'.format(str(int(error.retry_after))))
        elif isinstance(error, CommandError):
            print(error)
            return await ctx.send('Allicht foutje gepleegd!')
        else:
            print(error)


def setup(bot):
    bot.add_cog(Krab(bot))
