from discord.utils import get


class Roles:
    def __init__(self, roles, channels, settings):
        self.admin = get(roles, id=settings.admin)
        self.guild = self.admin.guild
        self.stadthouder = get(roles, id=settings.stadthouder)
        self.ridder = get(roles, id=settings.ridder)
        self.burgerij = get(roles, id=settings.burgerij)
        self.spanjool = get(roles, id=settings.spanjool)
        self.alva = get(roles, id=settings.alva)
        self.kop_dicht = get(roles, id=settings.kop_dicht)
        self.straffen = get(channels, id=settings.straffen)
        self.babbelaar = get(roles, id=settings.babbelaar)
        self.lekker_trekken = get(channels, id=settings.lekker_trekken)
        self.geheime_ruimte = get(channels, id=settings.geheime_ruimte)
