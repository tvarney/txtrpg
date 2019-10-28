
import abc
import os
import os.path
import platform

import yaml

import typing
if typing.TYPE_CHECKING:
    from typing import Any, Dict, IO, Optional, Sequence, Type


class PropertyTypeError(ValueError):
    def __init__(self, property_name: str, value: 'Any') -> None:
        ValueError.__init__(self, "can not set {} property to type {}".format(
            property_name, type(value)
        ))


class Context(object):
    """Context keeps track of the value being unpacked.

    The Context type keeps track of a file name and field name which are used
    to describe the context of an error when unpacking a configuration object.
    A Context must be provided to the unpack function of a configuration
    Property, which uses the context to write errors to. The result of the
    unpack operation should be a bool indicating overall success or failure,
    while the Context can be inspected to check how many errors occurred.

    If the `writer` field is not None, errors will be written to it. This must
    be set to a type which supports the write function (e.g. sys.stderr), and
    each error will result in multiple calls to write. Capturing the output
    can be done by setting the `writer` field to an io.StringIO.
    """

    def __init__(self, file_name: str = "", field_name: str = "") -> None:
        """Create a new Context.

        :param file_name: The filename of the context
        :param field_name: The name of the current field
        """
        self.file = file_name
        self.field = field_name
        self.error_count = 0
        self.writer = None

    def error(self, message: str, *args, **kwargs) -> None:
        if self.writer is not None:
            if self.file != "":
                self.writer.write(self.file)
                self.writer.write(": ")
            if self.field != "":
                self.writer.write(self.field)
                self.writer.write(": ")
            self.writer.write(message.format(*args, **kwargs))
            self.writer.write("\n")
        self.error_count += 1

    def invalid_type(self, expected_type: 'Type', value: 'Any') -> None:
        self.error(
            "invalid type; expected {}, got {} ({})",
            expected_type, value, type(value)
        )


class Property(abc.ABC):
    """Property is the abstract base class of all Configuration properties."""

    def __init__(self):
        abc.ABC.__init__(self)

    @abc.abstractmethod
    def copy(self) -> 'Property':
        raise NotImplementedError

    @abc.abstractmethod
    def unpack(self, value: 'Any', context: 'Context') -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def pack(self) -> 'Any':
        raise NotImplementedError


class PrimitiveProperty(Property, abc.ABC):
    def __init__(self, default: 'Any') -> None:
        Property.__init__(self)
        self._default = default
        self._value = default

    def __repr__(self) -> str:
        return str(self._value)

    def __str__(self) -> str:
        return str(self._value)

    def __bool__(self) -> bool:
        return bool(self._value)

    def __int__(self) -> int:
        return int(self._value)

    def __float__(self) -> float:
        return float(self._value)

    def __eq__(self, other: 'Any') -> bool:
        return self._value == other

    def __ne__(self, other: 'Any') -> bool:
        return self._value != other

    def __lt__(self, other: 'Any') -> bool:
        return self._value < other

    def __le__(self, other: 'Any') -> bool:
        return self._value <= other

    def __gt__(self, other: 'Any') -> bool:
        return self._value > other

    def __ge__(self, other: 'Any') -> bool:
        return self._value >= other

    def pack(self) -> 'Any':
        return self._value


class Boolean(PrimitiveProperty):
    """A boolean property."""

    def __init__(self, default: bool = False) -> None:
        """Create a new Boolean property.

        :param default: The default value of the property
        """
        if type(default) is not bool:
            raise PropertyTypeError("Boolean", default)

        PrimitiveProperty.__init__(self, default)

    @property
    def value(self) -> bool:
        """The value of the property."""
        return self._value

    @value.setter
    def value(self, value: bool) -> None:
        if type(value) is not bool:
            raise PropertyTypeError("Boolean", value)
        self._value = value

    @property
    def default(self) -> bool:
        """The default value of the property."""
        return self._default

    def copy(self) -> 'Boolean':
        """Create a copy of this Boolean Property.

        :returns: A copy of this boolean property
        """
        b = Boolean(self._default)
        b._value = self._value
        return b

    def unpack(self, value: 'Any', context: 'Context') -> bool:
        """Unpack a YAML value into this Boolean property.

        :param value: The value to unpack
        :param context: The context of this unpack operation
        :returns: If the unpack operation succeeded
        """
        if type(value) is not bool:
            context.invalid_type(bool, value)
            return False

        self._value = value
        return True


