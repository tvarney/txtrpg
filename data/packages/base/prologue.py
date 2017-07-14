
from rpg import event
from rpg.data import actor, location, resource
from rpg.ui import options as _options

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import List, Optional, Tuple


class CallbackStart(resource.Callback):
    def __init__(self):
        resource.Callback.__init__(self, "base.start_game")

    def apply(self, game: 'app.Game'):
        # Add starting equipment
        game.log.debug("base::prologue::CallbackStart(): Setting location to 'prologue.players_house'")
        game.state.set_location("prologue.players_house")


class PlayersHouse(location.Location):
    def __init__(self):
        location.Location.__init__(self, "prologue.players_house")

    def title(self, game: 'app.Game') -> str:
        return "Your House"

    def text(self, game: 'app.Game') -> str:
        return "This is your house"

    def options(self, game: 'app.Game'):
        return _options.OptionList((_options.Option("Leave", event.LocationEvent("prologue.town_square", 0)), 0, 0))

    def start(self, game: 'app.Game'):
        pass


class TownSquare(location.BasicLocationImpl):
    def __init__(self):
        location.BasicLocation.__init__(self, "prologue.town_square")

    def title(self, game: 'app.Game') -> str:
        return "Town Square"

    def text(self, game: 'app.Game') -> str:
        return "This is the Town Square"

    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        return [("Market", "prologue.market", 0)]


class Market(location.BasicLocationImpl):
    def __init__(self):
        location.BasicLocation.__init__(self, "prologue.market")

    def title(self, game: 'app.Game') -> str:
        return "Market"

    def text(self, game: 'app.Game') -> str:
        return "This is the Market"

    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        return [("Town Square", "prologue.town_square", 0)]
