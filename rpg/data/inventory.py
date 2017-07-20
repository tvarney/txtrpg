
from rpg import state
from rpg.data import item, resource

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import Dict, List, Optional


class ItemInstance(object):
    def __init__(self, resource_id: str, game: 'Optional[app.Game]'=None):
        self._resource_id = resource_id
        self._item_obj = None
        if game is not None:
            self.bind(game)

    def bind(self, game: 'app.Game') -> bool:
        if self._item_obj is not None:
            if game.state.state() != state.GameState.Invalid:
                obj = game.state.resources.get(resource.ResourceType.Item, self._resource_id)
                if obj is not None:
                    self._item_obj = obj
                    return True
        return False

    def item(self) -> 'Optional[item.Item]':
        return self._item_obj


class ItemStack(object):
    def __init__(self, item_instance: ItemInstance, count: int):
        self._item = item_instance
        self._count = count

    def weight(self) -> float:
        return self._item.item().weight() * self._count

    def item(self) -> ItemInstance:
        return self._item

    def count(self) -> int:
        return self._count

    def inc(self, amount=1) -> int:
        self._count += amount
        return self._count

    def dec(self, amount=1) -> int:
        self._count -= amount
        return self._count


class Inventory(object):
    def __init__(self):
        self._weight = 0.0  # type: float
        self._slots = dict()  # type: Dict[str, ItemStack]
        self._equipped = [None for _ in range(item.EquipSlot.COUNT)]  # type: List['item.Instance']

    def add(self, item_instance: 'item.Item') -> None:
        pass

    def remove(self, item_instance: 'item.Item') -> None:
        pass

    def equip(self, slot_id: int, count: int) -> None:
        pass

    def unequip(self, equip_slot: item.EquipSlot) -> None:
        pass

    def weight(self) -> float:
        return self._weight