class Integer(PrimitiveProperty):
    """An integer property."""

    def __init__(self, default: int = 0) -> None:
        """Create a new Integer property.

        :param default: The default value of the property
        """
        if type(default) is not int:
            raise PropertyTypeError("Integer", default)
        PrimitiveProperty.__init__(self, default)

    @property
    def value(self) -> int:
        """The value of the property."""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        if type(value) is not int:
            raise PropertyTypeError("Integer", value)
        self._value = value

    @property
    def default(self) -> int:
        """The default value of the property (read-only)."""
        return self._default

    def copy(self) -> 'Integer':
        """Create a copy of this Integer Property.

        :returns: A copy of this Integer
        """
        i = Integer(self._default)
        i._value = self._value
        return i

    def unpack(self, value: 'Any', context: 'Context') -> bool:
        """Unpack a YAML value into this Integer Property.

        The value being unpacked must be an int, otherwise an error is written
        to the context and False is returned.

        :param value: The value to unpack
        :param context: The context of this unpack operation
        :returns: If the unpack operation succeeded
        """
        if type(value) is not int:
            context.invalid_type(int, value)
            return False
        self._value = value
        return True


class Float(PrimitiveProperty):
    """A Float property."""

    def __init__(self, default: float = 0.0) -> None:
        """Create a new Float property.

        :param default: The default value of the property
        """
        if type(default) is not float:
            raise PropertyTypeError("Float", default)
        PrimitiveProperty.__init__(self, default)

    @property
    def value(self) -> float:
        """The value of the property."""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        if type(value) is not float:
            raise PropertyTypeError("Float", value)
        self._value = value

    @property
    def default(self) -> int:
        """The default value of the property (read-only)."""
        return self._default

    def copy(self) -> 'Float':
        """Create a copy of this Float Property.

        :returns: A copy of this Float
        """
        f = Float(self._default)
        f._value = self._value
        return f

    def unpack(self, value: 'Any', context: 'Context') -> bool:
        """Unpack a YAML value into this Float Property.

        The value being unpacked must be either a float or an int, otherwise
        an error is written to the context and False is returned.

        :param value: The value to unpack
        :param context: The context of this unpack operation
        :returns: If the unpack operation succeeded
        """
        if type(value) is int or type(value) is float:
            self._value = float(value)
            return True
        context.invalid_type(float, value)
        return False


class String(PrimitiveProperty):
    def __init__(self, default: str = "", allow_empty: bool = True,
                 strip: bool = False) -> None:
        if type(default) is not str:
            raise PropertyTypeError("String", default)
        if strip:
            default = default.strip()
        if not allow_empty and default == "":
            raise ValueError("may not be empty")

        PrimitiveProperty.__init__(self, default)
        self._allow_empty = allow_empty
        self._strip = strip

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        if type(value) is not str:
            raise PropertyTypeError("String", value)
        if self._strip:
            value = value.strip()
        if not self._allow_empty and value == "":
            raise ValueError("may not be empty")
        self._value = value

    @property
    def default(self) -> str:
        return self._default

    def copy(self) -> 'String':
        """Create a copy of this String Property.

        :returns: A copy of this String
        """
        s = String(self._default, self._allow_empty, self._strip)
        s._value = self._value
        return s

    def unpack(self, value: 'Any', context: 'Context') -> bool:
        """Unpack a YAML value into this String Property.

        The value being unpacked must be a str, otherwise an error is written
        to the context and False is returned.

        :param value: The value to unpack
        :param context: The context of this unpack operation
        :returns: If the unpack operation succeeded
        """
        if type(value) is not str:
            context.invalid_type(str, value)
            return False
        if self._strip:
            value = value.strip()
        if value == "" and not self._allow_empty:
            context.error("may not be empty")
            return False
        self._value = value
        return True


class EnumValueError(ValueError):
    def __init__(self, value: str) -> None:
        ValueError.__init__(
            self, "{} is not an allowed enum value".format(repr(value))
        )


