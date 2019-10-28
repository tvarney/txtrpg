"""Defines an object which manages resources defined from packages."""

from rpg.data import resource as r

import typing
if typing.TYPE_CHECKING:
    from rpg.data.resource import Resource, ResourceType
    from typing import Dict, List, Optional

_fmtReplaceError = "cannot replace {} {}; master {} not in allowed list {}"


class ResourceAlreadyDefinedError(KeyError):
    def __init__(self, resource_id: str, name: str) -> None:
        KeyError("resource '{}' already defined in {} collection".format(
            resource_id, name
        ))


class Resources(object):
    """Collection which manages resources loaded from packages, as well as
    looking resources up by unique id and type.
    """

    def __init__(self) -> None:
        """Initialize this Resources collection.

        This function creates ResourceType.COUNT dictionaries in a
        list which may be indexed by a ResourceType value to get the dictionary
        of that type of resource.
        """
        self._map: 'List[Dict[str, Resource]]' = [
            dict() for _ in range(r.ResourceType.COUNT)
        ]
        self._package_name: 'Optional[str]' = None

    def add(self, item: 'r.Resource') -> None:
        """Add a resource to the current collection of resources.

        :param item: The resource to add
        """
        type_id = item.type_id()
        resource_id = item.resource_id()

        collection = self._map[type_id]
        if resource_id in collection:
            raise ResourceAlreadyDefinedError(resource_id, type_id.name)

        collection[resource_id] = item

    def get(self, type_id: 'r.ResourceType',
            resource_id: str) -> 'Optional[r.Resource]':
        """Get a resource of the given type with the given resource_id.

        :param type_id: The ResourceType of the resource to look up
        :param resource_id: The string id of the resource to get
        :return: The resource if found, otherwise None
        """
        return self._map[type_id].get(resource_id, None)

    def set_package(self, package_name: str):
        """Set the name of the controlling package on this resources
        collection.

        :param package_name: The name of the package for which
        """
        self._package_name = package_name
        for sub_map in self._map:
            for key, value in sub_map.items():
                value._package = package_name

    def enumerate(self, resource_type: 'Optional[ResourceType]' = None):
        """Create a generator which returns each item in this collection.

        :return: A tuple of (ResourceType, str, Resource) for each item in this
                 collection.
        """
        if resource_type is not None:
            for key, value in self._map[resource_type].items():
                yield value.type_id(), key, value
        else:
            for collection in self._map:
                for key, value in collection.items():
                    yield value.type_id(), key, value

    def count(self, t_id: 'Optional[ResourceType]' = None) -> int:
        """Get the count of the given resource type in this collection.

        If the t_id parameter is None (the default), this method will return
        the total count of all resource types in this collection.

        :param t_id: The ResourceType to count, or None for every ResourceType
        :return: The number of the given resource type in this collection
        """
        if t_id is None:
            total = 0
            for collection in self._map:
                total += len(collection)
            return total
        else:
            return len(self._map[t_id])

    def merge(self, other: 'Resources',
              masters: 'Optional[List[str]]' = None) -> 'Optional[str]':
        """Add all resources defined in the other Resources collection to this
        collection.

        :param other: The other Resources collection to take all objects from
        :param masters: A list of master packages from which resources may be
                        replaced
        :return: None if no errors happen during the merge, otherwise a string
                 with a description of the errors
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
                    _error_str += _fmtReplaceError.format(
                        t_id.name, key, old_pkg, masters
                    )
            else:
                self._map[t_id][key] = value

        _error_str = _error_str.strip()
        return _error_str if _error_str != "" else None

    def clear(self):
        """Remove all resources from this collection."""
        for collection in self._map:
            collection.clear()
