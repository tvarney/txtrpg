
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
        self._inventory = None


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
