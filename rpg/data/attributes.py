
import abc
import typing
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, Sequence, Tuple

AttributeData = typing.Union[
    int,
    typing.Tuple[int, int],
]


class Attribute(object):
    """Class which tracks an attribute level and current value.

    Attributes are a primary or secondary statistic about an Actor which
    characterizes them in some manner. Primary attributes are as follows:
        Strength:     How strong the Actor is. Used for health, damage and how
                      much an actor may carry
        Dexterity:    The Actors fine motor skills. Used for hit-chance
        Constitution: How hardy the Actor is. Used to calculate stamina and
                      health
        Agility:      How quick and nimble the Actor is. Used to determine turn
                      order, actions per turn, and stamina
        Intelligence: How smart the Actor is. Used for Spell Damage and mana
        Wisdom:       How wise the Actor is. Used for mana and Spell Resistance
        Charisma:     How persuasive the character is. Used for persuade
                      checks, shop buy and sell prices
        Luck:         How lucky the Actor is. Small benefits to many parts of
                      the game

    Secondary attributes are implemented as a sub-class of the Attribute class
    (Stat), and are as follows:
        Health:  Hit Points, or how much damage an Actor can take before dieing
        Stamina: How much exertion the Actor can take before collapsing
        Mana:    Magical energy, used for casting spells

    For more on Secondary attributes, see the rpg.attributes.SecondaryAttribute
    class.

    The default value for the level of Primary Attributes is 10. This
    represents the average value that a human would have. As such, an Actor
    with an intelligence of 10 is averagely smart for a human, an actor with an
    Agility score of 10 is about as quick as the average human, etc.
    """

    ColorNormal = "black"
    ColorAbove = "green"
    ColorBelow = "red"

    def __init__(self, level: int = 10, value: 'Optional[int]' = None) -> None:
        """Create a new Attribute instance with the given level and value.

        If the value is not given, it is assumed to be the same as the level.

        :param level: The level of the attribute
        :param value: The current value of the attribute
        """
        self._level = level
        self._value = value if value is not None else level

    @property
    def color(self) -> str:
        """Get the color to display this attribute in.

        :return: A tkinter color string
        """
        if self._level == self._value:
            return Attribute.ColorNormal
        if self._value > self._level:
            return Attribute.ColorAbove
        return Attribute.ColorBelow

    @property
    def short_string(self) -> str:
        return self.string(True)

    @property
    def long_string(self) -> str:
        return self.string(False)

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, new_value: int) -> None:
        self.set_level(new_value)

    @property
    def actual_level(self) -> int:
        return self._level

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        self.set_value(new_value)

    def load(self, data: 'Optional[AttributeData]') -> None:
        if data is None:
            return

        if type(data) is tuple:
            if len(data) != 2:
                raise ValueError("too few elements in Attribute data tuple")
            self.level = data[0]
            self.value = data[1]
        elif type(data) is int:
            self.level = data
        else:
            raise ValueError(
                "invalid Attribute data type {}".format(type(data))
            )

    def string(self, short: bool = False) -> str:
        """Get a string representation of this Attribute.

        :param short: If the string should be the short version
        :return: A string representing the value of this attribute
        """
        if short or self._level == self._value:
            return str(self._value)
        return "{} [{:+}]".format(self._value, self._value - self._level)

    def set_level(self, new_value: int) -> None:
        difference = new_value - self._level
        if difference < 0:
            difference = max(-self._level, difference)
        self._level += difference
        self._value += difference

    def set_value(self, new_value: int) -> None:
        self._value = new_value

    def __str__(self) -> str:
        """Get the string representation of this Attribute.

        This method calls the self.string(False) method

        :return: The shortened string value of this Attribute
        """
        return self.string(False)

    def __repr__(self) -> str:
        """Get a string representation of this attribute.

        :return: A string representation of this attribute which may be
                 evaluated to create a copy of this Attribute
        """
        return "Attribute({}, {})".format(self._level, self._value)


class AttributeChangeListener(abc.ABC):
    @abc.abstractmethod
    def update(self, attr: 'Attribute', msg: str) -> None:
        raise NotImplementedError()


class PrimaryAttribute(Attribute):
    def __init__(self, level: int = 10, value: 'Optional[int]' = None) -> None:
        Attribute.__init__(self, level, value)
        self._listeners = list()

    def add(self, listener: 'AttributeChangeListener') -> None:
        self._listeners.append(listener)

    def notify(self, notify_msg: str) -> None:
        for listener in self._listeners:
            listener.update(self, notify_msg)

    def set_level(self, new_value: int) -> None:
        Attribute.set_level(self, new_value)
        self.notify("level")

    def set_value(self, new_value: int) -> None:
        Attribute.set_value(self, new_value)
        self.notify("value")


