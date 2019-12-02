from discord.ext.commands import Converter, CommandError
from dateparser import parse
from datetime import datetime, timedelta
from pytz import timezone


class DateConverter(Converter):
    async def convert(self, ctx, argument):
        parser_settings = {
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
            "TIMEZONE": "CET"
        }
        argument = argument.replace('for', 'in')
        argument = argument.replace('voor', 'over')
        argument = argument.replace('tot', 'om')
        try:
            date = parse(argument, languages=['en', 'nl'], settings=parser_settings)
        except Exception as e:
            raise CommandError(e)
        tz = timezone('Europe/Amsterdam')
        if date <= datetime.now(tz=tz):
            if ':' in argument:
                date = date + timedelta(days=1)
            else:
                date = datetime.now(tz=tz) + (datetime.now(tz=tz) - date)
        if not date:
            raise CommandError("Invalid Date")
        return date
