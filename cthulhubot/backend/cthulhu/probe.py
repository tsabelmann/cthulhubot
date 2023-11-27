"""
"""

from disnake import Localized, LocalizationProtocol, Locale
from cthulhubot.backend.utils.localization import AdvancedLocalized

import re
import enum
import random
import typing
from typing import Union


__probe_regex__ = re.compile(
    r'\s*(?P<probe>[0-9]{1,3})'
    r'(\s*(?P<id>[mM]|[bB]|[bB][oO][nN][uU][sS]|[mM][aA][lL][uU][sS])\s*(?P<value>[0-9]{1,2}))?'
    r'\s*'
)


def dice2value(die_10: int, die_1: int):
    if die_10 == 0 and die_1 == 0:
        return 100
    else:
        return (die_10 * 10) + die_1


def value2dice(value: int):
    if value == 100:
        return 0, 0
    else:
        die_10 = value // 10
        die_1 = value % 10
        return die_10, die_1


def probe_success(die: int, ability: int):
    if die == 1:
        return ProbeSuccess.CRITICAL_SUCCESS
    elif die <= (ability // 5):
        return ProbeSuccess.EXTREME_SUCCESS
    elif die <= (ability // 2):
        return ProbeSuccess.DIFFICULT_SUCCESS
    elif die <= ability:
        return ProbeSuccess.REGULAR_SUCCESS
    else:
        if ability < 50:
            if die >= 96:
                return ProbeSuccess.DOOM
            else:
                return ProbeSuccess.FAILURE
        else:
            if die == 100:
                return ProbeSuccess.DOOM
            else:
                return ProbeSuccess.FAILURE


class ProbeSuccess(enum.Enum):
    CRITICAL_SUCCESS = 0,
    EXTREME_SUCCESS = 1,
    DIFFICULT_SUCCESS = 2,
    REGULAR_SUCCESS = 3
    FAILURE = 4,
    DOOM = 5


class Probe:
    def __init__(self, ability: int = 0, bonus: int = 0, malus: int = 0):
        if ability < 0:
            raise ValueError

        if bonus > 0 and malus > 0:
            raise ValueError

        self._ability = ability
        self._bonus = bonus
        self._malus = malus

    @property
    def ability(self):
        return self._ability

    @property
    def bonus(self):
        return self._bonus

    @property
    def malus(self):
        return self._malus

    @classmethod
    def from_str(cls, value: str):
        match = __probe_regex__.search(value)
        if match:
            # Compute transmitted probe (ability) value
            ability = match.group("probe")
            ability = int(ability)

            # Bonus / Malus computation
            if match.group("id") and match.group("id").lower() in ["b", "B", "bon", "bonu", "bonus"]:
                # Get amount of bonus dice
                bonus = match.group("value")
                bonus = int(bonus)

                return cls(ability, bonus=bonus)
            elif match.group("id") and match.group("id").lower() in ["m", "M", "mal", "malu", "malus"]:
                # Get amount of bonus dice
                malus = match.group("value")
                malus = int(malus)

                return cls(ability, malus=malus)
            else:
                return cls(ability)
        else:
            raise ValueError

    def probe(self) -> "ProbeResult":
        die_10 = random.randint(0, 9)
        die_1 = random.randint(0, 9)

        if self.bonus > 0 and self.malus == 0:
            return ProbeResult(self.ability, die_10, die_1,
                               bonus_dice_10=[random.randint(0, 9) for _ in range(self.bonus)])
        elif self.bonus == 0 and self.malus > 0:
            return ProbeResult(self.ability, die_10, die_1,
                               malus_dice_10=[random.randint(0, 9) for _ in range(self.malus)])
        else:
            return ProbeResult(self.ability, die_10, die_1)


class ProbeResult:
    def __init__(self, ability: int, die_10: int, die_1: int,
                 bonus_dice_10: typing.Union[typing.List[int], None] = None,
                 malus_dice_10: typing.Union[typing.List[int], None] = None
                 ):

        if ability < 0:
            raise ValueError

        if die_10 < 0 or die_10 > 9:
            raise ValueError

        if die_1 < 0 or die_10 > 9:
            raise ValueError

        if (bonus_dice_10 is not None) and (malus_dice_10 is not None):
            raise ValueError

        self._ability = ability
        self._die_10 = die_10
        self._die_1 = die_1
        self._bonus_dice_10 = [] if bonus_dice_10 is None else bonus_dice_10
        self._malus_dice_10 = [] if malus_dice_10 is None else malus_dice_10

    @property
    def ability(self):
        return self._ability

    @property
    def die_10(self) -> int:
        return self._die_10

    @property
    def bonus_dice_10(self):
        return self._bonus_dice_10

    @property
    def malus_dice_10(self):
        return self._malus_dice_10

    @property
    def die_1(self) -> int:
        return self._die_1

    def value(self) -> int:
        if self.bonus_dice_10 != [] and self.malus_dice_10 == []:
            return min([dice2value(die_10, self.die_1) for die_10 in [self.die_10, *self.bonus_dice_10]])
        elif self.bonus_dice_10 == [] and self.malus_dice_10 != []:
            return max([dice2value(die_10, self.die_1) for die_10 in [self.die_10, *self.malus_dice_10]])
        else:
            return dice2value(self.die_10, self.die_1)

    def success(self) -> ProbeSuccess:
        return probe_success(self.value(), self.ability)
    
    def is_success(self) -> bool:
        return (self.value() <= self.ability)

    def render(self, 
               username: str, 
               description: str = "", 
               prot: Union[LocalizationProtocol, None] = None,
               locale: Union[Locale, None] = None
               ) -> str:
        success = self.success()
        
        # Add username and optionally description
        if description != None and description != "":
            result = f"**{username}** ({description})\n"
        else:
            result = f"**{username}**\n"

        ability_str = AdvancedLocalized("Ability", key="PROBE_RESULT_ABILITY", prot=prot, locale=locale)
        roll_str = AdvancedLocalized("Roll", key="PROBE_RESULT_ROLL", prot=prot, locale=locale)
        bonus_str = AdvancedLocalized("Bonus", key="PROBE_RESULT_BONUS", prot=prot, locale=locale)
        malus_str = AdvancedLocalized("Malus", key="PROBE_RESULT_MALUS", prot=prot, locale=locale)
        result_str = AdvancedLocalized("Result", key="PROBE_RESULT_RESULT", prot=prot, locale=locale)
    
        if self.bonus_dice_10 != [] and self.malus_dice_10 == []:
            # Check if the bonus had an effect
            if self.value() < dice2value(self.die_10, self.die_1):
                result += f"{roll_str}: [{self.die_10 * 10:02d}][**{self.die_1}**] {ability_str}: **{self.ability}**\n"

                # Compute index in dice that holds the die_10 value
                index = [dice2value(die_10, self.die_1) for die_10 in self.bonus_dice_10].index(self.value())

                # Compute new dice string
                lst = [f"**{die * 10:02d}**" if i == index else f"{die * 10:02d}" for i, die in
                       enumerate(self.bonus_dice_10)]
                dice_str = f"[{', '.join(lst)}]"
                result += f"{bonus_str}: {dice_str}\n"
            else:
                result += f"{roll_str}: [**{self.die_10 * 10:02d}**][**{self.die_1}**] {ability_str}: **{self.ability}**\n"

                lst = [f"{die * 10:02d}" for die in self.bonus_dice_10]
                dice_str = f"[{', '.join(lst)}]"
                result += f"{bonus_str}: {dice_str}\n"
        elif self.bonus_dice_10 == [] and self.malus_dice_10 != []:
            # Check if the malus had an effect
            if self.value() > dice2value(self.die_10, self.die_1):
                result += f"{roll_str}: [{self.die_10 * 10:02d}][**{self.die_1}**] {ability_str}: **{self.ability}**\n"

                # Compute index in dice that holds the die_10 value
                index = [dice2value(die_10, self.die_1) for die_10 in self.malus_dice_10].index(self.value())

                # Compute new dice string
                lst = [f"**{die * 10:02d}**" if i == index else f"{die * 10:02d}" for i, die in
                       enumerate(self.malus_dice_10)]
                dice_str = f"[{', '.join(lst)}]"
                result += f"{malus_str}: {dice_str}\n"
            else:
                result += f"{roll_str}: [**{self.die_10 * 10:02d}**][**{self.die_1}**] {ability_str}: **{self.ability}**\n"

                lst = [f"{die * 10:02d}" for die in self.malus_dice_10]
                dice_str = f"[{', '.join(lst)}]"
                result += f"{malus_str}: {dice_str}\n"
        else:
            result += f"{roll_str}: [**{self.die_10 * 10:02d}**][**{self.die_1}**] {ability_str}: **{self.ability}**\n"

        # Compute result
        result += f"{result_str}: **{self.value()}**\n"

        # Compute success level
        if success == ProbeSuccess.CRITICAL_SUCCESS:
            critical = AdvancedLocalized("Critical success", key="CRITICAL_SUCCESS", prot=prot, locale=locale)
            result += f"**{critical}**\n"
            # result += f"**{Localized('Critical success', key='CRITICAL_SUCCESS').string}**\n"
        elif success == ProbeSuccess.EXTREME_SUCCESS:
            extreme = AdvancedLocalized("Extreme success", key="EXTREME_SUCCESS", prot=prot, locale=locale)
            result += f"**{extreme}**\n"
            # result += f"**{Localized('Extreme success', key='EXTREME_SUCCESS').string}**\n"
        elif success == ProbeSuccess.DIFFICULT_SUCCESS:
            difficult = AdvancedLocalized("Difficult success", key="DIFFICULT_SUCCESS", prot=prot, locale=locale)
            result += f"**{difficult}**\n"
            # result += f"**{Localized('Difficult success', key='DIFFICULT_SUCCESS').string}**\n"
        elif success == ProbeSuccess.REGULAR_SUCCESS:
            regular = AdvancedLocalized("Regular success", key="REGULAR_SUCCESS", prot=prot, locale=locale)
            result += f"**{regular}**\n"
            # result += f"**{Localized('Regular success', key='REGULAR_SUCCESS').string}**\n"
        elif success == ProbeSuccess.FAILURE:
            failure = AdvancedLocalized("You have screwed up!", key="FAILURE", prot=prot, locale=locale)
            result += f"**{failure}**\n"
            # result += f"**{Localized('You have screwed up!', key='FAILURE').string}**\n"
        else:
            doom = AdvancedLocalized("You are doomed!", key="DOOM", prot=prot, locale=locale)
            result += f"**{doom}**\n"
            # result += f"**{Localized('You are doomed!', key='DOOM').string}**\n"

        return result
