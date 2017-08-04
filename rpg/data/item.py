
from enum import IntEnum, unique
from rpg.data import resource

import typing
if typing.TYPE_CHECKING:
    from typing import Callable, List, Optional


@unique
class ItemType(IntEnum):

    """An enumeration of the types of Items that the game recognizes.

    These values are used to categorize what an item instance is in the game, providing an ostensibly faster method of
    checking if the item is one of the various sub-classes of item.

    Values are as follows:
        Misc - An item with no real use. May be used for quests, recipes, or just be something to sell.
        Consumable - An item which may be consumed in some fashion. These tend to have effects
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


@unique
class WeaponType(IntEnum):

    """An enumeration of the different types of weapons.

    Each type of weapon has different trade-offs. For instance, a weapon which is fast may allow multiple attacks per
    round (independent of agility), yet have very low damage.

    Weapon types and their strengths/weaknesses are as follows:
        Dagger: Very fast, low damage. Daggers get to attack twice per action
        ShortSword: Fast, low damage, good block
        LongSword: Average, average damage
        GreatSword: Slow, high damage
        Scimitar: Average, average damage
        LongBow: Allow 2 attacks at range
        ShortBow: Allow 1 attack at range
        Spear: Average speed, average damage, disadvantages opponents with swords or daggers
        Halberd: Low speed, high damage, disadvantages opponents with swords or daggers
        Whip: Very fast, low damage, inflicts stun occasionally on hit
        Staff: Fast, low damage, spell casting bonus

    """

    Dagger = 0
    ShortSword = 1
    LongSword = 2
    GreatSword = 3
    Scimitar = 4
    LongBow = 5
    ShortBow = 6
    Spear = 7
    Halberd = 8
    Whip = 9
    Staff = 10


class Item(resource.Resource):

    """The base class for Items.

    The base class defines a few shared members of all items, namely the type of the item, the name of the item, the
    base value of the item, and the weight of the item in kg.

    The type of the item must be a valid ItemType enum value, and is used to determine what the player can do with the
    item as well as what subclass the item is.

    The base value of the item is the cost of the item with no modifiers added. This value is the buy price of the item
    when the players charisma is exactly 10 (no modifier).

    """

    def __init__(self, resource_id: str, item_type: ItemType, name: str, value: int, weight: float, stack: bool=True):
        """Initialize a new Item instance.

        :param resource_id: The unique string used to identify this item
        :param item_type: The type of this item
        :param name: The name displayed for this item
        :param value: The base value of this item
        :param weight: How much the item weighs in kg
        """
        resource.Resource.__init__(self, resource.ResourceType.Item, resource_id)
        self._item_type = item_type
        self._name = name
        self._value = value
        self._weight = weight
        self._stackable = stack

    def type(self) -> ItemType:
        """Get the type of this item instance.

        :return: The type of the item
        """
        return self._item_type

    def name(self) -> str:
        """Get the name of this item instance.

        :return: The name of the item
        """
        return self._name

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


class Attack(object):

    """Definition of an attack.

    The Attack class defines an attack which may be performed during a fight instance. At least one of these needs to be
    defined for a weapon for it to be usable in combat. In addition, actors may have attacks added to them as well;
    these attacks objects represent unarmed attacks that the character may attempt.

    """

    def __init__(self, name: str, dmg: int, accuracy: int):
        """Create a new attack instance.

        :param name: The name of the attack displayed to the user
        :param dmg: The amount of damage that the attack does
        :param accuracy: How accurate the attack is
        """
        # TODO: Add a flag for checking if one or both hands are free
        self._name = name
        self._dmg = dmg
        self._accuracy = accuracy

    def name(self) -> str:
        """Get the name of this attack.

        :return: The name of the attack
        """
        return self._name

    def damage(self) -> int:
        """Get the damage this attack can do

        :return:
        """
        return self._dmg

    def accuracy(self) -> int:
        """Get the accuracy of this attack.

        :return: The accuracy of the attack
        """
        return self._accuracy

    def __str__(self):
        """Get a string representation of this attack

        :return: A string representation of this attack
        """
        return "{}: dmg={}, accuracy={}".format(self._name, self._dmg, self._accuracy)

    def __repr__(self):
        return "Attack({}, {}, {})".format(repr(self._name), repr(self._dmg), repr(self._accuracy))


class WearableItem(Item):
    def __init__(self, resource_id: str, item_type: ItemType, name: str, value: int, weight: float, slot: EquipSlot):
        Item.__init__(self, resource_id, item_type, name, value, weight, False)
        self._slot = slot

    def slot(self) -> EquipSlot:
        return self._slot


class ArmorItem(WearableItem):
    def __init__(self, resource_id: str, name: str, value: int, weight: float, slot: EquipSlot, damage_reduce: int):
        WearableItem.__init__(self, resource_id, ItemType.Armor, name, value, weight, slot)
        self._damage_reduce = damage_reduce

    def damage_reduce(self) -> int:
        return self._damage_reduce


class CombatItem(WearableItem):
    """Base class for items which are used in combat.

    """

    def __init__(self, resource_id: str, item_type: ItemType, name: str, value: int, weight: float, hand_slots: int,
                 attacks: 'Optional[List[Attack]]', block: int):
        """Initialize the combat item instance.

        :param resource_id: The unique string used to look this item up
        :param item_type: The type of this item
        :param name: The name of this item
        :param value: The base value of this item
        :param weight: The weight of this item in kg
        :param hand_slots: The number of hand slots that this combat item takes
        :param attacks: Attacks that may be made with this combat item
        :param block: How well this item can be used to block attacks
        """
        WearableItem.__init__(self, resource_id, item_type, name, value, weight, EquipSlot.Held)
        self._hand_slots = hand_slots
        self._attacks = attacks if attacks is None or len(attacks) > 0 else None
        self._block = block


class Weapon(CombatItem):
    """Class used to create weapons.

    """
    def __init__(self, resource_id: str, weapon_type: WeaponType, name: str, value: int, weight: float, hand_slots: int,
                 attacks: 'List[Attack]', parry: int):
        """Initialize the weapon.

        :param resource_id: The unique string used to look this weapon up
        :param weapon_type: The type of this weapon (see rpg.data.WeaponType)
        :param name: The name of this weapon
        :param value: The value of this weapon
        :param weight: The weight of this weapon in kg
        :param hand_slots: The number of hand slots this weapon takes
        :param attacks: The attacks that this weapon offers
        :param parry: How well this weapon can be used to block attacks
        """
        CombatItem.__init__(self, resource_id, ItemType.Weapon, name, value, weight, hand_slots, attacks, parry)
        self._weapon_type = weapon_type


class Shield(CombatItem):

    """Class used to create shields.

    Despite not being a weapon, a shield can be used to attack in combat. Doing so means that the shield can not
    be used to block an attack.

    """

    def __init__(self, resource_id: str, name: str, value: int, weight: float, hand_slots: int, block: int,
                 attacks: 'Optional[List[Attack]]' = None):
        """Initialize the shield instance.

        :param resource_id: The unique string used to look this shield up
        :param name: The name of the shield
        :param value: How much the shield is worth
        :param weight: How much the shield weighs in kg
        :param hand_slots: How many hand slots this shield takes
        :param block: How well this shield blocks attacks
        :param attacks: Any attacks this shield may make
        """
        CombatItem.__init__(self, resource_id, ItemType.Shield, name, value, weight, hand_slots, attacks, block)


class MiscItem(Item):

    """Base class which can be used to create misc items.

    MiscItem instances can be used for quests, recipes, or just selling.

    """

    def __init__(self, resource_id: str, name: str, value: int, weight: float):
        """Initialize the misc. item instance.

        :param resource_id: The unique string used to look this item up
        :param name: The name of this item
        :param value: The base value of this misc item
        :param weight: How much this item weighs in kg
        """
        Item.__init__(self, resource_id, ItemType.Misc, name, value, weight)


class Consumable(Item):

    """An item which can be consumed in some fashion.

    These items are things like potions, food, or special items which can be used to provide an effect.

    """

    def __init__(self, resource_id: str, name: str, value: int, weight: float, fn_callback: 'Callable[]'):
        """Initialize this consumable item.

        :param resource_id: The unique string used to look up the consumable item
        :param name: The name of the consumable item
        :param value: The base value of the consumable item
        :param weight: The weight of the consumable item
        :param fn_callback: A callback function which is used to apply the consumable items effect
        """
        Item.__init__(self, resource_id, ItemType.Consumable, name, value, weight)
        self._callback = fn_callback

    def apply(self, target):
        """Method used to call the provided callback function

        :param target: The actor instance which this consumable item is being used on
        """
        self._callback(self, target)
