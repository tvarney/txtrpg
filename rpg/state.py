
"""Classes used for tracking game state.

The game state is defined as all the data which is being used by the game itself. This excludes things like the
package listing, the logging class, and various other bits defined in the rpg.app.Game class.

"""

from enum import IntEnum, unique
from rpg.data import actor, location, resource, resources

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.ui import views
    from typing import Any, Dict, Optional, Tuple


@unique
class GameState(IntEnum):

    """Enumeration which tracks the current state of the GameData class.

    """

    Stopped = 0
    Location = 1
    Dialog = 2
    Fight = 3


class GameData(object):

    """Collection of data which can be thought of as the games state.

    The GameData class can be thought of as the game state for a particular instance of the game. This is the object
    which can be loaded and saved to files more or less completely to implement a save game feature.

    """

    def __init__(self, game_object: 'app.Game') -> None:
        """Initialize the GameData instance

        :param game_object: The app.Game instance holding this GameData instance
        """
        self._game_object = game_object  # type: app.Game
        self._state = GameState.Stopped  # type: GameState
        self._add_loc_text = False  # type: bool

        self.player = actor.Player()  # type: actor.Player
        self.monster = None  # type: Optional[actor.NonPlayerCharacter]
        self.location = None  # type: Optional[location.Location]
        self.fight = None  # type: None
        self.dialog = None  # type: Optional[resource.Dialog]
        self.time = None  # type: None
        self.resources = resources.Resources()
        self.variables = dict()  # type: Dict[str, Any]
        self.temp = dict()  # type: Dict[str, Any]

    def start(self) -> None:
        """Set the current location, fight, and dialog to None and then apply all callbacks."""
        self.location = None
        self.fight = None
        self.dialog = None

        r_type = resource.ResourceType.Callback
        for _, _, callback in self.resources.enumerate(r_type):  # type: Tuple[resource.Callback]
            callback.apply(self._game_object)

        if self.location is None:
            self._game_object.log.error("No initial location set by start callbacks")

    def set_location(self, location_id: str) -> None:
        """Attempt to change the current location to the location denoted by the given resource_id.

        :param location_id: The resource_id of the new location
        """
        instance = self.resources.get(resource.ResourceType.Location, location_id)  # type: location.Location
        if instance is None:
            self._game_object.log.error("Could not find location {}", location_id)
            return
        self._state = GameState.Location
        self.location = instance  # type: location.Location
        self._add_loc_text = True
        self.location.start(self._game_object)
        # Only display if the current state is GameState.Location and our instance is the correct instance
        if self._state == GameState.Location and instance is self.location:
            if self.location is not None:
                self._display(self.location)

    def set_dialog(self, dialog_id: str) -> None:
        """Attempt to set the current dialog to the one denoted by the given resource id.

        :param dialog_id: The resource id of the dialog to switch to
        """
        instance = self.resources.get(resource.ResourceType.Dialog, dialog_id)
        if instance is None:
            self._game_object.log.error("Could not find dialog {}", dialog_id)
            return
        else:
            self._state = GameState.Dialog
            self.dialog = instance  # type: resource.Dialog
            self._display(self.dialog)

    def set_fight(self, monster_id: str) -> None:
        self._state = GameState.Fight
        self.monster = self.resources.get(resource.ResourceType.Actor, monster_id)
        view = self._game_object.stack.current()  # type: views.GameView
        if view.is_game_view():
            view.fight_start(self.monster)

    def stop_fight(self) -> None:
        self._state = GameState.Location
        view = self._game_object.stack.current()  # type: views.GameView
        if view.is_game_view():
            view.fight_end()
        
        self.resume_display()

    def game_view(self) -> 'Optional[views.GameView]':
        """Get the GameView instance, assuming it is the current view.

        :return: The current view as a GameView, assuming it implements the GameView interface
        """
        view = self._game_object.stack.current()  # type: views.GameView
        return view if view.is_game_view() else None

    def state(self) -> GameState:
        """Get the GameState value representing the current state of the game.

        :return: The current state of the game
        """
        return self._state

    def resume_display(self) -> None:
        """Force the current displayable to be redisplayed.

        Which displayable is displayed is dependent on the current state of the game.
        """
        if self._state == GameState.Location:
            self._display(self.location)
        elif self._state == GameState.Dialog:
            self._display(self.dialog)
        else:
            self._game_object.log.error("GameData::resume_display(): Can not resume display for state {}",
                                        self._state.name)

    def _display(self, displayable: 'resource.Displayable'):
        """Display the given Displayable resource if the current View is the GameView.

        :param displayable: The displayable to display
        """
        # Technically, this annotation can be wrong; when it is though, we don't do anything
        view = self._game_object.stack.current()  # type: views.GameView
        if view.is_game_view():
            view.display(displayable)
