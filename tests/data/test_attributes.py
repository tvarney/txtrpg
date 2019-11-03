
from unittest.mock import MagicMock, create_autospec
from rpg.data.attributes import *


def test_attribute_color():
    attr = Attribute(10, 10)
    assert attr.color == Attribute.ColorNormal

    attr.value = 11
    assert attr.color == Attribute.ColorAbove

    attr.value = 9
    assert attr.color == Attribute.ColorBelow


def test_attribute_short_string():
    attr = Attribute(10, 10)
    assert attr.short_string == "10"

    attr.value = 9
    assert attr.short_string == "9"

    attr.value = 11
    assert attr.short_string == "11"


def test_attribute_long_string():
    attr = Attribute(10, 10)
    assert attr.long_string == "10"

    attr.value = 11
    assert attr.long_string == "11 [+1]"

    attr.value = 9
    assert attr.long_string == "9 [-1]"


def test_attribute_set_level():
    attr = Attribute(10, 10)

    attr.level = 11
    assert attr.level == 11
    assert attr.value == 11

    attr.level = 10
    assert attr.level == 10
    assert attr.value == 10

    attr.level += 2
    assert attr.level == 12
    assert attr.value == 12

    attr.level -= 100
    assert attr.level == 0
    assert attr.value == 0

    attr.level = 10
    attr.value = 12

    attr.level -= 1
    assert attr.level == 9
    assert attr.value == 11

    attr.level += 2
    assert attr.level == 11
    assert attr.value == 13


def _make_primary_attr_listeners(level, value, listener_count):
    attr = PrimaryAttribute(level, value)
    listeners = (MagicMock() for _ in range(3))
    for l in listeners:
        l.udpate.return_value = None
        attr.add(l)

    return attr, listeners


def test_primary_attribute_notify():
    attr, listeners = _make_primary_attr_listeners(10, 10, 3)
    attr.notify('test')
    for l in listeners:
        l.update.assert_called_once_with(attr, 'test')


def test_primary_attribute_notify_on_level():
    attr, listeners = _make_primary_attr_listeners(10, 10, 3)
    attr.level += 1
    for l in listeners:
        l.update.assert_called_once_with(attr, 'level')


def test_primary_attribute_level_no_notify_zero():
    attr, listeners = _make_primary_attr_listeners(10, 10, 3)
    attr.level = 10
    for l in listeners:
        l.assert_not_called()


def test_primary_attribute_notify_on_value():
    attr, listeners = _make_primary_attr_listeners(10, 10, 3)
    attr.value += 1
    for l in listeners:
        l.update.assert_called_once_with(attr, 'value')


def test_primary_attribute_value_no_notify_zero():
    attr, listeners = _make_primary_attr_listeners(10, 10, 3)
    attr.value = 10
    for l in listeners:
        l.update.assert_not_called()


def test_secondary_attribute_tracked_change():
    attr_1 = PrimaryAttribute(10, 10)
    attr_2 = PrimaryAttribute(10, 10)
    attr = SecondaryAttribute(tracked=((7, attr_1), (3, attr_2)))

    assert attr.level == 100
    assert attr.value == 100

    attr_1.level += 1
    assert attr.level == 107
    assert attr.value == 107

    attr.level -= 1
    assert attr.level == 107
    assert attr.value == 107
