
"""Composite widget definitions.

This module defines composite tkinter widgets. These are more complicated than those found in the rpg.ui.widgets module.
In general, these define a logical grouping of widgets which have a very narrow focus (such as a menu bar or status
bar).

"""

from enum import IntEnum, unique
import tkinter
from rpg import util
from rpg.ui import widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.data import actor
    from typing import Any, Dict, List, Optional, Tuple


class RootMenuBar(tkinter.Menu):
    """The root menu bar for the main window.

    """
    def __init__(self, game_obj: 'app.Game') -> None:
        """Initialize the RootMenuBar instance.

        :param game_obj: The app.Game object this menu bar is attached to
        """
        tkinter.Menu.__init__(self, game_obj.root())
        self._game_obj = game_obj
        self._console = None
        self._console_state = ConsoleState(game_obj)

        self.file_menu = tkinter.Menu(self, tearoff=0)
        self.file_menu.add_command(label="Save", command=self._action_save)
        self.file_menu.add_command(label="Load", command=self._action_load)
        self.file_menu.add_command(label="Options", command=self._action_options)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._action_exit)
        self.add_cascade(label="File", menu=self.file_menu)

        self.debug_menu = tkinter.Menu(self, tearoff=0)
        self.debug_menu.add_command(label="Open Console", command=self._action_console)
        self.add_cascade(label="Debug", menu=self.debug_menu)

    def _action_save(self) -> None:
        self._game_obj.log.debug("RootMenuBar::_action_save(): Called")

    def _action_load(self) -> None:
        self._game_obj.log.debug("RootMenuBar::_action_load(): Called")

    def _action_exit(self) -> None:
        self._game_obj.log.debug("RootMenuBar::_action_exit(): Called")

    def _action_options(self) -> None:
        self._game_obj.log.debug("RootMenuBar::_action_options(): Called")

    def _action_console(self) -> None:
        root = self._game_obj.root()  # type: tkinter.Tk
        self._console = ConsoleWindow(root, self._console_state)


@unique
class StatusBarItem(IntEnum):
    """Index for each of the items in the StatusBar component.

    """

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


# TODO: Make the StatusBar class more generally accessible to data packages
#     : If a package adds a variable (stored generally in rpg.state.GameData.variables) that should be displayed
#     : there should be some method for the package to hook into the StatusBar and add new sections/fields
class StatusBar(tkinter.Frame):

    """A tkinter.Frame holding a collection of status display widgets for actor instances.

    This component is intended to display the attributes of the player actor.

    """

    def __init__(self, root: tkinter.Frame, *args, **kwargs) -> None:
        """Initialize and layout the StatusBar.

        :param root: The root frame that this StatusBar is to be added to
        :param args: Extra arguments for the main frame
        :param kwargs: Keyword arguments for the main frame
        """
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

    def _add_section(self, header_text: str, items: 'List[StatusBarItem]', side: str=tkinter.TOP) -> None:
        """Add a section to the StatusBar.

        :param header_text: The text of the header
        :param items: The list of items to add to this section
        :param side: How to lay this section out
        """
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

    def update_actor(self, _actor: 'actor.Actor') -> None:
        """Update the actor attribute fields.

        :param _actor: The actor to get values from
        """
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

    """Widget for editing an attribute of an actor.

    This widget is used by the AttributeEditorFrame to implement character attribute improvements.

    """

    def __init__(self, root: 'tkinter.Frame', name: str, points: 'tkinter.IntVar', initial_value: int=10,
                 min_value: int=8, max_value: int=18) -> None:
        """Initialize the AttributeWidget.

        For initial set-up, the default minimum value of 8 should be used. For level-up attribute changes, the min_value
        argument should be equal to the initial_value argument; this keeps the player from lowering an attribute on
        level up to get more points.

        :param root: The root frame to place this AttributeWidget in
        :param name: The name of the attribute
        :param points: The tkinter.IntVar used to track how many points may be spent
        :param initial_value: The starting value of the attribute
        :param min_value: The lowest this AttributeWidget will let the tracked value go
        :param max_value: The maximum this AttributeWidget will let the tracked value go
        """
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

    def update_value(self, value: int, min_value: 'Optional[int]'=None, max_value: 'Optional[int]'=None) -> None:
        """Change the initial_value, min_value, and max_value arguments of this AttributeWidget.

        :param value: The new value/initial value of the widget
        :param min_value: The new minimum value of the widget (use None to keep the old value)
        :param max_value: The new maximum value of the widget (use None to keep the old value)
        :return:
        """
        self.value.set(value)
        self._initial_value = value
        self._min_value = min_value if min_value is not None else self._min_value
        self._max_value = max_value if max_value is not None else self._max_value

    def reset_value(self) -> None:
        """Reset the value of this widget to the initial value, refunding any points spent."""
        diff = self.value.get() - self._initial_value
        self._point_var.set(self._point_var.get() + diff)
        self.value.set(self._initial_value)

    def save_value(self) -> None:
        """Set the initial value to the current value."""
        self._initial_value = self.value.get()

    def _action_inc(self) -> None:
        _value = self.value.get()
        _points = self._point_var.get()
        if _points > 0 and _value < self._max_value:
            self.value.set(_value + 1)
            self._point_var.set(_points - 1)

    def _action_dec(self) -> None:
        _value = self.value.get()
        if _value > self._min_value:
            self.value.set(_value - 1)
            self._point_var.set(self._point_var.get() + 1)


