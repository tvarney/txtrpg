
import inspect

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.ui import options
    from typing import Callable, List


class GameEvent(object):
    def apply(self, game: 'app.Game'):
        raise NotImplementedError()

    def action(self) -> str:
        return type(self).__name__

    def __str__(self):
        return self.action()


class CallbackEvent(GameEvent):
    def __init__(self, func: 'Callable[[app.Game], None]'):
        GameEvent.__init__(self)
        self._function = func

    def apply(self, game: 'app.Game'):
        self._function(game)


class CompoundEvent(GameEvent):
    def __init__(self, *events: 'List[GameEvent]'):
        GameEvent.__init__(self)
        self._events = list()  # type: List[GameEvent]
        for item in events:
            if inspect.isclass(item):
                raise Exception("Class instance '{}' passed to CompoundEvent".format(item))
            self._events.append(item)

    def apply(self, game: 'app.Game'):
        for item in self._events:
            item.apply(game)


class OptionListReturnEvent(GameEvent):
    def apply(self, game: 'app.Game'):
        pass


class UpdateOptionsEvent(GameEvent):
    def __init__(self, option_list: 'options.OptionList'):
        self._option_list = option_list

    def apply(self, game: 'app.Game'):
        pass


class LocationEvent(GameEvent):
    def __init__(self, location_id: str, time_delta: int=0):
        GameEvent.__init__(self)
        self._location_id = location_id
        self._time_delta = time_delta

    def apply(self, game: 'app.Game'):
        game.log.debug("LocationEvent({}, {})", self._location_id, self._time_delta)
