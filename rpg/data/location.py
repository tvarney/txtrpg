
from abc import abstractmethod
from rpg import event
from rpg.data import resource
from rpg.ui import options

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data.resource import ResourceID
    from typing import List, Optional, Tuple


class Location(resource.Displayable):

    """Abstract base class of all Location objects.

    A location object represents the current part of the game world that the player is in. These are further divided
    down into actual Locations and 'Features'. A feature is generally used for parts of the parent location which either
    take no time or very little time to travel to. Features can be things like shops, houses, alleyways, etc.

    There are further subclasses of Location which simplify the process of creating a Location by standardizing on how
    the data the location holds and how it displays it, though it is a perfectly valid method to provide subclasses of
    the base Location class.

    """

    def __init__(self, resource_id: 'ResourceID') -> None:
        """Initialize the Location instance.

        :param resource_id: The unique id string used to look this location up
        """
        resource.Displayable.__init__(self, resource.ResourceType.Location, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        """Get the text to display for this Location.

        :param game: The app.Game instance displaying this Location
        :return: The text to display for this Location
        """
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> 'options.OptionList':
        """Get the OptionList used to set the options for this Location.

        :param game: The app.Game instance displaying this Location
        :return: An OptionList instance denoting the options available at this Location
        """
        raise NotImplementedError()


class BasicLocation(Location):

    """Specialization of the Location class to provide a standard interface to most locations.

    The BasicLocation class defines the concept of a Location providing links to other locations, a collection of
    'features' or sub-locations of this location, and non-player characters.

    These methods are all marked abstract and left to the implementation to provide.

    """

    def __init__(self, name_id: 'ResourceID') -> None:
        """Initialize the BasicLocation instance.

        :param name_id: The unique id used to look this location up
        """
        Location.__init__(self, name_id)
        self._options = options.OptionList()  # type: options.OptionList
        self._options_locations = options.OptionList()  # type: options.OptionList
        self._options_features = options.OptionList()  # type: options.OptionList
        self._options_npcs = options.OptionList()  # type: options.OptionList

    @abstractmethod
    def text(self, game: 'app.Game'):
        """Get the text to display for this location.

        :param game: The app.Game instance displaying this location
        :return: The text to display for this location
        """
        raise NotImplementedError()

    def options(self, game: 'app.Game') -> 'options.OptionList':
        """Get the OptionList instance used to set the options for this location.

        This method uses the OptionList.generate_paged_list() method to create standard options for travel locations,
        feature locations, and NPCs present at the location. If the respective method returns None, then that button is
        not created.

        :param game: The app.Game instance displaying this location
        :return: An OptionList instance denoting options for this location
        """
        self._options.clear()
        _locations = self.locations(game)
        if _locations:
            if len(_locations) > 0:
                game.log.debug("BasicLocation::options(): Adding Travel button")
                travel_options = list((name, event.LocationEvent(dest, td)) for name, dest, td in _locations)
                self._options_locations = options.OptionList.generate_paged_list(travel_options)
                opt_travel = options.Option("Travel", event.UpdateOptionsEvent(self._options_locations))
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
                self._options_features = options.OptionList.generate_paged_list(feature_options)
                opt_features = options.Option("Visit", event.UpdateOptionsEvent(self._options_features))
                self._options.set(opt_features, 0, 1)
            else:
                game.log.debug("BasicLocation::options(): Feature options list is empty")
        else:
            game.log.debug("BasicLocation::options(): Feature options list is None")

        return self._options

    @abstractmethod
    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[ResourceID, str, int]]]':
        """Get a list of (name, resource_id, minutes) tuples which denote locations that may be traveled to.

        :param game: The game object
        :return: A list of possible locations to travel to from this location
        """
        raise NotImplementedError()

    @abstractmethod
    def features(self, game: 'app.Game') -> 'Optional[List[Tuple[ResourceID, str, int]]]':
        """Get a list of (name, resource_id, minutes) tuples which denote features within this location.

        :param game: The game object
        :return: A list of possible sub-locations to visit at this location
        """
        raise NotImplementedError()

    @abstractmethod
    def npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[ResourceID, str]]]':
        """Get a list of (name, resource_id) tuples which denote npcs at this location.

        :param game: The game object
        :return: A list of npcs at this location
        """
        raise NotImplementedError()


class BasicLocationImpl(BasicLocation):

    """A subclass of BasicLocationImpl which provides default methods for the BasicLocation API.

    """

    def __init__(self, name_id: str) -> None:
        """Initialize the BasicLocationImpl instance.

        :param name_id: The unique id of this BasicLocationImpl
        """
        BasicLocation.__init__(self, name_id)

    @abstractmethod
    def title(self, game: 'app.Game') -> str:
        raise NotImplementedError()

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        """Get the text to display for this location.

        :param game: The app.Game instance displaying this location
        :return: The text to display for this location
        """
        raise NotImplementedError()

    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[ResourceID, str, int]]]':
        """Get the locations which may be traveled to from this location.

        If not overloaded by a subclass, this method just returns None. This allows locations which don't provide travel
        options to just ignore this method.

        :param game: The app.Game instance displaying this location
        :return: A list of locations which may be traveled to, or None
        """
        return None

    def features(self, game: 'app.Game') -> 'Optional[List[Tuple[ResourceID, str, int]]]':
        """Get the feature locations which may be visited from this location.

        If not overloaded by a subclass, this method just returns None. This allows locations which don't provide
        features to visit to just ignore this method.

        :param game: The app.Game instance displaying this location
        :return: A list of locations which may be visited at this location, or None
        """
        return None

    def npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[ResourceID, str]]]':
        """Get the npcs who are present at this location.

        If not overloaded by a subclass, this method just returns None. This allows locations which don't provide NPCs
        to just ignore this method.

        :param game:
        :return:
        """
        return None
