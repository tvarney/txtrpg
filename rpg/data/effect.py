
import abc

import typing
if typing.TYPE_CHECKING:
    from typing import List
    from rpg.data.actor import Actor


class Effect(abc.ABC):
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def apply(self, source: 'Actor', target: 'Actor') -> None:
        raise NotImplementedError()


class CompoundEffect(Effect):
    def __init__(self, effects: 'List[Effect]') -> None:
        Effect.__init__(self)
        self._effects = effects

    def apply(self, source: 'Actor', target: 'Actor') -> None:
        for effect in self._effects:
            effect.apply(source, target)


class Heal(Effect):
    def __init__(self, amount: int) -> None:
        Effect.__init__(self)
        self._amount = amount

    def apply(self, source: 'Actor', target: 'Actor') -> None:
        pass

