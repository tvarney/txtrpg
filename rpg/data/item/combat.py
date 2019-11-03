
from enum import IntEnum, unique
import rpg.data.item.item as _item

import typing
if typing.TYPE_CHECKING:
    from typing import List, Optional


@unique
class WeaponType(IntEnum):
    """An enumeration of the different types of weapons.

    Each type of weapon has different trade-offs. For instance, a weapon which
    is fast may allow multiple attacks per round (independent of agility), yet
    have very low damage.

    Weapon types and their strengths/weaknesses are as follows:
        Dagger: Very fast, low damage. Daggers get to attack twice per action
        ShortSword: Fast, low damage, good block
        LongSword: Average, average damage
        GreatSword: Slow, high damage
        Scimitar: Average, average damage
        LongBow: Allow 2 attacks at range
        ShortBow: Allow 1 attack at range
        Spear: Average speed, average damage, disadvantages opponents with
               swords or daggers
        Halberd: Low speed, high damage, disadvantages opponents with swords or
                 daggers
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


class Attack(object):
    """Definition of an attack.

    The Attack class defines an attack which may be performed during a fight
    instance. At least one of these needs to be defined for a weapon for it to
    be usable in combat. In addition, actors may have attacks added to them as
    well; these attacks objects represent unarmed attacks that the character
    may attempt.
    """

    def __init__(self, name: str, dmg: int, accuracy: int) -> None:
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
        return "{}: dmg={}, accuracy={}".format(
            self._name, self._dmg, self._accuracy
        )

    def __repr__(self):
        return "Attack({}, {}, {})".format(
            repr(self._name), repr(self._dmg), repr(self._accuracy)
        )


class ArmorItem(_item.WearableItem):
    def __init__(self, resource_id: str, name: str, value: int, weight: float,
                 slot: _item.EquipSlot, damage_reduce: int) -> None:
        _item.WearableItem.__init__(
            self, resource_id, _item.ItemType.Armor, name, value, weight, slot
        )
        self._damage_reduce = damage_reduce

    def damage_reduce(self) -> int:
        return self._damage_reduce


class CombatItem(_item.WearableItem):
    """Base class for items which are used in combat."""

    def __init__(self, resource_id: str, item_type: _item.ItemType, name: str,
                 value: int, weight: float, hand_slots: int,
                 attacks: 'Optional[List[Attack]]', block: int) -> None:
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
        _item.WearableItem.__init__(
            self, resource_id, item_type, name, value, weight,
            _item.EquipSlot.Held
        )
        self._hand_slots = hand_slots
        self._attacks = None  # type: Optional[List[Attack]]
        if attacks is not None and len(attacks) > 0:
            self._attacks = attacks
        self._block = block


class Shield(CombatItem):
    """Class used to create shields.

    Despite not being a weapon, a shield can be used to attack in combat. Doing
    so means that the shield can not be used to block an attack.
    """

    def __init__(self, resource_id: str, name: str, value: int, weight: float,
                 hand_slots: int, block: int,
                 attacks: 'Optional[List[Attack]]' = None) -> None:
        """Initialize the shield instance.

        :param resource_id: The unique string used to look this shield up
        :param name: The name of the shield
        :param value: How much the shield is worth
        :param weight: How much the shield weighs in kg
        :param hand_slots: How many hand slots this shield takes
        :param block: How well this shield blocks attacks
        :param attacks: Any attacks this shield may make
        """
        CombatItem.__init__(
            self, resource_id, _item.ItemType.Shield, name, value, weight,
            hand_slots, attacks, block
        )


class Weapon(CombatItem):
    """Class used to create weapons."""
    def __init__(self, resource_id: str, weapon_type: WeaponType, name: str,
                 value: int, weight: float, hand_slots: int,
                 attacks: 'List[Attack]', parry: int) -> None:
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
        CombatItem.__init__(
            self, resource_id, _item.ItemType.Weapon, name, value, weight,
            hand_slots, attacks, parry
        )
        self._weapon_type = weapon_type

