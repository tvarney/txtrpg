
import typing
if typing.TYPE_CHECKING:
    from typing import Dict, Optional


class StringMap(object):
    Current: 'StringMap'
    Default: 'StringMap'

    def __init__(self, **kwargs) -> None:
        default_map = StringMap.Default
        if "default" in kwargs:
            default_map = kwargs.pop("default")

        self._default: 'Optional[StringMap]' = default_map
        self._strings: 'Dict[str, str]' = dict()

    def get(self, key: str,
            default: 'Optional[str]' = None) -> 'Optional[str]':
        """Get a value from the StringMap

        :param key: The main ID of the string
        :param default: A value to return if the given key/sub_key pair
                        is not defined
        :return: The value associated with the key and sub_key, or the
                 default
        """
        value = self._strings.get(key, None)
        if value is None and self._default is not None:
            value = self._default.get(key, default)
        return value if value is not None else default

    def set(self, key: str, value: str) -> None:
        self._strings[key] = value


StringMap.Default = StringMap()
StringMap.Current = StringMap.Default
