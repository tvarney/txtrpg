
from enum import IntEnum, unique
from rpg.data import actor, resource, resources

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.ui import views
    from typing import Any, Dict, Optional


@unique
class GameState(IntEnum):
    Stopped = 0
    Location = 1
    Dialog = 2
    Fight = 3


class GameData(object):
    def __init__(self, game_object: 'app.Game'):
        self._game_object = game_object  # type: app.Game
        self._state = GameState.Stopped  # type: GameState
        self._add_loc_text = False  # type: bool

        self.player = actor.Player()  # type: actor.Player
        self.location = None  # type: Optional[resource.Location]
        self.fight = None  # type: None
        self.dialog = None  # type: Optional[resource.Dialog]
        self.time = None  # type: None
        self.resources = resources.Resources()
        self.variables = dict()  # type: Dict[str, Any]
        self.temp = dict()  # type: Dict[str, Any]

    def set_location(self, location_id: str):
        """
        Attempt to change the current location to the location denoted by the given resource_id
        :param location_id: The resource_id of the new location
        """
        instance = self.resources.get(resource.ResourceType.Location, location_id)
        if instance is None:
            self._game_object.log.error("Could not find location {}", location_id)
            return
        self._state = GameState.Location
        self.location = instance  # type: resource.Location
        self._add_loc_text = True
        self.location.start(self._game_object)
        # Only display if the current state is GameState.Location and our instance is the correct instance
        if self._state == GameState.Location and instance == self._state:
            self._display(self.location)

    def set_dialog(self, dialog_id: str):
        """
        Attempt to set the current dialog to the one denoted by the given resource id
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

    def game_view(self) -> 'Optional[views.GameView]':
        """
        Get the GameView instance, assuming it is the current view
        :return: The current view as a GameView, assuming it implements the GameView interface
        """
        view = self._game_object.stack.current()  # type: views.GameView
        return view if view.is_game_view() else None

    def _display(self, displayable: 'resource.Displayable'):
        """
        Display the given Displayable resource if the current View is the GameView
        :param displayable: The displayable to display
        """
        # Technically, this annotation can be wrong; when it is though, we don't do anything
        view = self._game_object.stack.current()  # type: views.GameView
        if view.is_game_view():
            view.set_text(displayable.text(self._game_object))
            view.set_options(displayable.options(self._game_object))
