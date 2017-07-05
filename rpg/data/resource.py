
"""Define resource objects which can be imported from package objects.

This module defines an abstract base class 'Resource' and the subclasses of it which can be loaded from package objects
defined in the ./data/packages directory of the game.

Resources are defined such that they hold both a type_id and a resource_id; the type_id denotes the type of the resource
and the resource_id is a unique string used to look the resource up.
"""

from abc import ABCMeta, abstractmethod
from enum import IntEnum, unique
from rpg import event
from rpg.data import actor, attributes
from rpg.ui import options as _options

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import List, Optional, Tuple


@unique
class ResourceType(IntEnum):

    """An integer tag which denotes the type of the resource.

    The values here are used by the Resources class (defined in rpg.data.resource) to put all resource of the same type
    into the same map.

    """

    Location = 0
    Dialog = 1
    Item = 2
    Monster = 3
    Callback = 4
    COUNT = 5


class Resource(metaclass=ABCMeta):

    """The abstract base class of all Resources.

    A resource is defined as any object which can be loaded from packages (defined by rpg.io.package). Sub-classes of
    the resource should pass the correct ResourceType enum value to the __init__(...) function of the Resource class.

    """

    def __init__(self, type_id: ResourceType, resource_id: str) -> None:
        """Create a new Resource object.

        :param type_id: The ResourceType enum object appropriate for this type of Resource
        :param resource_id: The unique string identifier used to look this Resource up
        """
        self._type_id = type_id  # type: ResourceType
        self._resource_id = resource_id  # type: str
        self._package = None  # type: Optional[str]

    def type_id(self) -> ResourceType:
        """Get the ResourceType type_id of this Resource instance.

        :return: The type_id of this Resource
        """
        return self._type_id

    def resource_id(self) -> str:
        """Get the resource_id string of this resource.

        :return: The resource_id string of this Resource instance
        """
        return self._resource_id

    def package(self) -> 'Optional[str]':
        """Get the package which defined this resource object.

        The package name is filled out by the package class (rpg.io.package) after loading all resources.

        :return: The name of the package which defined this object
        """
        return self._package


class Callback(Resource):

    """A callback method defined in a Resource Package.

    Callback instances are used to pre- and post-initialize the game, as well as provide hooks for various other
    points of game initialization.

    """

    def __init__(self, resource_id: str) -> None:
        """Create a new Callback instance.

        :param resource_id: The unique string identifying this Callback Resource
        """
        Resource.__init__(self, ResourceType.Callback, resource_id)

    @abstractmethod
    def apply(self, game: 'app.Game') -> None:
        """Apply this callback to the game object given.

        :param game: The game object to apply this callback to
        """
        raise NotImplementedError()