class AttributeEditorFrame(tkinter.Frame):

    """Frame which aggregates AttributeWidgets for each attribute a player may edit.

    This component also initializes the shared tkinter.IntVar for the points that each AttributeWidget requires.

    """

    def __init__(self, root: 'tkinter.Frame', initial_points: int) -> None:
        """Initialize the AttributeEditorFrame.

        :param root: The root tkinter.Frame to place this AttributeEditorFrame in
        :param initial_points: How many attribute points are available
        """
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

    def read(self, _actor: 'actor.Player') -> None:
        """Set the AttributeWidget values to the Attribute levels of the given player

        :param _actor: The actor.Player instance to use for values
        """
        self._points.set(_actor.attribute_points)
        self._frmStrength.value.set(_actor.stats.strength.value())
        self._frmDexterity.value.set(_actor.stats.dexterity.value())
        self._frmConstitution.value.set(_actor.stats.constitution.value())
        self._frmAgility.value.set(_actor.stats.agility.value())
        self._frmIntelligence.value.set(_actor.stats.intelligence.value())
        self._frmWisdom.value.set(_actor.stats.wisdom.value())
        self._frmCharisma.value.set(_actor.stats.charisma.value())
        self._frmLuck.value.set(_actor.stats.luck.value())

    def write(self, _actor: 'actor.Player') -> None:
        """Set the Attribute levels of the given player to the values in the AttributeWidgets.

        :param _actor: The actor.Player instance to set values on
        """
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


class StatCanvas(tkinter.Canvas):
    def __init__(self, root: tkinter.Frame, title: str, width: int, height: int, color: int):
        tkinter.Canvas.__init__(self, root)
        self._width = width
        self._height = height
        self._color = color
        self._title = title

    def draw_self(self):
        self.create_text()


class CombatStatusBar(tkinter.Frame):
    def __init__(self, root: tkinter.Frame, **kwargs):
        tkinter.Frame.__init__(self, root, **kwargs)
        # We want a layout like:
        # Name: Level (buffs)
        # Health | | Mana | | Stamina

        self._var_name = tkinter.StringVar(self)
        self._var_level = tkinter.StringVar(self)
        self._var_status = tkinter.StringVar(self)

        self._title_frame = tkinter.Frame(self)
        self._stats_frame = tkinter.Frame(self)

        self._lbl_name = tkinter.Label(self._title_frame, textvariable=self._var_name, font=("arial", 14, "bold"))
        self._lbl_level = tkinter.Label(self._title_frame, textvariable=self._var_level, font=("arial", 10, "bold"))
        self._lbl_status = tkinter.Label(self._title_frame, textvariable=self._var_status, font=("arial", 10, "bold"))

        self._lbl_health = widgets.LabeledVariable(self._stats_frame, "Health:")
        self._lbl_mana = widgets.LabeledVariable(self._stats_frame, "Mana:")
        self._lbl_stamina = widgets.LabeledVariable(self._stats_frame, "Stamina:")

        self._lbl_name.pack(side="left")
        self._lbl_level.pack(side="left")
        self._lbl_status.pack(side="left")

        self._lbl_health.pack(side="left")
        self._lbl_stamina.pack(side="left")
        self._lbl_mana.pack(side="left")

        self._title_frame.pack(side="top", expand=True, fill="x")
        self._stats_frame.pack(side="top", expand=True, fill="x")

    def update_actor(self, actor_: "actor.NonPlayerCharacter"):
        self._var_name.set(actor_.name())
        self._var_level.set("(lvl. 1)")
        self._var_status.set("")
        self._lbl_health.get_variable().set(actor_.stats.health.string(False))
        self._lbl_stamina.get_variable().set(actor_.stats.stamina.string(False))
        self._lbl_mana.get_variable().set(actor_.stats.mana.string(False))


