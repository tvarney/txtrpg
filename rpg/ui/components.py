
from enum import IntEnum, unique
import tkinter
from rpg.ui import widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import actor
    from typing import Dict, List, Tuple


class RootMenuBar(tkinter.Menu):
    """
    The root menu bar for the main window
    """
    def __init__(self, game_obj: 'app.Game'):
        tkinter.Menu.__init__(self, game_obj.root())
        self._game_obj = game_obj

        self.file_menu = tkinter.Menu(self, tearoff=0)
        self.file_menu.add_command(label="Save", command=self._action_save)
        self.file_menu.add_command(label="Load", command=self._action_load)
        self.file_menu.add_command(label="Options", command=self._action_options)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._action_exit)
        self.add_cascade(label="File", menu=self.file_menu)

    def _action_save(self):
        self._game_obj.log.debug("RootMenuBar::_action_save(): Called")

    def _action_load(self):
        self._game_obj.log.debug("RootMenuBar::_action_load(): Called")

    def _action_exit(self):
        self._game_obj.log.debug("RootMenuBar::_action_exit(): Called")

    def _action_options(self):
        self._game_obj.log.debug("RootMenuBar::_action_options(): Called")


@unique
class StatusBarItem(IntEnum):
    Name = 0
    Strength = 1
    Dexterity = 2
    Constitution = 3
    Agility = 4
    Intelligence = 5
    Wisdom = 6
    Charisma = 7
    Luck = 8
    Health = 9
    Mana = 10
    Stamina = 11
    Level = 12
    Exp = 13
    Money = 14
    Time = 15
    Date = 16


class StatusBar(tkinter.Frame):
    def __init__(self, root: tkinter.Frame, *args, **kwargs):
        tkinter.Frame.__init__(self, root, *args, **kwargs)
        self._font_name = ('Arial', 10, 'bold')
        self._font_header = ('Arial', 9, 'bold')
        self._font_item = ('Arial', 7)
        self._widgets = dict()  # type: Dict[StatusBarItem, Tuple[tkinter.Label, tkinter.Label, tkinter.StringVar]]

        var_name = tkinter.StringVar()
        w_name = widgets.LabeledVariable(self, "Name:", var_name, font=self._font_name)
        w_name.pack(side=tkinter.TOP, fill='x')
        self._widgets[StatusBarItem.Name] = (w_name.label, w_name.variable, var_name)

        self._add_section("Core Stats", [StatusBarItem.Strength, StatusBarItem.Dexterity, StatusBarItem.Constitution,
                                         StatusBarItem.Agility, StatusBarItem.Intelligence, StatusBarItem.Wisdom,
                                         StatusBarItem.Charisma, StatusBarItem.Luck])
        self._add_section("Combat Stats", [StatusBarItem.Health, StatusBarItem.Mana, StatusBarItem.Stamina])
        self._add_section("Advancement", [StatusBarItem.Level, StatusBarItem.Exp, StatusBarItem.Money])
        self._add_section("World", [StatusBarItem.Time, StatusBarItem.Date])

    def _add_section(self, header_text: str, items: 'List[StatusBarItem]', side: str=tkinter.TOP):
        section = tkinter.Frame(self)
        lbl = tkinter.Label(section, text=header_text, font=self._font_header)
        lbl.grid(row=0, column=0, columnspan=2, sticky='WE')
        for index, item in enumerate(items):
            variable = tkinter.StringVar()
            lbl = tkinter.Label(section, text=item.name, anchor='w', font=self._font_item)
            var = tkinter.Label(section, textvariable=variable, font=self._font_item)

            lbl.grid(row=index+1, column=0, sticky='WE', padx=5)
            var.grid(row=index+1, column=1, sticky='E', padx=5)
            self._widgets[item] = (lbl, var, variable)

        section.pack(side=side)

    def update_actor(self, _actor: 'actor.Actor'):
        self._widgets[StatusBarItem.Name][2].set(_actor.name())
        self._widgets[StatusBarItem.Strength][2].set(_actor.stats.strength.string())
        self._widgets[StatusBarItem.Dexterity][2].set(_actor.stats.dexterity.string())
        self._widgets[StatusBarItem.Constitution][2].set(_actor.stats.constitution.string())
        self._widgets[StatusBarItem.Agility][2].set(_actor.stats.agility.string())
        self._widgets[StatusBarItem.Intelligence][2].set(_actor.stats.intelligence.string())
        self._widgets[StatusBarItem.Wisdom][2].set(_actor.stats.wisdom.string())
        self._widgets[StatusBarItem.Charisma][2].set(_actor.stats.charisma.string())
        self._widgets[StatusBarItem.Luck][2].set(_actor.stats.luck.string())
        self._widgets[StatusBarItem.Health][2].set(_actor.stats.health.string())
        self._widgets[StatusBarItem.Mana][2].set(_actor.stats.mana.string())
        self._widgets[StatusBarItem.Stamina][2].set(_actor.stats.stamina.string())


