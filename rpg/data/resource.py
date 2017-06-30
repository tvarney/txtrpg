
from enum import IntEnum, unique
from rpg.ui import options

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import List, Optional, Tuple


@unique
class ResourceType(IntEnum):
    Location = 0
    Dialog = 1
    Item = 2
    Monster = 3
    COUNT = 4


class Resource(object):
    def __init__(self, type_id: ResourceType, resource_id: str):
        self._type_id = type_id  # type: ResourceType
        self._resource_id = resource_id  # type: str
        self._package = None  # type: Optional[str]

    def type_id(self) -> ResourceType:
        """
        Get the ResourceType type_id of this Resource instance
        :return: The type_id of this Resource
        """
        return self._type_id

    def resource_id(self) -> str:
        """
        Get the resource_id string of this resource
        :return: The resource_id string of this Resource instance
        """
        return self._resource_id

    def package(self) -> 'Optional[str]':
        return self._package


class Displayable(Resource):
    def __init__(self, type_id: ResourceType, resource_id: str):
        Resource.__init__(self, type_id, resource_id)

    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    def options(self, game: 'app.Game'):
        raise NotImplementedError()

    def start(self, game: 'app.Game'):
        pass

    def resume(self, game: 'app.Game'):
        self.start(game)


class Location(Displayable):
    def __init__(self, resource_id: str):
        Displayable.__init__(self, ResourceType.Location, resource_id)

    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    def options(self, game: 'app.Game'):
        raise NotImplementedError()


class Dialog(Displayable):
    def __init__(self, resource_id: str):
        Displayable.__init__(self, ResourceType.Dialog, resource_id)

    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    def options(self, game: 'app.Game'):
        raise NotImplementedError()


class BasicLocation(Location):
    def __init__(self, name_id: str):
        Location.__init__(self, name_id)
        self._options = options.OptionList()
        self._options_locations = options.OptionList()
        self._options_features = options.OptionList()
        self._options_npcs = options.OptionList()

    def get_text(self, game: 'app.Game'):
        raise NotImplementedError()

    def get_options(self, game: 'app.Game'):
        self._options.clear()
        locations = self.get_locations(game)

    def get_locations(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        """
        Get a list of (name, resource_id, minutes) tuples which denote locations that may be traveled to
        :param game: The game object
        :return:
        """
        return None

    def get_features(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        return None

    def get_npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str]]]':
        return None