class Enum(PrimitiveProperty):
    def __init__(self, allowed: 'Sequence[str]',
                 default: 'Optional[str]' = None) -> None:
        if len(allowed) == 0:
            raise ValueError("Enum type requires at least one value")

        default = default if default is not None else allowed[0]
        if default not in allowed:
            raise EnumValueError(default)
        PrimitiveProperty.__init__(self, default)
        self._allowed = allowed

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        if type(value) is not str:
            raise PropertyTypeError("Enum", value)
        if value not in self._allowed:
            raise EnumValueError(value)
        self._value = value

    @property
    def default(self) -> str:
        return self._default

    def copy(self) -> 'Enum':
        """Create a copy of this Enum Property.

        :returns: A copy of this Enum
        """
        e = Enum(self._allowed, self._default)
        e._value = self._value
        return e

    def unpack(self, value: 'Any', context: 'Context') -> bool:
        """Unpack a YAML value into this Enum Property.

        The value being unpacked must be a str and be present in the list of
        allowed enum values.

        :param value: The value to unpack
        :param context: The context of this unpack operation
        :returns: If the unpack operation succeeded
        """
        if type(value) is not str:
            context.invalid_type(str, value)
            return False
        if value not in self._allowed:
            context.error(
                "{} not an allowed enum value, must be one of {}",
                repr(value), repr(self._allowed)
            )
            return False
        self._value = value
        return True


class Map(Property):
    def __init__(self, values: 'Dict[str, Property]') -> None:
        Property.__init__(self)
        object.__setattr__(self, '_values', values)

    def copy(self) -> 'Map':
        m = Map(dict())
        for key, value in self._values.items():
            m.parameters[key] = value.copy()
        return m

    def unpack(self, value: 'Any', context: 'Context') -> bool:
        if value is None:
            return True
        if type(value) is not dict:
            raise PropertyTypeError("Map", value)

        good = True
        base_field = context.field
        field = base_field if base_field == "" else base_field + '.'
        for key, value in value.items():
            context.field = field + key
            child = self._values.get(key, None)
            if child is None:
                good = False
                context.error("invalid key")
                continue
            good &= child.unpack(value, context)
        return good

    def pack(self) -> 'Any':
        serialized = dict()
        for key, value in self._values.items():
            serialized[key] = value.pack()
        return serialized

    @property
    def parameters(self) -> 'Dict[str, Property]':
        return self._values

    def __getitem__(self, key: str) -> 'Property':
        return self._values[key]

    def __setitem__(self, key: str, value: 'Any') -> None:
        self._values[key].value = value

    def __getattr__(self, key: str) -> 'Property':
        return self._values[key]

    def __setattr__(self, key: str, value: 'Any') -> None:
        if key in self._values:
            self.__dict__['_values'][key].value = value
        else:
            self.__dict__[key] = value


class Config(Map):
    @staticmethod
    def folder() -> str:
        """Get the folder where configuration files should be read from.

        :return: The folder for configuration files
        """
        if platform.win32_ver()[0] != '':
            return os.path.expandvars("%APPDATA%/txtrpg")
        if platform.mac_ver()[0] != '':
            return os.path.expanduser("~/Library/Application Support/txtrpg")
        return os.path.expanduser("~/.local/share/txtrpg")

    def load(self, filename: str, fp: 'Optional[IO]' = None,
             ctx: 'Optional[Context]' = None) -> bool:
        ctx = ctx if ctx is not None else Context(filename)
        if fp is not None:
            return self._load(filename, fp, ctx)
        else:
            with open(filename, "rb") as fp:
                return self._load(filename, fp, ctx)

    def _load(self, filename: str, fp: 'IO', ctx: 'Context') -> bool:
        ctx.file = filename
        ctx.field = ""
        data: dict
        try:
            data = yaml.safe_load(fp)
        except Exception as e:
            ctx.error("{}: {}", type(e).__name__, e)
            return False
        return self.unpack(data, ctx)

    def save(self, filename: str, fp: 'Optional[IO]' = None) -> None:
        data = self.pack()
        if fp is None:
            with open(filename, "w") as fp:
                yaml.dump(data, fp)
        else:
            yaml.dump(data, fp)
