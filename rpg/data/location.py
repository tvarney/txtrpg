
from abc import abstractmethod
from rpg import event
from rpg.data import resource
from rpg.ui import options

import typing
if typing.TYPE_CHECKING:
    from rpg.app import Game
    from rpg.data.resource import ResourceID
    from typing import List, Optional

TravelInfo = typing.Tuple[resource.ResourceID, str, int]
NPCInfo = typing.Tuple[resource.ResourceID, str]


class Location(resource.Displayable):
    """Abstract base class of all Location objects.

    A location object represents the current part of the game world that the
    player is in. These are further divided down into actual Locations and
    'Features'. A feature is generally used for parts of the parent location
    which either take no time or very little time to travel to. Features can be
    things like shops, houses, alleyways, etc.

    There are further subclasses of Location which simplify the process of
    creating a Location by standardizing on how the data the location holds and
    how it displays it, though it is a perfectly valid method to provide
    subclasses of the base Location class.
    """

    def __init__(self, id_: 'ResourceID') -> None:
        """Initialize the Location instance.

        :param id_: The unique id string used to look this location up
        """
        _type = resource.ResourceType.Location
        resource.Displayable.__init__(self, _type, id_)

    @abstractmethod
    def text(self, game: 'Game') -> str:
        """Get the text to display for this Location.

        :param game: The Game instance displaying this Location
        :return: The text to display for this Location
        """
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'Game') -> 'options.OptionList':
        """Get the OptionList used to set the options for this Location.

        :param game: The Game instance displaying this Location
        :return: An OptionList instance denoting the options available at this
                 Location
        """
        raise NotImplementedError()


class BasicLocation(Location):
    """Specialization of the Location class to provide a standard interface to
    most locations.

    The BasicLocation class defines the concept of a Location providing links
    to other locations, a collection of 'features' or sub-locations of this
    location, and non-player characters.

    These methods are all marked abstract and left to the implementation to
    provide.
    """

    def __init__(self, name_id: 'ResourceID') -> None:
        """Initialize the BasicLocation instance.

        :param name_id: The unique id used to look this location up
        """
        Location.__init__(self, name_id)
        self._options = options.OptionList()
        self._options_locations = options.OptionList()
        self._options_features = options.OptionList()
        self._options_npcs = options.OptionList()

    @abstractmethod
    def text(self, game: 'Game'):
        """Get the text to display for this location.

        :param game: The Game instance displaying this location
        :return: The text to display for this location
        """
        raise NotImplementedError()

    def options(self, game: 'Game') -> 'options.OptionList':
        """Get the OptionList instance used to set the options for this
        location.

        This method uses the OptionList.generate_paged_list() method to create
        standard options for travel locations, feature locations, and NPCs
        present at the location. If the respective method returns None, then
        that button is not created.

        :param game: The Game instance displaying this location
        :return: An OptionList instance denoting options for this location
        """
        self._options.clear()
        _locations = self.locations(game)
        if _locations:
            if len(_locations) > 0:
                game.log.debug(
                    "BasicLocation::options(): Adding Travel button"
                )
                travel_options = list()
                for name, destination, td in _locations:
                    location_event = event.LocationEvent(destination, td)
                    travel_options.append((name, location_event))
                ol = options.OptionList.generate_paged_list(travel_options)
                self._options_locations = ol
                opt_travel = options.Option(
                    "Travel", event.UpdateOptionsEvent(self._options_locations)
                )
                self._options.set(opt_travel, 0, 0)
            else:
                game.log.debug(
                    "BasicLocation::options(): Travel options list is empty"
                )
        else:
            game.log.debug(
                "BasicLocation::options(): Travel options list is None"
            )

        _features = self.features(game)
        if _features:
            if len(_features) > 0:
                game.log.debug(
                    "BasicLocation::options(): Adding Features button"
                )
                feature_options = list()
                for name, destination, td in _features:
                    location_event = event.LocationEvent(destination, td)
                    feature_options.append((name, location_event))
                ol = options.OptionList.generate_paged_list(feature_options)
                self._options_features = ol
                opt_features = options.Option(
                    "Visit", event.UpdateOptionsEvent(self._options_features)
                )
                self._options.set(opt_features, 0, 1)
            else:
                game.log.debug(
                    "BasicLocation::options(): Feature options list is empty"
                )
        else:
            game.log.debug(
                "BasicLocation::options(): Feature options list is None"
            )

        return self._options

    @abstractmethod
    def locations(self, game: 'Game') -> 'Optional[List[TravelInfo]]':
        """Get a list of (name, resource_id, minutes) tuples which denote
        locations that may be traveled to.

        :param game: The game object
        :return: A list of possible locations to travel to from this location
        """
        raise NotImplementedError()

    @abstractmethod
    def features(self, game: 'Game') -> 'Optional[List[TravelInfo]]':
        """Get a list of (name, resource_id, minutes) tuples which denote
        features within this location.

        :param game: The game object
        :return: A list of possible sub-locations to visit at this location
        """
        raise NotImplementedError()

    @abstractmethod
    def npcs(self, game: 'Game') -> 'Optional[List[NPCInfo]]':
        """Get a list of (resource_id, name) tuples which denote NPCs at this
        location.

        :param game: The game object
        :return: A list of npcs at this location
        """
        raise NotImplementedError()


class BasicLocationImpl(BasicLocation):
    """A subclass of BasicLocationImpl which provides default methods for the
    BasicLocation API.
    """

    def __init__(self, name_id: str) -> None:
        """Initialize the BasicLocationImpl instance.

        :param name_id: The unique id of this BasicLocationImpl
        """
        BasicLocation.__init__(self, name_id)

    @abstractmethod
    def title(self, game: 'Game') -> str:
        raise NotImplementedError()

    @abstractmethod
    def text(self, game: 'Game') -> str:
        """Get the text to display for this location.

        :param game: The Game instance displaying this location
        :return: The text to display for this location
        """
        raise NotImplementedError()

    def locations(self, game: 'Game') -> 'Optional[List[TravelInfo]]':
        """Get the locations which may be traveled to from this location.

        If not overloaded by a subclass, this method just returns None. This
        allows locations which don't provide travel options to just ignore this
        method.

        :param game: The Game instance displaying this location
        :return: A list of locations which may be traveled to, or None
        """
        return None

    def features(self, game: 'Game') -> 'Optional[List[TravelInfo]]':
        """Get the feature locations which may be visited from this location.

        If not overloaded by a subclass, this method just returns None. This
        allows locations which don't provide features to visit to just ignore
        this method.

        :param game: The Game instance displaying this location
        :return: A list of locations which may be visited at this location
        """
        return None

    def npcs(self, game: 'Game') -> 'Optional[List[NPCInfo]]':
        """Get the npcs who are present at this location.

        If not overloaded by a subclass, this method just returns None. This
        allows locations which don't provide NPCs to just ignore this method.

        :param game: The game instance displaying this location
        :return: A list of NPCs which may be talked to at this location
        """
        return None
