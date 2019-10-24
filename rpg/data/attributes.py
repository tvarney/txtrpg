
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple, Union


class Attribute(object):

    """Class which tracks an attribute level and current value.

    Attributes are a primary or secondary statistic about an Actor which characterizes them in some manner. Primary
    attributes are as follows:
        Strength: How strong the Actor is. Used for health, damage and how much an actor may carry
        Dexterity: The Actors fine motor skills. Used for hit-chance
        Constitution: How hardy the Actor is. Used to calculate stamina and health
        Agility: How quick and nimble the Actor is. Used to determine turn order, actions per turn, and stamina
        Intelligence: How smart the Actor is. Used for Spell Damage and mana
        Wisdom: How wise the Actor is. Used for mana and Spell Resistance
        Charisma: How persuasive the character is. Used for persuade checks, shop buy and sell prices
        Luck: How lucky the Actor is. Small benefits to many parts of the game

    Secondary attributes are implemented as a sub-class of the Attribute class (Stat), and are as follows:
        Health: Hit Points, or how much damage an Actor can take before collapsing
        Stamina: How much exertion the Actor can take before collapsing
        Mana: Magical energy, used for casting spells

    For more on Secondary attributes, see the rpg.attributes.Stat class

    The default value for the level of Primary Attributes is 10. This represents the average value that a human would
    have. As such, an Actor with an intelligence of 10 is averagely smart for a human, an actor with an Agility score of
    10 is about as quick as the average human, etc.

    """

    ColorNormal = "black"
    ColorAbove = "green"
    ColorBelow = "red"

    def __init__(self, level: int=10, value: 'Optional[int]'=None):
        """Create a new Attribute instance with the given level and value.

        If the value is not given, it is assumed to be the same as the level.

        :param level: The level of the attribute
        :param value: The current value of the attribute
        """
        self._level = level
        self._value = value if value is not None else level

    def color(self) -> str:
        """Get the color to display this attribute in.

        :return: A tkinter color string
        """
        if self._level == self._value:
            return Attribute.ColorNormal
        if self._value > self._level:
            return Attribute.ColorAbove
        return Attribute.ColorBelow

    def string(self, short: bool=False) -> str:
        """Get a string representation of this Attribute.

        :param short: If the string should be the short version
        :return: A string representing the value of this attribute
        """
        if short or self._level == self._value:
            return str(self._value)
        return "{} [{:+}]".format(self._value, self._value - self._level)

    def level(self) -> int:
        """Get the level of this attribute.

        :return: The level of this attribute
        """
        return self._level

    def value(self) -> int:
        """Get the value of this attribute.

        :return: The value of this attribute
        """
        return self._value

    def level_up(self, increment: int=1):
        """Increase the level of this attribute.

        This method will also increase the value of the Attribute by the same amount

        :param increment: The amount to increase the level of this attribute by
        """
        self._level += increment
        self._value += increment

    def level_down(self, decrement: int=1):
        """Decrease the level of this attribute.

        This method will also decrease the value of the Attribute by the same amount

        :param decrement: The amount to decrease the level of this attribute
        """
        self._level -= decrement
        self._value -= decrement

    def increase(self, increment: int=1):
        """Increase the value of this attribute.

        :param increment: The amount to increase the value of this attribute by
        """
        self._value += increment

    def decrease(self, decrement: int=1):
        """Decrease the value of this attribute.

        :param decrement: The amount to decrease the value of this attribute by
        """
        self._value -= decrement

    def __str__(self) -> str:
        """Get the string representation of this Attribute.

        This method calls the self.string(False) method

        :return: The shortened string value of this Attribute
        """
        return self.string(False)

    def __repr__(self) -> str:
        """Get a string representation of this attribute.

        :return: A string representation of this attribute which may be evaluated to create a copy of this Attribute
        """
        return "Attribute({}, {})".format(self._level, self._value)