class MonsterTemplate(Resource):

    """A template used to generate monsters.

    The MonsterTemplate class defines all the data needed to dynamically generate a monster for any given difficulty
    level. Ideally, this object is able to change the name/stats/attacks of a given monster generated based on the
    difficulty of the encounter, as well as global/game-state settings for difficulty.

    """

    def __init__(self, resource_id: str, name: str, **kwargs) -> None:
        """Create a new MonsterTemplate instance.

        Keyword arguments to this function may be any of the following:
            str: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters strength attribute
            dex: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters dexterity attribute
            con: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters constitution attribute
            agl: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters agility attribute
            int: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters intelligence attribute
            wis: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters wisdom attribute
            cha: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters charisma attribute
            lck: Union[int, Tuple[int, int, int]] = 10
                The flat value or a tuple of length 3 defining a range for the monsters luck attribute
            health: Union[int, Tuple[int, int, int]] = None
                The flat value or a tuple of length 3 defining a range for the monsters health
                If this is left as None, then the health formula is used instead
            stamina: Union[int, Tuple[int, int, int]] = None
                The flat value or a tuple of length 3 defining a range for the monsters stamina
                If this is left as None, then the stamina formula is used instead
            mana: Union[int, Tuple[int, int, int]] = None
                The flat value or a tuple of length 3 defining a range for the monsters mana
                If thie is left as None, then the mana formula is used instead


        :param resource_id: The unique string used to identify this monster template
        :param name: The name of the monster
        :param kwargs: Various other arguments which may be left blank for a default value
        """
        Resource.__init__(self, ResourceType.Monster, resource_id)
        self._name = name
        
        self._strength = kwargs.get("str", 10)
        self._dexterity = kwargs.get("dex", 10)
        self._constitution = kwargs.get("con", 10)
        self._agility = kwargs.get("agl", 10)
        self._intelligence = kwargs.get("int", 10)
        self._wisdom = kwargs.get("cha", 10)
        self._charisma = kwargs.get("cha", 10)
        self._luck = kwargs.get("lck", 10)
        
        self._health = kwargs.get("health", None)
        self._mana = kwargs.get("mana", None)
        self._stamina = kwargs.get("stamina", None)
    
    def generate(self) -> 'actor.Monster':
        """Generatea a monster instance from this template.

        :return: A new instance of rpg.actor.Monster which can be used in a Fight instance
        """
        _ability_scores = attributes.AttributeList(str=self._strength, dex=self._dexterity, con=self._constitution,
                                                   agl=self._agility, int=self._intelligence, wis=self._wisdom,
                                                   cha=self._charisma, lck=self._luck, health=self._health,
                                                   stamina=self._stamina, mana=self._mana)
        _monster = actor.Monster(self._name, None, _ability_scores)
        return _monster