class SecondaryAttribute(Attribute, AttributeChangeListener):
    """A Secondary Attribute.

    For a thorough explanation of Attributes and Stats, see
    rpg.attributes.Attribute.

    A Stat is a secondary Attribute. These Attributes tend to be both higher
    valued than Primary Attributes (by roughly 10x), and change value
    frequently. The default value of a Stat is thus 100/100

    Stat instances are used to track health, stamina, and mana.
    """

    ThresholdGood = 1.0
    ThresholdOkay = 0.75
    ThresholdPoor = 0.5
    ThresholdHurt = 0.25

    ColorBuffed = "cyan"
    ColorGood = "green"
    ColorOkay = "yellow"
    ColorPoor = "orange"
    ColorHurt = "red"

    def __init__(
        self, level: int = 0,
        value: 'Optional[int]' = None,
        tracked: 'Optional[Sequence[Tuple[int, PrimaryAttribute]]]' = None
    ) -> None:
        """Create a new Stat instance.

        If the value argument is not given or is None, then the value is
        assumed to be equal to the level.

        :param level: The level of the Stat
        :param value: The current value of the Stat
        """
        Attribute.__init__(self, level, value)
        self._tracked = tracked
        self._effective = level
        for amount, attribute in self._tracked:
            attribute.add(self)
            self._effective += attribute.level * amount
        if value is None:
            self._value = self._effective

    def update(self, attr: 'Attribute', msg: str) -> None:
        """Update callback used to handle changes in a tracked
        attribute.

        :param attr: The attribute which changed
        :param msg: Indicator of what changed.
        """
        if msg != 'level':
            return

        # Assign to the property so the value tracks correctly
        new_value = self._level + sum(
            amount * attribute.level for amount, attribute in self._tracked
        )
        difference = new_value - self._effective
        self._effective = new_value
        if difference > 0:
            self._value += difference
        elif self._value > self._effective:
            self._value = self._effective

    def string(self, short: bool = False) -> str:
        """Get a string representation of this SecondaryAttribute.

        :param short: If the string returned should be shortened if level
                      equals value
        :return: A string representing this Stat
        """
        if short and self._value == self._effective:
            return str(self._effective)
        return "{}/{}".format(self._value, self._effective)

    @property
    def level(self) -> int:
        return self._effective

    @level.setter
    def level(self, new_value: int) -> None:
        difference = new_value - self._effective
        if difference < 0:
            difference = max(-self._level, difference)

        self._level += difference
        self._effective += difference
        if difference > 0 or self._value > self._effective:
            self._value += difference

    @property
    def color(self) -> str:
        """Get a tkinter color string used to represent the status of this
        SecondaryAttribute.

        The color string returned is controlled by class variables of the Stat
        class.
        :return: A tkinter color string
        """
        ratio = float(self._value) / float(self._level)
        if ratio > SecondaryAttribute.ThresholdGood:
            return SecondaryAttribute.ColorBuffed
        if ratio > SecondaryAttribute.ThresholdOkay:
            return SecondaryAttribute.ColorGood
        if ratio > SecondaryAttribute.ThresholdPoor:
            return SecondaryAttribute.ColorOkay
        if ratio > SecondaryAttribute.ThresholdHurt:
            return SecondaryAttribute.ColorPoor
        return SecondaryAttribute.ColorHurt

    def __repr__(self) -> str:
        """Get a string representation of this Stat which can be evaluated to a
        valid Stat instance.

        :return: A string representation of this Stat
        """
        return "Stat({}, {})".format(self._level, self._value)


class AttributeList(object):
    """A list of Attributes for an Actor.

    This class tracks each Attribute that every Actor needs.
    """

    @staticmethod
    def load(data: 'Dict[str, AttributeData]') -> 'AttributeList':
        al = AttributeList()
        al.strength.load(data.pop("str", None))
        al.dexterity.load(data.pop("dex", None))
        al.agility.load(data.pop("agl", None))
        al.constitution.load(data.pop("con", None))
        al.intelligence.load(data.pop("int", None))
        al.wisdom.load(data.pop("wis", None))
        al.charisma.load(data.pop("cha", None))
        al.luck.load(data.pop("lck", None))
        al.health.load(data.pop("hp", None))
        al.mana.load(data.pop("mp", None))
        al.stamina.load(data.pop("st", None))
        return al

    def __init__(self) -> None:
        self.strength = PrimaryAttribute()
        self.dexterity = PrimaryAttribute()
        self.agility = PrimaryAttribute()
        self.constitution = PrimaryAttribute()
        self.intelligence = PrimaryAttribute()
        self.wisdom = PrimaryAttribute()
        self.charisma = PrimaryAttribute()
        self.luck = PrimaryAttribute()

        self.health = SecondaryAttribute(
            tracked=(
                (3, self.strength),
                (7, self.constitution),
            )
        )
        self.mana = SecondaryAttribute(
            tracked=(
                (3, self.wisdom),
                (7, self.intelligence),
            )
        )
        self.stamina = SecondaryAttribute(
            tracked=(
                (6, self.constitution),
                (4, self.agility)
            )
        )
