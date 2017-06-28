
from rpg.data import resource as r

import typing
if typing.TYPE_CHECKING:
    from typing import Optional


class Resources(object):
    def __init__(self):
        self._map = [dict() for _ in range(r.ResourceType.COUNT)]

    def add(self, resource: 'r.Resource'):
        """
        Add a resource to the current collection of resources
        :param resource: The resource to add
        """
        type_id = resource.type_id()
        resource_id = resource.resource_id()

        collection = self._map[type_id]
        if resource_id in collection:
            raise KeyError("Resource '{}' already defined in {} collection".format(resource_id, type_id.name))

        collection[resource_id] = resource

    def get(self, type_id: 'r.ResourceType', resource_id: str) -> 'Optional[r.Resource]':
        """
        Get a resource of the given type with the given resource_id
        :param type_id: The ResourceType of the resource to look up
        :param resource_id: The string id of the resource to get
        :return: The resource if found, otherwise None
        """
        return self._map[type_id].get(resource_id, None)