class ConsoleState(object):
    def __init__(self, game: 'app.Game'):
        self.history = list()
        self.environ = {'game': game, 'console': self}
        self._game = game
        self._window = None

    def bind(self, console_window: 'ConsoleWindow'):
        self._window = console_window

    def unbind(self):
        self._window = None

    def clear(self):
        if self._window is not None:
            self._window.clear()

    def evaluate(self, code_string) -> 'Any':
        # Ensure that game and console are always correct
        code_string = code_string.strip()
        if code_string == "reset":
            self.environ = {'game': self._game, 'console': self}
            self.history.clear()
            self.clear()
            return

        try:
            return eval(code_string, self.environ)
        except Exception as _:
            pass
        # Let any exceptions thrown here be passed up to the caller
        exec(code_string, self.environ)


class ConsoleWindow(tkinter.Toplevel):
    def __init__(self, root: 'tkinter.Tk', state: ConsoleState, **kwargs):
        tkinter.Toplevel.__init__(self, root, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._alt = False
        self._ctrl = False

        self._state = state
        self._state.bind(self)
        self._hist_line = 0
        self._stash = ""

        self._frame = tkinter.Frame(self)
        self._scrollOutput = tkinter.Scrollbar(self._frame)
        self._scrollInput = tkinter.Scrollbar(self._frame)
        self._txtOutput = widgets.StaticTextArea(self._frame, yscrollcommand=self._scrollOutput.set)
        self._txtInput = widgets.CustomTextArea(self._frame, height=1, yscrollcommand=self._scrollInput.set)

        self._txtInput.bind("<Return>", self._on_enter)
        self._txtInput.bind("<Up>", self._arrow_up)  # Move to previous history line
        self._txtInput.bind("<Down>", self._arrow_down)  # Move to next history line

        self._txtOutput.grid(row=0, column=0, sticky='nsew')
        self._txtInput.grid(row=1, column=0, sticky='nsew')
        self._scrollOutput.grid(row=0, column=1, sticky='ns')
        self._scrollInput.grid(row=1, column=1, sticky='ns')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._frame.pack(fill='both')

        self._txtOutput.tag_config("e", foreground="red")
        self._txtOutput.tag_config("o", foreground="blue")

        self._txtInput.focus()

    def clear(self):
        print("Clear Window")
        self._txtOutput.delete('1.0', 'end')

    def _on_close(self):
        self._state.unbind()
        self.destroy()

    def _on_enter(self, event) -> 'Optional[str]':
        # If shift is pressed, let the enter key pass un-interrupted
        if widgets.shift(event):
            return

        # Otherwise, we need to display the text, reset the input box, run the code, and display the result
        value = self._txtInput.get(1.0, "end").strip()
        self._txtInput.delete(1.0, "end")
        if value == "":
            return "break"

        if len(self._state.history) > 0:
            if self._state.history[-1] != value:
                self._state.history.append(value)
        else:
            self._state.history.append(value)
        self._hist_line = 0

        value_add = "\n".join(">>> {}".format(part) for part in value.split("\n")) + "\n"
        self._txtOutput.insert("end", value_add)
        self._txtInput.configure(height=3)

        try:
            return_value = self._state.evaluate(value)
            if return_value is not None:
                self._txtOutput.insert('end', "{}\n".format(repr(return_value)), "o")
        except Exception as e:
            self._txtOutput.insert("end", util.format_exception(e), "e")

        # Make sure the output is focused at the end of the text in it
        self._txtOutput.see("end")
        return "break"

    def _print_override(self, *objects, sep='', end='\n', file=None) -> None:
        self._txtOutput.insert("end", sep.join(str(obj) for obj in objects) + end, "o")

    def _raise_exception(self, *args, **kwargs):
        raise Exception("function not available")

    def _arrow_up(self, _) -> str:
        y, x = self._txtInput.get_mark('insert')
        if y == 1:
            min_hist = -len(self._state.history)
            if min_hist < 0 and self._hist_line == 0:
                self._stash = self._txtInput.get('1.0', 'end-1c').rstrip()

            hist_line = max(self._hist_line - 1, min_hist)
            if hist_line != self._hist_line:
                self._hist_line = hist_line
                self._txtInput.delete('1.0', 'end')
                self._txtInput.insert('1.0', self._state.history[self._hist_line])
            return "break"

    def _arrow_down(self, _) -> str:
        y, x = self._txtInput.get_mark('insert')
        max_y, max_x = self._txtInput.get_mark('end')
        if y == max_y - 1:
            if self._hist_line == -1:
                self._hist_line = 0
                self._txtInput.delete('1.0', 'end')
                self._txtInput.insert('1.0', self._stash)
                self._stash = ""
            else:
                hist_line = min(self._hist_line + 1, 0)
                if hist_line != self._hist_line:
                    self._hist_line = hist_line
                    self._txtInput.delete('1.0', 'end')
                    if hist_line != 0:
                        self._txtInput.insert('1.0', self._state.history[self._hist_line])
            return "break"
