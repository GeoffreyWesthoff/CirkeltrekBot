from discord import Embed, TextChannel, VoiceChannel, CategoryChannel, StoreChannel
from discord.ext import commands

from .checks import Checks
from .language import Language
from .settings_entry import SettingsEntry


class Utilities:
    def __init__(self, bot):
        self.settings_cache = dict()
        self.bot = bot
        self.checks = Checks(self)

    def settings_entry(self, guild_id: int):
        entry = self.settings_cache.get(guild_id, None)
        if not entry:
            entry = self.bot.mongo.guilds.find_one({"_id": guild_id}, {"settings": 1})
            if entry:
                entry = entry.get('settings', None)
                if entry:
                    entry = SettingsEntry(self.bot, guild_id, entry)
                else:
                    entry = SettingsEntry(self.bot, guild_id, dict())
            else:
                entry = SettingsEntry(self.bot, guild_id, dict())
            self.settings_cache[guild_id] = entry
        return entry

    def get_language(self, guild_id):
        try:
            lang = self.bot.settings_entry(guild_id).locale
            return Language(self.bot.langs.get(lang), self.bot.langs.get('en'))
        except Exception as e:
            return Language(self.bot.langs.get('en'), self.bot.langs.get('en'))

    def get_language_by_name(self, name):
        try:
            return Language(self.bot.langs.get(name), self.bot.langs.get('en'))
        except Exception as e:
            return Language(self.bot.langs.get(name), self.bot.langs.get('en'))

    def list_languages(self):
        return list(self.bot.langs.keys())

    def guild_lang(self, guild_id):
        try:
            lang = self.bot.settings_entry(guild_id).locale
            return lang
        except Exception as e:
            return 'en'

    @staticmethod
    def to_bool(s):
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
        else:
            return None

    @staticmethod
    def parse_redis(result: str = None):
        if not result:
            return None
        elif result.isnumeric():
            return int(result)
        elif result.lower() == 'true':
            return True
        elif result.lower() == 'false':
            return False
        else:
            return result

    @staticmethod
    def embed_to_codeblock(embed):
        msg = ''
        if embed.title != Embed.Empty:
            msg = msg + f'**{embed.title}**\n'
        if embed.description != Embed.Empty:
            msg = msg + f'{embed.description}\n\n'
        if embed.author != Embed.Empty:
            msg = msg + f'**User**\n{embed.author.name}\n\n'
        for field in embed.fields:
            msg = msg + f'**{field.name}**\n{field.value}\n\n'
        if embed.footer != Embed.Empty:
            msg = msg + f'{embed.footer.text}'
        msg = msg + '\nTip: Enable Embed Links for cleaner messages!'
        return msg

    @staticmethod
    def localized_channeltype(channel, lang):
        if isinstance(channel, TextChannel):
            if channel.is_news():
                return lang['logging']['channel']['news']
            else:
                return lang['logging']['channel']['text']
        elif isinstance(channel, VoiceChannel):
            return lang['logging']['channel']['vc']
        elif isinstance(channel, CategoryChannel):
            return lang['logging']['channel']['category']
        elif isinstance(channel, StoreChannel):
            return lang['logging']['channel']['store']
        else:
            return lang['logging']['channel']['other']


class PrefixHelper:
    @staticmethod
    async def return_prefix(bot, message):
        prefix = bot.settings_entry(message.guild.id).prefix
        return commands.when_mentioned_or(prefix)(bot, message)



