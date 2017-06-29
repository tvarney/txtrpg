
from enum import IntEnum, unique

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import Optional


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
