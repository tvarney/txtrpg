
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, Union


class Attribute(object):
    ColorNormal = "black"
    ColorAbove = "green"
    ColorBelow = "red"

    def __init__(self, level: int, value: 'Optional[int]'=None):
        self._level = level
        self._value = value if value is not None else level

    def color(self) -> str:
        """
        Get the color to display this attribute in
        :return: A tkinter color string
        """
        if self._level == self._value:
            return Attribute.ColorNormal
        if self._value > self._level:
            return Attribute.ColorAbove
        return Attribute.ColorBelow

    def string(self, short: bool=False) -> str:
        """
        Get a string representation of this Attribute
        :param short: If the string should be the short version
        :return: A string representing the value of this attribute
        """
        if short or self._level == self._value:
            return str(self._value)
        return "{} [{:+}]".format(self._value, self._value - self._level)

    def level(self) -> int:
        """
        Get the level of this attribute
        :return: The level of this attribute
        """
        return self._level

    def value(self) -> int:
        """
        Get the value of this attribute
        :return: The value of this attributell
        """
        return self._value

    def level_up(self, increment: int=1):
        """
        Increase the level of this attribute (this also increases the value by the same amount)
        :param increment: The amount to increase the level of this attribute by
        """
        self._level += increment
        self._value += increment

    def level_down(self, decrement: int=1):
        """
        Decrease the level of this attribute (this also decreases the value by the same amount)
        :param decrement: The amount to decrease the level of this attribute
        """
        self._level -= decrement
        self._value -= decrement

    def increase(self, increment: int=1):
        """
        Increase the value of this attribute. This does not change the level of the attribute
        :param increment: The amount to increase the value of this attribute by
        """
        self._value += increment

    def decrease(self, decrement: int=1):
        """
        Descrease the value of this attribute. This does not change the level of the attribute
        :param decrement: The amount to decrease the value of this attribute by
        :return:
        """
        self._value -= decrement

    def __str__(self) -> str:
        return self.string(False)

    def __repr__(self) -> str:
        return "Attribute({}, {})".format(self._level, self._value)


class Stat(Attribute):
    ThresholdGood = 1.0
    ThresholdOkay = 0.75
    ThresholdPoor = 0.5
    ThresholdHurt = 0.25

    ColorBuffed = "cyan"
    ColorGood = "green"
    ColorOkay = "yellow"
    ColorPoor = "orange"
    ColorHurt = "red"

    def __init__(self, level: int, value: 'Optional[int]'=None):
        Attribute.__init__(self, level, value)

    def color(self) -> str:
        """
        Get a tkinter color string used to represent the status of this Stat

        The color string returned is controlled by class variables of the Stat class.
        :return: A tkinter color string
        """
        ratio = float(self._value) / float(self._level)
        if ratio > Stat.ThresholdGood:
            return Stat.ColorBuffed
        if ratio > Stat.ThresholdOkay:
            return Stat.ColorGood
        if ratio > Stat.ThresholdPoor:
            return Stat.ColorOkay
        if ratio > Stat.ThresholdHurt:
            return Stat.ColorPoor
        return Stat.ColorHurt

    def string(self, short: bool=False) -> str:
        """
        Get a string value of this Stat
        :param short: If the string returned should be shortened if level == value
        :return: A string representing this Stat
        """
        if short and self._value == self._level:
            return str(self._level)
        return "{}/{}".format(self._value, self._level)

    def __repr__(self) -> str:
        return "Stat({}, {})".format(self._level, self._value)


class AttributeList(object):
    @staticmethod
    def _coerce(value: 'Union[int, Attribute, Tuple[int, int]]', klass):
        if type(value) is tuple:
            return klass(value[0], value[1]) if len(value) > 1 else klass(value[0])
        elif type(value) is int:
            return klass(value)
        else:
            return value

    def __init__(self, **kwargs):
        self.health = AttributeList._coerce(kwargs.get("health", Stat(100)), Stat)
        self.mana = AttributeList._coerce(kwargs.get("mana", Stat(100)), Stat)
        self.stamina = AttributeList._coerce(kwargs.get("stamina", Stat(100)), Stat)
        self.energy = AttributeList._coerce(kwargs.get("energy", Stat(100)), Stat)

        self.strength = AttributeList._coerce(kwargs.get("str", Attribute(10)), Attribute)
        self.dexterity = AttributeList._coerce(kwargs.get("dex", Attribute(10)), Attribute)
        self.constitution = AttributeList._coerce(kwargs.get("con", Attribute(10)), Attribute)
        self.agility = AttributeList._coerce(kwargs.get("agl", Attribute(10)), Attribute)
        self.intelligence = AttributeList._coerce(kwargs.get("int", Attribute(10)), Attribute)
        self.wisdom = AttributeList._coerce(kwargs.get("wis", Attribute(10)), Attribute)
        self.charisma = AttributeList._coerce(kwargs.get("cha", Attribute(10)), Attribute)
        self.luck = AttributeList._coerce(kwargs.get("lck", Attribute(10)), Attribute)
