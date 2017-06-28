
from enum import IntEnum, unique
from rpg.data import resource

import typing
if typing.TYPE_CHECKING:
    from typing import Callable, List, Optional


@unique
class ItemType(IntEnum):
    Misc = 0
    Consumable = 1
    Weapon = 2
    Shield = 3
    Armor = 4


@unique
class WeaponType(IntEnum):
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
    def __init__(self, resource_id: str, item_type: ItemType, name: str, value: int):
        resource.Resource.__init__(self, resource.ResourceType.Item, resource_id)
        self._item_type = item_type
        self._name = name
        self._value = value

    def name(self) -> str:
        return self._name

    def value(self) -> int:
        return self._value


class Attack(object):
    def __init__(self, name: str, dmg: int, accuracy: int):
        self._name = name
        self._dmg = dmg
        self._accuracy = accuracy

    def name(self) -> str:
        return self._name

    def damage(self) -> int:
        return self._dmg

    def accuracy(self) -> int:
        return self._accuracy

    def __str__(self):
        return "{}: dmg={}, accuracy={}".format(self._name, self._dmg, self._accuracy)

    def __repr__(self):
        return "Attack({}, {}, {})".format(repr(self._name), repr(self._dmg), repr(self._accuracy))


class CombatItem(Item):
    def __init__(self, resource_id: str, item_type: ItemType, name: str, value: int, hand_slots: int,
                 attacks: 'Optional[List[Attack]]', block: int):
        Item.__init__(self, resource_id, item_type, name, value)
        self._hand_slots = hand_slots
        self._attacks = attacks if attacks is None or len(attacks) > 0 else None
        self._block = block


class Weapon(CombatItem):
    def __init__(self, resource_id: str, weapon_type: WeaponType, name: str, value: int, hand_slots: int,
                 attacks: 'List[Attack]', parry: int):
        CombatItem.__init__(self, resource_id, ItemType.Weapon, name, value, hand_slots, attacks, parry)
        self._weapon_type = weapon_type


class Shield(CombatItem):
    def __init__(self, resource_id: str, name: str, value: int, hand_slots: int, block: int,
                 attacks: 'Optional[List[Attack]]' = None):
        CombatItem.__init__(self, resource_id, ItemType.Shield, name, value, hand_slots, attacks, block)


class MiscItem(Item):
    def __init__(self, resource_id: str, name: str, value: int):
        Item.__init__(self, resource_id, ItemType.Misc, name, value)


class Consumable(Item):
    def __init__(self, resource_id: str, name: str, value: int, fn_callback: 'Callable[]'):
        Item.__init__(self, resource_id, ItemType.Consumable, name, value)
        self._callback = fn_callback

    def apply(self, target):
        self._callback(self, target)
