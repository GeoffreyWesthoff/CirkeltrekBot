from collections import UserDict


class Language(UserDict):
    def __init__(self, strings, english):
        super(Language, self).__init__()
        self.strings = strings
        self.english = english

    def __getitem__(self, item):
        try:
            value = self.strings[item]
            if isinstance(value, dict):
                value = Language(value, self.english.get(item))
            return value
        except (KeyError, TypeError):
            return self.english[item]
