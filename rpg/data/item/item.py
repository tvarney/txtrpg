
from enum import IntEnum, unique
from rpg.data import resource

import typing
if typing.TYPE_CHECKING:
    from rpg.data.resource import ResourceID
    from rpg.data.actor import Actor
    from typing import Callable


@unique
class ItemType(IntEnum):
    """An enumeration of the types of Items that the game recognizes.

    These values are used to categorize what an item instance is in the game,
    providing an ostensibly faster method of checking if the item is one of the
    various sub-classes of item.

    Values are as follows:
        Misc - An item with no real use. May be used for quests, recipes, or
               just be something to sell.
        Consumable - An item which may be consumed in some fashion. These tend
                     to have effects
        Weapon - An item which provides attacks for an Actor
        Shield - An item which can be used to block attacks
        Armor - An item which can be worn to provide protection against attacks
    """

    Misc = 0
    Consumable = 1
    Weapon = 2
    Shield = 3
    Armor = 4


@unique
class EquipSlot(IntEnum):
    Helmet = 0      # Full/Medium helmets, hats
    Eyes = 1        # Goggles, glasses, blindfolds
    Neck = 2        # Necklaces
    Chest = 3       # Chest-Middle (armor)
    Coat = 4        # Chest-Over (Jackets/Mantles)
    Undershirt = 5  # Chest-Under (Shirts)
    Waist = 6       # Belts, sashes
    Legs = 7        # Legs-Middle (armor)
    Pants = 8       # Legs-Under (pants)
    Skirt = 9       # Legs-Alternate (skirts/kilts)
    Feet = 10       # Boots, shoes, sandals
    Hands = 11      # Gloves, Gauntlets
    Back = 12       # Capes/Backpacks (Wings, lol)
    Quiver = 13
    Ring = 14
    Held = 15       # Weapons and shields
    COUNT = 16


class Item(resource.Resource):
    """The base class for Items.

    The base class defines a few shared members of all items, namely the type
    of the item, the name of the item, the base value of the item, and the
    weight of the item in kg.

    The type of the item must be a valid ItemType enum value, and is used to
    determine what the player can do with the item as well as what subclass the
    item is.

    The base value of the item is the cost of the item with no modifiers added.
    This value is the buy price of the item when the players charisma is
    exactly 10 (no modifier).
    """

    def __init__(
        self, resource_id: 'ResourceID', item_type: ItemType, name: str,
        value: int, weight: float, stack: bool = True,
    ) -> None:
        """Initialize a new Item instance.

        :param resource_id: The unique string used to identify this item
        :param item_type: The type of this item
        :param name: The name displayed for this item
        :param value: The base value of this item
        :param weight: How much the item weighs in kg
        """
        resource.Resource.__init__(
            self, resource.ResourceType.Item, resource_id
        )
        self._item_type = item_type
        self._name = name
        self._value = value
        self._weight = weight
        self._stackable = stack

    @property
    def type(self) -> ItemType:
        """Get the type of this item instance.

        :return: The type of the item
        """
        return self._item_type

    @property
    def name(self) -> str:
        """Get the name of this item instance.

        :return: The name of the item
        """
        return self._name

    @property
    def value(self) -> int:
        """Get the value of the item.

        :return:
        """
        return self._value

    def weight(self) -> float:
        """Get the weight of the item.

        :return: The weight of the item
        """
        return self._weight

    def stackable(self) -> bool:
        """Check if the item is stackable

        :return: If the item is stackable
        """
        return self._stackable


class WearableItem(Item):
    def __init__(self, resource_id: str, item_type: ItemType, name: str,
                 value: int, weight: float, slot: EquipSlot) -> None:
        Item.__init__(
            self, resource_id, item_type, name, value, weight, False
        )
        self._slot = slot

    def slot(self) -> EquipSlot:
        return self._slot


class MiscItem(Item):
    """Base class which can be used to create misc items.

    MiscItem instances can be used for quests, recipes, or just selling.
    """

    def __init__(self, resource_id: str, name: str, value: int,
                 weight: float) -> None:
        """Initialize the misc. item instance.

        :param resource_id: The unique string used to look this item up
        :param name: The name of this item
        :param value: The base value of this misc item
        :param weight: How much this item weighs in kg
        """
        Item.__init__(self, resource_id, ItemType.Misc, name, value, weight)


class Consumable(Item):
    """An item which can be consumed in some fashion.

    These items are things like potions, food, or special items which can be
    used to provide an effect.
    """

    def __init__(self, resource_id: str, name: str, value: int, weight: float,
                 fn_callback: 'Callable[[Consumable, Actor], None]') -> None:
        """Initialize this consumable item.

        :param resource_id: The unique string used to look up the consumable
        :param name: The name of the consumable item
        :param value: The base value of the consumable item
        :param weight: The weight of the consumable item
        :param fn_callback: A callback function used when the consumable is
        """
        Item.__init__(
            self, resource_id, ItemType.Consumable, name, value, weight
        )
        self._callback = fn_callback

    def apply(self, target: 'Actor'):
        """Method used to call the provided callback function

        :param target: The actor which this consumable item is being used on
        """
        self._callback(self, target)
