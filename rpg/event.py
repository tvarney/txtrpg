"""Definitions of GameEvents.

The various GameEvent instances which are provided by default are defined in
this module. A GameEvent is simply an object which holds a callback of some
form. A generic 'lambda' callback event is provided as CallbackEvent, though it
is preferable to define a subclass of GameEvent and overload the
GameEvent.apply() method.
"""

from abc import ABCMeta, abstractmethod
import inspect

import typing
if typing.TYPE_CHECKING:
    from rpg.app import Game
    from rpg.ui import options, views
    from typing import Callable, List


class GameEvent(object, metaclass=ABCMeta):
    @abstractmethod
    def apply(self, game: 'Game') -> None:
        """Apply the GameEvent to the Game instance.

        :param game: The Game instance to apply this GameEvent to
        """
        raise NotImplementedError()

    def action(self) -> str:
        """Get a string which represents this GameEvent.

        This method is intended more for debugging than for general use.

        :return: A string which represents the action this GameEvent takes
        """
        return type(self).__name__

    def __str__(self):
        return self.action()


class CallbackEvent(GameEvent):
    """A lambda style callback event.

    This class is intended for one-off events which can be defined with a
    lambda function. The lambda function should take only 1 argument (the Game
    instance) and not return anything.

    If the event can be generally used, it is better to provide it as a library
    extension.
    """

    def __init__(self, func: 'Callable[[Game], None]') -> None:
        """Initialize this callback event with the given callback.

        :param func: The callback function which is called when the event is
                     applied
        """
        GameEvent.__init__(self)
        self._function = func

    def apply(self, game: 'Game') -> None:
        """Apply the callback function to the given Game instance.

        :param game: The Game instance
        """
        self._function(game)


class CompoundEvent(GameEvent):
    """An event which is composed of various other events.

    This event is used for when a sequence of events is desired. For instance,
    a dialog may want to add an item to the character, change the location,
    then start a fight. Doing so would with this class would be as simple as
    providing the following compound event:

        CompoundEvent(InventoryEvent('item.bronze_dagger', 1),
                      LocationEvent('prologue.meadow', 0),
                      FightEvent('monster.goblin'))
    """

    def __init__(self, *events: 'GameEvent') -> None:
        """Initialize the CompoundEvent with the given list of events

        :param events: The events to apply
        """
        GameEvent.__init__(self)
        self._events = list()  # type: List[GameEvent]
        for item in events:
            if inspect.isclass(item):
                raise Exception(
                    "Class instance '{}' passed to CompoundEvent".format(item)
                )
            self._events.append(item)

    def apply(self, game: 'Game') -> None:
        """Apply the events in the order that they were given.

        :param game: The Game instance to apply each event to
        """
        for item in self._events:
            item.apply(game)


class OptionListReturnEvent(GameEvent):
    """A GameEvent which forces the current displayable to redisplay itself.

    This GameEvent is used to force the GameView to redisplay the current
    displayable resource. This is useful for when the options or text has been
    changed by another event but the current displayable hasn't been been
    changed nor has the game state been updated.
    """

    def apply(self, game: 'Game') -> None:
        """Resume the current displayable.

        :param game: The Game instance
        """
        game.state.resume_display()


class UpdateOptionsEvent(GameEvent):
    """GameEvent which changes the displayed OptionList.

    This GameEvent is used to change the OptionList displayed by the GameView
    without changing the location or dialog instance. This allows paged lists
    and sub lists of options to be implemented.
    """

    def __init__(self, option_list: 'options.OptionList') -> None:
        """Initialize this event with the given OptionList instance

        :param option_list: The options.OptionList instance to switch to on
                            application of the event
        """
        self._option_list = option_list

    def apply(self, game: 'Game') -> None:
        """Change the OptionList being displayed.

        :param game: The Game instance to apply this event to
        """
        view = game.stack.current()
        if view is None or not view.is_game_view():
            return

        # Coerce the type to make mypy/PyCharm happy
        typing.cast(views.GameView, view).set_options(self._option_list)


class LocationEvent(GameEvent):
    """GameEvent which changes the current location."""

    def __init__(self, location_id: str, time_delta: int = 0) -> None:
        """Initialize the LocationEvent instance.

        :param location_id: The unique string used to identify the location to
                            change to
        :param time_delta: How many minutes the location change should take
        """
        GameEvent.__init__(self)
        self._location_id = location_id
        self._time_delta = time_delta

    def apply(self, game: 'Game') -> None:
        """Change the current location of the game.

        :param game: The Game instance to apply to
        """
        game.state.set_location(self._location_id)


class FightEndEvent(GameEvent):
    def apply(self, game: 'Game') -> None:
        game.state.stop_fight()


class FightStartEvent(GameEvent):
    def __init__(self, monster: str) -> None:
        GameEvent.__init__(self)
        self._monster = monster

    def apply(self, game: 'Game') -> None:
        game.state.set_fight(self._monster)
