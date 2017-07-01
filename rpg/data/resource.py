
from abc import ABCMeta, abstractmethod
from enum import IntEnum, unique
from rpg import event
from rpg.ui import options as _options

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
    Callback = 4
    COUNT = 5


class Resource(metaclass=ABCMeta):
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


class Callback(Resource):
    def __init__(self, resource_id: str):
        Resource.__init__(self, ResourceType.Callback, resource_id)

    @abstractmethod
    def apply(self, game: 'app.Game'):
        raise NotImplementedError()


class Displayable(Resource):
    def __init__(self, type_id: ResourceType, resource_id: str):
        Resource.__init__(self, type_id, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> '_options.OptionList':
        raise NotImplementedError()

    def start(self, game: 'app.Game'):
        pass

    def resume(self, game: 'app.Game'):
        self.start(game)


class Location(Displayable):
    def __init__(self, resource_id: str):
        Displayable.__init__(self, ResourceType.Location, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> '_options.OptionList':
        raise NotImplementedError()


class Dialog(Displayable):
    def __init__(self, resource_id: str):
        Displayable.__init__(self, ResourceType.Dialog, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> '_options.OptionList':
        raise NotImplementedError()


class BasicLocation(Location):
    def __init__(self, name_id: str):
        Location.__init__(self, name_id)
        self._options = _options.OptionList()
        self._options_locations = _options.OptionList()
        self._options_features = _options.OptionList()
        self._options_npcs = _options.OptionList()

    @abstractmethod
    def text(self, game: 'app.Game'):
        raise NotImplementedError()

    def options(self, game: 'app.Game') -> '_options.OptionList':
        self._options.clear()
        _locations = self.locations(game)
        if _locations:
            if len(_locations) > 0:
                game.log.debug("BasicLocation::options(): Adding Travel button")
                travel_options = list((name, event.LocationEvent(dest, td)) for name, dest, td in _locations)
                self._options_locations = _options.OptionList.generate_paged_list(travel_options)
                opt_travel = _options.Option("Travel", event.UpdateOptionsEvent(self._options_locations))
                self._options.set(opt_travel, 0, 0)
            else:
                game.log.debug("BasicLocation::options(): Travel options list is empty")
        else:
            game.log.debug("BasicLocation::options(): Travel options list is None")

        _features = self.features(game)
        if _features:
            if len(_features) > 0:
                game.log.debug("BasicLocation::options(): Adding Features button")
                feature_options = list((name, event.LocationEvent(dest, td)) for name, dest, td in _features)
                self._options_features = _options.OptionList.generate_paged_list(feature_options)
                opt_features = _options.Option("Visit", event.UpdateOptionsEvent(self._options_features))
                self._options.set(opt_features, 0, 1)
            else:
                game.log.debug("BasicLocation::options(): Feature options list is empty")
        else:
            game.log.debug("BasicLocation::options(): Feature options list is None")

        return self._options

    @abstractmethod
    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        """
        Get a list of (name, resource_id, minutes) tuples which denote locations that may be traveled to
        :param game: The game object
        :return: A list of possible locations to travel to from this location
        """
        raise NotImplementedError()

    @abstractmethod
    def features(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        """
        Get a list of (name, resource_id, minutes) tuples which denote features within this location
        :param game: The game object
        :return: A list of possible sub-locations to visit at this location
        """
        raise NotImplementedError()

    @abstractmethod
    def npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str]]]':
        """
        Get a list of (name, resource_id) tuples which denote npcs at this location
        :param game: The game object
        :return: A list of npcs at this location
        """
        raise NotImplementedError()


class BasicLocationImpl(BasicLocation):
    def __init__(self, name_id: str):
        BasicLocation.__init__(self, name_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        return None

    def features(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        return None

    def npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str]]]':
        return None
