
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