class AttributeWidget(tkinter.Frame):
    def __init__(self, root: 'tkinter.Frame', name: str, points: 'tkinter.IntVar', initial_value: int=10, min_value: int=8,
                 max_value: int=18):
        tkinter.Frame.__init__(self, root)
        self.value = tkinter.IntVar(self, initial_value)
        self._point_var = points
        self._initial_value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._name = name

        self._lblName = tkinter.Label(self, text=name)
        self._btnIncrease = widgets.Button(self, "+", self._action_inc)
        self._lblDisplay = tkinter.Label(self, textvariable=self.value)
        self._btnDecrease = widgets.Button(self, "-", self._action_dec)

        self._lblName.pack(side='top')
        self._btnIncrease.pack(side='top')
        self._lblDisplay.pack(side='top')
        self._btnDecrease.pack(side='top')

    def update_value(self, value: int, min_value: int=8, max_value: int=18):
        self.value.set(value)
        self._initial_value = value
        self._min_value = min_value
        self._max_value = max_value

    def reset_value(self):
        diff = self.value.get() - self._initial_value
        self._point_var.set(self._point_var.get() + diff)
        self.value.set(self._initial_value)

    def save_value(self):
        self._initial_value = self.value.get()

    def _action_inc(self):
        _value = self.value.get()
        _points = self._point_var.get()
        if _points > 0 and _value < self._max_value:
            self.value.set(_value + 1)
            self._point_var.set(_points - 1)

    def _action_dec(self):
        _value = self.value.get()
        if _value > self._min_value:
            self.value.set(_value - 1)
            self._point_var.set(self._point_var.get() + 1)


class AttributeEditorFrame(tkinter.Frame):
    def __init__(self, root: 'tkinter.Frame', initial_points: int):
        tkinter.Frame.__init__(self, root)
        self._points = tkinter.IntVar(self, initial_points)

        self._frmPoints = tkinter.Frame(self)
        self._lblPointsLabel = tkinter.Label(self._frmPoints, text="Points:")
        self._lblPointsDisplay = tkinter.Label(self._frmPoints, textvariable=self._points)

        self._frmStrength = AttributeWidget(self, "Str", self._points)
        self._frmDexterity = AttributeWidget(self, "Dex", self._points)
        self._frmConstitution = AttributeWidget(self, "Con", self._points)
        self._frmAgility = AttributeWidget(self, "Agl", self._points)
        self._frmIntelligence = AttributeWidget(self, "Int", self._points)
        self._frmWisdom = AttributeWidget(self, "Wis", self._points)
        self._frmCharisma = AttributeWidget(self, "Cha", self._points)
        self._frmLuck = AttributeWidget(self, "Lck", self._points)

        self._lblPointsLabel.pack(side='left')
        self._lblPointsDisplay.pack(side='left')
        self._frmPoints.grid(row=0, column=0, columnspan=8)
        self._frmStrength.grid(row=1, column=0)
        self._frmDexterity.grid(row=1, column=1)
        self._frmConstitution.grid(row=1, column=2)
        self._frmAgility.grid(row=1, column=3)
        self._frmIntelligence.grid(row=1, column=4)
        self._frmWisdom.grid(row=1, column=5)
        self._frmCharisma.grid(row=1, column=6)
        self._frmLuck.grid(row=1, column=7)

    def read(self, _actor: 'actor.Player'):
        self._points.set(_actor.attribute_points)
        self._frmStrength.value.set(_actor.stats.strength.value())
        self._frmDexterity.value.set(_actor.stats.dexterity.value())
        self._frmConstitution.value.set(_actor.stats.constitution.value())
        self._frmAgility.value.set(_actor.stats.agility.value())
        self._frmIntelligence.value.set(_actor.stats.intelligence.value())
        self._frmWisdom.value.set(_actor.stats.wisdom.value())
        self._frmCharisma.value.set(_actor.stats.charisma.value())
        self._frmLuck.value.set(_actor.stats.luck.value())

    def write(self, _actor: 'actor.Player'):
        _actor.attribute_points = self._points.get()
        _actor.stats.strength.level_up(self._frmStrength.value.get() - _actor.stats.strength.value())
        _actor.stats.dexterity.level_up(self._frmDexterity.value.get() - _actor.stats.dexterity.value())
        _actor.stats.constitution.level_up(self._frmConstitution.value.get() - _actor.stats.constitution.value())
        _actor.stats.agility.level_up(self._frmAgility.value.get() - _actor.stats.agility.value())
        _actor.stats.intelligence.level_up(self._frmIntelligence.value.get() - _actor.stats.intelligence.value())
        _actor.stats.wisdom.level_up(self._frmWisdom.value.get() - _actor.stats.wisdom.value())
        _actor.stats.charisma.level_up(self._frmCharisma.value.get() - _actor.stats.charisma.value())
        _actor.stats.luck.level_up(self._frmLuck.value.get() - _actor.stats.luck.value())
        _actor.calculate_secondaries()