class Displayable(Resource):

    """A resource which can be displayed on a GameView instance.

    The displayable class adds two new abstract methods to the Resource abstract base class which define how the
    resource is displayed on the GameView instance. In addition, the start() and resume() methods are defined but
    given a default implementation, allowing Displayable Resources to have a callback before being displayed.

    """

    def __init__(self, type_id: ResourceType, resource_id: str) -> None:
        """Create a new Displayable instance.

        The Displayable class is not a valid Resource type in and of itself; sub-classes of the Displayable class should
        pass the __init__(...) method a valid ResourceType.

        :param type_id: The ResourceType of the displayable Resource
        :param resource_id: The unique string used to identify this displayable Resource
        """
        Resource.__init__(self, type_id, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        """Get the text to display for this Displayable instance.

        :param game: A handle to the app.Game instance this displayable is being displayed in
        :return: The text to place on the active GameView instance
        """
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> '_options.OptionList':
        """Get the options list for this Displayable.

        :param game: A handle to the app.Game instance this displayable is being displayed in
        :return: An options.OptionList instance which represents the options available for this Displayable instance
        """
        raise NotImplementedError()

    def start(self, game: 'app.Game'):
        """Callback hook for doing something before this displayable is actually displayed.

        This method can be overridden to do anything from variable set-up to outright changing the current state of the
        game. For instance, a location could override this and check a boolean value in the variables. If the value was
        false, then the location could force the game to go immediately into a dialog instead.

        This method defaults to doing absolutely nothing

        :param game: A handle to the app.Game instance this displayable is being displayed in
        """
        pass

    def resume(self, game: 'app.Game'):
        """Callback hook for doing something when this Displayable is shown again after being obscured.

        This method defaults to simply calling self.start(game)

        :param game: A handle to the app.Game instance this displayable is being displayed in
        """
        self.start(game)


class Location(Displayable):

    """Abstract base class of all Location objects.

    A location object represents the current part of the game world that the player is in. These are further divided
    down into actual Locations and 'Features'. A feature is generally used for parts of the parent location which either
    take no time or very little time to travel to. Features can be things like shops, houses, alleyways, etc.

    There are further subclasses of Location which simplify the process of creating a Location by standardizing on how
    the data the location holds and how it displays it, though it is a perfectly valid method to provide subclasses of
    the base Location class.

    """

    def __init__(self, resource_id: str) -> None:
        """Initialize the Location instance.

        :param resource_id: The unique id string used to look this location up
        """
        Displayable.__init__(self, ResourceType.Location, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        """Get the text to display for this Location.

        :param game: The app.Game instance displaying this Location
        :return: The text to display for this Location
        """
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> '_options.OptionList':
        """Get the OptionList used to set the options for this Location.

        :param game: The app.Game instance displaying this Location
        :return: An OptionList instance denoting the options available at this Location
        """
        raise NotImplementedError()


class Dialog(Displayable):

    """Base class for resources representing narration or conversations.

    This class is used to provide extra narration at a Location or to handle conversations.

    """

    def __init__(self, resource_id: str) -> None:
        """Initialize the Dialog instance.

        :param resource_id: The unique id string used to look this dialog up
        """
        Displayable.__init__(self, ResourceType.Dialog, resource_id)

    @abstractmethod
    def text(self, game: 'app.Game') -> str:
        """Get the text to display for this Dialog.

        :param game: The app.Game instance displaying this Dialog
        :return: The text to display for this Dialog
        """
        raise NotImplementedError()

    @abstractmethod
    def options(self, game: 'app.Game') -> '_options.OptionList':
        """Get the OptionList used to set the options for this Dialog.

        :param game: The app.Game instance displaying this Dialog
        :return: An OptionList instance denoting the options available for this Dialog
        """
        raise NotImplementedError()


class BasicLocation(Location):

    """Specialization of the Location class to provide a standard interface to most locations.

    The BasicLocation class defines the concept of a Location providing links to other locations, a collection of
    'features' or sub-locations of this location, and non-player characters.

    These methods are all marked abstract and left to the implementation to provide.

    """

    def __init__(self, name_id: str) -> None:
        """Initialize the BasicLocation instance.

        :param name_id: The unique id used to look this location up
        """
        Location.__init__(self, name_id)
        self._options = _options.OptionList()  # type: _options.OptionList
        self._options_locations = _options.OptionList()  # type: _options.OptionList
        self._options_features = _options.OptionList()  # type: _options.OptionList
        self._options_npcs = _options.OptionList()  # type: _options.OptionList

    @abstractmethod
    def text(self, game: 'app.Game'):
        """Get the text to display for this location.

        :param game: The app.Game instance displaying this location
        :return: The text to display for this location
        """
        raise NotImplementedError()

    def options(self, game: 'app.Game') -> '_options.OptionList':
        """Get the OptionList instance used to set the options for this location.

        This method uses the OptionList.generate_paged_list() method to create standard options for travel locations,
        feature locations, and NPCs present at the location. If the resepctive method returns None, then that button is
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
        """Get a list of (name, resource_id, minutes) tuples which denote locations that may be traveled to.

        :param game: The game object
        :return: A list of possible locations to travel to from this location
        """
        raise NotImplementedError()

    @abstractmethod
    def features(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        """Get a list of (name, resource_id, minutes) tuples which denote features within this location.

        :param game: The game object
        :return: A list of possible sub-locations to visit at this location
        """
        raise NotImplementedError()

    @abstractmethod
    def npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str]]]':
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
    def text(self, game: 'app.Game') -> str:
        """Get the text to display for this location.

        :param game: The app.Game instance displaying this location
        :return: The text to display for this location
        """
        raise NotImplementedError()

    def locations(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        """Get the locations which may be traveled to from this location.

        If not overloaded by a subclass, this method just returns None. This allows locations which don't provide travel
        options to just ignore this method.

        :param game: The app.Game instance displaying this location
        :return: A list of locations which may be traveled to, or None
        """
        return None

    def features(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str, int]]]':
        """Get the feature locations which may be visited from this location.

        If not overloaded by a subclass, this method just returns None. This allows locations which don't provide
        features to visit to just ignore this method.

        :param game: The app.Game instance displaying this location
        :return: A list of locations which may be visited at this location, or None
        """
        return None

    def npcs(self, game: 'app.Game') -> 'Optional[List[Tuple[str, str]]]':
        """Get the npcs who are present at this location.

        If not overloaded by a subclass, this method just returns None. This allows locations which don't provide NPCs
        to just ignore this method.

        :param game:
        :return:
        """
        return None
