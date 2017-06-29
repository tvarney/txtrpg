
from rpg.data import resource as r

import typing
if typing.TYPE_CHECKING:
    from rpg.data import resource
    from typing import Dict, List, Optional


class Resources(object):
    def __init__(self):
        self._map = [dict() for _ in range(r.ResourceType.COUNT)]  # type: List[Dict[str, resource.Resource]]
        self._package_name = None  # type: Optional[str]

    def add(self, item: 'r.Resource'):
        """
        Add a resource to the current collection of resources
        :param item: The resource to add
        """
        type_id = item.type_id()
        resource_id = item.resource_id()

        collection = self._map[type_id]
        if resource_id in collection:
            raise KeyError("Resource '{}' already defined in {} collection".format(resource_id, type_id.name))

        collection[resource_id] = item

    def get(self, type_id: 'r.ResourceType', resource_id: str) -> 'Optional[r.Resource]':
        """
        Get a resource of the given type with the given resource_id
        :param type_id: The ResourceType of the resource to look up
        :param resource_id: The string id of the resource to get
        :return: The resource if found, otherwise None
        """
        return self._map[type_id].get(resource_id, None)

    def set_package(self, package_name: str):
        """
        Set the name of the controlling package on this resources collection
        :param package_name: The name of the package for which
        :return:
        """
        self._package_name = package_name
        for sub_map in self._map:
            for key, value in sub_map.items():
                value._package = package_name

    def enumerate(self):
        """
        Create a generator which returns each item in this collection
        :return: A tuple of (ResourceType, str, Resource) for each item in this collection
        """
        for collection in self._map:
            for key, value in collection.items():
                type_id = value.type_id()
                yield type_id, key, value

    def count(self, t_id: 'Optional[resource.ResourceType]'=None) -> int:
        """
        Get the count of the given resource type in this collection

        If the t_id parameter is None (the default), this method will return the total count of all resource types in
        this collection.
        :param t_id: The resource type to count, or None for every resource type
        :return: The number of the given resource type in this collection
        """
        if t_id is None:
            total = 0
            for collection in self._map:
                total += len(collection)
            return total
        else:
            return len(self._map[t_id])

    def merge(self, other: 'Resources', masters: 'Optional[List[str]]'=None) -> 'Optional[str]':
        """
        Add all resources defined in the other Resources collection to this collection
        :param other: The other Resources collection to take all objects from
        :param masters: A list of master packages from which resources may be replaced
        :return: None if no errors happen during the merge, otherwise a string with a description of the errors
        """
        if masters is None:
            masters = list()  # type: List[str]

        _error_str = ""

        for t_id, key, value in other.enumerate():
            old_obj = self._map[t_id].get(key, None)
            if old_obj is not None:
                old_pkg = old_obj.package()
                if old_pkg in masters:
                    self._map[t_id][key] = value
                else:
                    _fmt_str = "Can not replace {} {}; master package {} not in allowed list {}\n"
                    _error_str += _fmt_str.format(t_id.name, key, old_pkg, masters)
            else:
                self._map[t_id][key] = value

        _error_str = _error_str.strip()
        return _error_str if _error_str != "" else None

    def clear(self):
        """
        Remove all resources from this collection
        """
        for collection in self._map:
            collection.clear()
