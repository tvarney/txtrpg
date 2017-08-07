
from rpg import state
from rpg.data import item, resource

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import List, Optional


class ItemInstance(object):
    def __init__(self, resource_id: str, game: 'Optional[app.Game]'=None):
        self._resource_id = resource_id
        self._item_obj = None
        if game is not None:
            self.bind(game)

    def bind(self, game: 'app.Game') -> bool:
        if self._item_obj is None:
            obj = game.state.resources.get(resource.ResourceType.Item, self._resource_id)
            if obj is not None:
                self._item_obj = obj
                return True
        return False

    def unbind(self):
        self._item_obj = None

    def item(self) -> 'Optional[item.Item]':
        return self._item_obj

    def resource_id(self) -> str:
        return self._resource_id


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
        self.slots = list()  # type: List[ItemStack]
        self._equipped = [None for _ in range(item.EquipSlot.COUNT)]  # type: List['item.Instance']
        self._game = None  # type: Optional[app.Game]
        self._max_slots = 100

    def bind(self, game: 'app.Game'):
        if self._game is not None:
            self.unbind()
        self._game = game
        newslots = list()  # type: List[ItemStack]
        for item_stack in self.slots:
            item_stack.item().bind(game)
            if item_stack.item().item() is not None:
                if item_stack.item().item().stackable():
                    newslots.append(item_stack)
                else:
                    count = min(item_stack.count(), self._max_slots - len(newslots))
                    for i in range(count):
                        newslots.append(ItemStack(item_stack.item(), 1))
                    if len(newslots) >= self._max_slots:
                        return
            else:
                game.log.error("Could not find item with resource_id: {}", item_stack.item().resource_id())
        self.slots = newslots

    def unbind(self):
        self._game = None
        for stack in self.slots:
            stack.item().unbind()

    def add(self, item_id, count: int = 1) -> int:
        if count <= 0:
            return

        item_instance = ItemInstance(item_id)
        if self._game is not None:
            item_instance.bind(self._game)
            if item_instance.item() is None:
                self._game.log.error("Could not find item with resource_id: {}", item_instance.resource_id())
                return 0
            if item_instance.item().stackable():
                for carried_item in self.slots:
                    if carried_item.item().resource_id() == item_id:
                        carried_item.inc(count)
                        return count
                if len(self.slots) < self._max_slots:
                    self.slots.append(ItemStack(item_instance, count))
                    return count
            else:
                count = min(count, self._max_slots - len(self.slots))
                for i in range(count):
                    self.slots.append(ItemStack(item_instance, 1))
                return count
        else:
            for carried_item in self.slots:
                if carried_item.item().resource_id() == item_id:
                    carried_item.inc(count)
                    return count
            self.slots.append(ItemStack(item_instance, count))
            return count

    def _remove_ids(self, ids: 'List[int]'):
        prev = len(self.slots) + 1
        for i in reversed(ids):
            if i != prev:
                self.slots.pop(i)
            i = prev

    def update(self):
        _remove = list()
        for i, stack in enumerate(self.slots):
            if stack.count() <= 0:
                _remove.append(i)
        self._remove_ids(_remove)

    def remove(self, item_id: str, count: int = 1) -> int:
        removed = 0
        left = count
        if self._game is not None:
            remove_ids = list()
            for i in range(len(self.slots)):
                stack = self.slots[i]
                if stack.item().resource_id() == item_id:
                    if stack.count() > left:
                        stack.dec(left)
                        self._remove_ids(remove_ids)
                        removed += left
                        break
                    else:
                        remove_ids.append(i)
                        left -= stack.count()
                        removed += stack.count()
            self._remove_ids(remove_ids)
            return removed
        else:
            for i in range(len(self.slots)):
                stack = self.slots[i]
                if stack.item().resource_id() == item_id:
                    if stack.count() > count:
                        stack.dec(count)
                        return count
                    removed = stack.count()
                    self.slots.pop(i)
                    return removed
            return 0

    def equip(self, slot_id: int, count: int) -> None:
        pass

    def unequip(self, equip_slot: item.EquipSlot) -> None:
        pass

    def weight(self) -> float:
        return self._weight

    def __str__(self) -> str:
        return "\n".join("{} {}".format(stack.count(), stack.item().resource_id()) for stack in self.slots)
