
from rpg.data import attributes

import typing
if typing.TYPE_CHECKING:
    from typing import Optional


class Actor(object):
    def __init__(self, name: str, race: None=None, stats: 'Optional[attributes.AttributeList]'=None):
        self._name = name
        self._race = race
        self.stats = stats if stats is not None else attributes.AttributeList()

    def name(self, new_name: 'Optional[str]'=None) -> str:
        if new_name is not None:
            self._name = new_name
        return self._name

    def race(self) -> None:
        return self._race


class Player(Actor):
    def __init__(self):
        Actor.__init__(self, "", None, None)
        self.attribute_points = 0  # type: int
        self.inventory = None

    def calculate_secondaries(self):
        current_health = self.stats.health.level()
        new_health = self.stats.constitution.level() * 3 + self.stats.strength.level() * 7
        self.stats.health.level_up(new_health - current_health)

        current_stamina = self.stats.stamina.level()
        new_stamina = self.stats.constitution.level() * 7 + self.stats.agility.level() * 3
        self.stats.stamina.level_up(new_stamina - current_stamina)

        current_mana = self.stats.mana.level()
        new_mana = self.stats.intelligence.level() * 7 + self.stats.wisdom.level() * 3
        self.stats.mana.level_up(new_mana - current_mana)


class NonPlayerCharacter(Actor):
    def __init__(self, name: str, race: None=None, stats: 'Optional[attributes.AttributeList]'=None):
        Actor.__init__(self, name, race, stats)

    def get_dialog(self, game):
        raise NotImplementedError()


class Monster(NonPlayerCharacter):
    def __init__(self, name: str, race: None=None, stats: 'Optional[attributes.AttributeList]'=None):
        NonPlayerCharacter.__init__(self, name, race, stats)

    def fight(self):
        pass