class Stat(Attribute):

    """A Secondary Attribute.

    For a thorough explanation of Attributes and Stats, see rpg.attributes.Attribute.

    A Stat is a secondary Attribute. These Attributes tend to be both higher valued than Primary Attributes (by roughly
    10x), and change value frequently. The default value of a Stat is thus 100/100

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

    def __init__(self, level: int=100, value: 'Optional[int]'=None):
        """Create a new Stat instance.

        If the value argument is not given or is None, then the value is assumed to be equal to the level

        :param level: The level of the Stat
        :param value:
        """
        Attribute.__init__(self, level, value)

    def color(self) -> str:
        """Get a tkinter color string used to represent the status of this Stat.

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
        """Get a string representation of this Stat.

        :param short: If the string returned should be shortened if level == value
        :return: A string representing this Stat
        """
        if short and self._value == self._level:
            return str(self._level)
        return "{}/{}".format(self._value, self._level)

    def __repr__(self) -> str:
        """Get a string representation of this Stat which can be evaluated to a valid Stat instance.

        :return: A string representation of this Stat
        """
        return "Stat({}, {})".format(self._level, self._value)


class AttributeList(object):

    """A list of Attributes for an Actor.

    This class tracks each Attribute that every Actor needs.
    """

    @staticmethod
    def _coerce(value: 'Union[int, Attribute, Tuple[int, int]]', klass):
        if type(value) is tuple:
            return klass(value[0], value[1]) if len(value) > 1 else klass(value[0])
        elif type(value) is int:
            return klass(value)
        else:
            return value

    @staticmethod
    def default_health(attr_list: 'AttributeList') -> int:
        """Get the default level for the Health attribute from an AttributeList

        :param attr_list: The AttributeList instance to calculate default health level from
        :return: The default level of health an actor with this AttributeList would have
        """
        return attr_list.strength.level() * 7 + attr_list.constitution.level() * 3

    @staticmethod
    def default_mana(attr_list: 'AttributeList'):
        """Get the default level for the Mana attribute from an AttributeList

        :param attr_list: The AttributeList instance to calculate default mana from
        :return: The default level of mana an actor with this AttributeList would have
        """
        return attr_list.intelligence.level() * 4 + attr_list.wisdom.level() * 6

    @staticmethod
    def default_stamina(attr_list: 'AttributeList'):
        """Get the default level for the Stamina attribute from an AttributeList

        :param attr_list: The AttributeList instance to calculate default stamina from
        :return: The default level of stamina an actor with this AttributeList would have
        """
        return attr_list.constitution.level() * 7 + attr_list.agility.level() * 3

    def __init__(self, **kwargs):
        """Create a new AttributeList instance.

        Keyword arguments which are accepted are:
            health: Union[int, Stat, Tuple[int, int]]
            stamina: Union[int, Stat, Tuple[int, int]]
            mana: Union[int, Stat, Tuple[int, int]]

            str: Union[int, Attribute, Tuple[int, int]]
            dex: Union[int, Attribute, Tuple[int, int]]
            con: Union[int, Attribute, Tuple[int, int]]
            agl: Union[int, Attribute, Tuple[int, int]]
            int: Union[int, Attribute, Tuple[int, int]]
            wis: Union[int, Attribute, Tuple[int, int]]
            cha: Union[int, Attribute, Tuple[int, int]]
            lck: Union[int, Attribute, Tuple[int, int]]

        :param kwargs: keyword arguments for initial attribute values
        """

        self.strength = AttributeList._coerce(kwargs.get("str", Attribute(10)), Attribute)
        self.dexterity = AttributeList._coerce(kwargs.get("dex", Attribute(10)), Attribute)
        self.constitution = AttributeList._coerce(kwargs.get("con", Attribute(10)), Attribute)
        self.agility = AttributeList._coerce(kwargs.get("agl", Attribute(10)), Attribute)
        self.intelligence = AttributeList._coerce(kwargs.get("int", Attribute(10)), Attribute)
        self.wisdom = AttributeList._coerce(kwargs.get("wis", Attribute(10)), Attribute)
        self.charisma = AttributeList._coerce(kwargs.get("cha", Attribute(10)), Attribute)
        self.luck = AttributeList._coerce(kwargs.get("lck", Attribute(10)), Attribute)

        self.health = AttributeList._coerce(kwargs.get("health", Stat(AttributeList.default_health(self))), Stat)
        self.mana = AttributeList._coerce(kwargs.get("mana", Stat(AttributeList.default_mana(self))), Stat)
        self.stamina = AttributeList._coerce(kwargs.get("stamina", Stat(AttributeList.default_stamina(self))), Stat)
        self.energy = AttributeList._coerce(kwargs.get("energy", Stat(100)), Stat)

