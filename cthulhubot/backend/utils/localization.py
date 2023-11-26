from disnake import Locale, LocalizationProtocol

class AdvancedLocalized:
    def __init__(self, string: str, key: str, prot: LocalizationProtocol, locale: Locale) -> None:
        if (string == None) or (string == "") or (key == None) or (key == ""):
            raise ValueError()


        self.string = string
        self.key = key
        self.prot = prot
        self.locale = locale
        
    def __str__(self) -> str:
        if (self.key != None) and (self.prot != None) and (self.locale != None):
            locs = self.prot.get(self.key)
            if locs != None:
                return locs.get(str(self.locale), self.string)
            else:
                return self.string
        else:
            return self.string
