class SettingsEntry:
    def __init__(self, bot, guild_id, entry):
        self.ready = False
        self.guild_id = guild_id
        self.mongo = bot.mongo
        default = bot.default_settings
        for key in default.keys():
            setattr(self, key, entry.get(key, default[key]))
        self.ready = True

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if self.ready and key not in ['ready', 'guild_id', 'mongo']:
            self.mongo.guilds.update_one({"_id": self.guild_id}, {"$set": {f'settings.{key}': value}}, upsert=True)
