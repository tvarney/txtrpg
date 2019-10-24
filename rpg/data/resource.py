
"""Define resource objects which can be imported from package objects.

This module defines an abstract base class 'Resource' and the subclasses of it which can be loaded from package objects
defined in the ./data/packages directory of the game.

Resources are defined such that they hold both a type_id and a resource_id; the type_id denotes the type of the resource
and the resource_id is a unique string used to look the resource up.
"""

from abc import ABCMeta, abstractmethod
from enum import IntEnum, unique
from rpg.ui import options as _options

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import resources
    from rpg.ui import options
    from typing import Callable, List, Optional, Tuple


ResourceID = str


@unique
class ResourceType(IntEnum):

    """An integer tag which denotes the type of the resource.

    The values here are used by the Resources class (defined in rpg.data.resource) to put all resource of the same type
    into the same map.

    """

    Location = 0
    Dialog = 1
    Item = 2
    Actor = 3
    Callback = 4
    Recipe = 5
    COUNT = 6


class Resource(metaclass=ABCMeta):

    """The abstract base class of all Resources.

    A resource is defined as any object which can be loaded from packages (defined by rpg.io.package). Sub-classes of
    the resource should pass the correct ResourceType enum value to the __init__(...) function of the Resource class.

    """

    def __init__(self, type_id: ResourceType, resource_id: ResourceID) -> None:
        """Create a new Resource object.

        :param type_id: The ResourceType enum object appropriate for this type of Resource
        :param resource_id: The unique string identifier used to look this Resource up
        """
        self._type_id = type_id  # type: ResourceType
        self._resource_id = resource_id  # type: ResourceID
        self._package = None  # type: Optional[str]

    def type_id(self) -> ResourceType:
        """Get the ResourceType type_id of this Resource instance.

        :return: The type_id of this Resource
        """
        return self._type_id

    def resource_id(self) -> ResourceID:
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

    def __init__(self, resource_id: ResourceID) -> None:
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


class Displayable(Resource):

    """A resource which can be displayed on a GameView instance.

    The displayable class adds two new abstract methods to the Resource abstract base class which define how the
    resource is displayed on the GameView instance. In addition, the start() and resume() methods are defined but
    given a default implementation, allowing Displayable Resources to have a callback before being displayed.

    """

    def __init__(self, type_id: ResourceType, resource_id: ResourceID) -> None:
        """Create a new Displayable instance.

        The Displayable class is not a valid Resource type in and of itself; sub-classes of the Displayable class should
        pass the __init__(...) method a valid ResourceType.

        :param type_id: The ResourceType of the displayable Resource
        :param resource_id: The unique string used to identify this displayable Resource
        """
        Resource.__init__(self, type_id, resource_id)

    @abstractmethod
    def title(self, game: 'app.Game') -> str:
        """Get the title of this displayable resource.

        :param game: The app.Game instance
        :return: The title of this displayable resource
        """
        raise NotImplementedError()

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


class Dialog(Displayable):

    """Base class for resources representing narration or conversations.

    This class is used to provide extra narration at a Location or to handle conversations.

    """

    def __init__(self, resource_id: ResourceID) -> None:
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
    def options(self, game: 'app.Game') -> 'options.OptionList':
        """Get the OptionList used to set the options for this Dialog.

        :param game: The app.Game instance displaying this Dialog
        :return: An OptionList instance denoting the options available for this Dialog
        """
        raise NotImplementedError()


@unique
class RecipeCategory(IntEnum):
    General = 0
    Smelting = 1
    Smithing = 2
    Cooking = 3
    Crafting = 4


class Recipe(Resource):

    """Implementation of a crafting recipe

    """

    def __init__(self, resource_id: ResourceID, name: str, skill: 'List[Tuple[str, int]]',
                 inputs: 'List[Tuple[ResourceID, int]]', outputs: 'List[Tuple[ResourceID, int]]',
                 **kwargs) -> None:
        """Create a new Recipe

        :param resource_id: The resource_id of this Recipe
        :param name: The displayed name of this Recipe
        :param skill: A list of tuples of (skill_name, skill_level) required to use this Recipe
        :param inputs: A list of tuples of (resource_id, count) input items needed to use this Recipe
        :param outputs: A list of tuples of (resource_id, count) output items to yield on completion of the Recipe
        """
        Resource.__init__(self, ResourceType.Recipe, resource_id)
        self._name = name
        self._inputs = inputs
        self._outputs = outputs
        self._skill = skill
        self._category = kwargs.get("category", RecipeCategory.General)
        self._available_callback = kwargs.get("avail_callback", None)  # type: Optional[Callable[[app.Game], bool]]

    def available(self, game: 'app.Game') -> bool:
        if self._available_callback is not None:
            return self._available_callback(game)
        return True

    def category(self) -> RecipeCategory:
        return self._category

    def validate(self, resource_package: 'resources.Resources') -> 'Tuple(bool, Optional[str])':
        errors = list()
        for _item, _count in self._inputs:
            if resource_package.get(ResourceType.Item, _item) is None:
                errors.append("  Invalid input item resource '{}'".format(_item))
            if _count <= 0:
                errors.append("  Invalid count value for input resource '{}'".format(_count))
        for _item, _count in self._outputs:
            if resource_package.get(ResourceType.Item, _item) is None:
                errors.append("  Invalid output item resource '{}'".format(_item))
            if _count <= 0:
                errors.append("  Invalid count value for input resource '{}'".format(_count))
        # TODO: Validate skills exist
        if len(errors) > 0:
            return False, "Errors in Recipe '{}':\n{}".format(self._name, "\n".join(errors))
        return True, None
