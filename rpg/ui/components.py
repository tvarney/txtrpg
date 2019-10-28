
"""Composite widget definitions.

This module defines composite tk widgets. These are more complicated than
those found in the rpg.ui.widgets module. In general, these define a logical
grouping of widgets which have a very narrow focus (such as a menu bar or
status bar).
"""

import tkinter as tk
from rpg.ui import console, widgets

import typing
if typing.TYPE_CHECKING:
    from rpg.app import Game
    from rpg.data.inventory import Inventory, ItemStack
    from rpg.data.actor import Actor, Player, NonPlayerCharacter
    from typing import Callable, Dict, List, Optional

StatusBarSectionItem = typing.Tuple[
    str, tk.Widget, typing.Optional[typing.Callable]
]

StatusBarSectionItemAddition = typing.Tuple[
    StatusBarSectionItem, typing.Dict
]


class RootMenuBar(tk.Menu):
    """The root menu bar for the main window.

    """
    def __init__(self, game_obj: 'Game') -> None:
        """Initialize the RootMenuBar instance.

        :param game_obj: The Game object this menu bar is attached to
        """
        tk.Menu.__init__(self, game_obj.root())
        self._game_obj = game_obj
        self._console = None
        self._console_state = console.ConsoleState(game_obj)

        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="Save", command=self._action_save)
        self.file_menu.add_command(label="Load", command=self._action_load)
        self.file_menu.add_command(
            label="Options", command=self._action_options
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._action_exit)
        self.add_cascade(label="File", menu=self.file_menu)

        self.debug_menu = tk.Menu(self, tearoff=0)
        self.debug_menu.add_command(
            label="Open Console", command=self._action_console
        )
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
        root = self._game_obj.root()
        self._console = console.ConsoleWindow(root, self._console_state)


class StatusBarSection(tk.Frame):
    def __init__(self, root: tk.Frame, name: 'Optional[str]',
                 title_fnt=("Arial", 12, 'bold')) -> None:
        tk.Frame.__init__(self, root)
        self._name = name
        self._lock = False
        self._items = list()    # type: List[StatusBarSectionItem]
        self._removed = list()  # type: List[int]
        self._added = list()    # type: List[StatusBarSectionItemAddition]

        self._title = None
        if name is not None and name != "":
            self._title = tk.Label(self, text=name, font=title_fnt)

        if self._title is not None:
            self._title.pack(side="top", anchor="w")

    def lock(self) -> None:
        self._lock = True

    def unlock(self) -> None:
        self._lock = False
        if len(self._removed) > 0:
            self._remove_all()
        if len(self._added) > 0:
            self._add_all()

    def add_item(self, key: str, widget: tk.Widget,
                 update_fn: 'Optional[Callable]' = None, **kwargs) -> None:
        self._added.append(((key, widget, update_fn), kwargs))
        if not self._lock:
            self._add_all()

    def remove_item(self, key: str):
        for i in range(len(self._items)):
            if self._items[i][0] == key:
                self._removed.append(i)

        if not self._lock:
            self._remove_all()

    def get_item(self, key: str) -> 'Optional[tk.Widget]':
        for wkey, widget, update_fn in self._items:
            if wkey == key:
                return widget

        for wkey, widget, kwargs, update_fn in self._added:
            if wkey == key:
                return widget

        return None

    def update_widgets(self, player: 'Actor', game: 'Game') -> None:
        for key, widget, update_fn in self._items:
            if callable(update_fn):
                update_fn(widget, player, game)

    def _remove_all(self) -> None:
        self._removed.sort()
        # Guaranteed to be invalid - used to skip duplicate removals
        last = len(self._items) + 1
        for idx in self._removed:
            if idx != last:
                self._items.pop(idx)
            last = idx

    def _add_all(self) -> None:
        for key, widget, kwargs, update_fn in self._added:
            self._items.append((key, widget, update_fn))
            if "expand" not in kwargs:
                kwargs['expand'] = True
            if kwargs['expand']:
                kwargs['fill'] = 'x'
            if 'anchor' not in kwargs:
                kwargs['anchor'] = 'w'
            widget.pack(**kwargs)
        self._added.clear()


class StatusBar(tk.Frame):
    """A Frame holding a collection of status display widgets for actor
    instances.

    This component is intended to display the attributes of the player actor.
    """

    @classmethod
    def default(cls, root: tk.Frame, game: 'Game',
                *args, **kwargs) -> 'StatusBar':
        status_bar = StatusBar(root, game, *args, **kwargs)

        # The header section holds the players' name
        header = status_bar.add_section("header", None)
        header.add_item(
            "name", widgets.LabeledVariable(
                header, "Name:", font=status_bar._font_name
            ),
            lambda w, p, g: w.get_variable().set(p.name())
        )

        def _stat_up(key: str, short: bool = True):
            def _update_stat(w, p, _):
                # TODO: Set the color of the variable label instance
                w.get_variable().set(getattr(p.stats, key).string(short))

            return _update_stat

        def create_stat(parent, label):
            return widgets.LabeledVariable(
                parent, label, font=status_bar._font_item, expand=True
            )

        core = status_bar.add_section("core", "Core Stats")
        core.add_item(
            "str", create_stat(core, "Strength"), _stat_up("strength"),
            expand=True
        )
        core.add_item(
            "dex", create_stat(core, "Dexterity"), _stat_up("dexterity"),
            expand=True
        )
        core.add_item(
            "con", create_stat(core, "Constitution"), _stat_up("constitution"),
            expand=True
        )
        core.add_item(
            "agl", create_stat(core, "Agility"), _stat_up("agility"),
            expand=True
        )
        core.add_item(
            "int", create_stat(core, "Intelligence"), _stat_up("intelligence"),
            expand=True
        )
        core.add_item(
            "wis", create_stat(core, "Wisdom"), _stat_up("wisdom"),
            expand=True
        )
        core.add_item(
            "cha", create_stat(core, "Charisma"), _stat_up("charisma"),
            expand=True
        )
        core.add_item(
            "lck", create_stat(core, "Luck"), _stat_up("luck"),
            expand=True
        )

        combat = status_bar.add_section("combat", "Combat Stats")
        combat.add_item(
            "hp", create_stat(combat, "Health"), _stat_up("health", False),
            expand=True
        )
        combat.add_item(
            "mp", create_stat(combat, "Mana"), _stat_up("mana", False),
            expand=True
        )
        combat.add_item(
            "st", create_stat(combat, "Stamina"), _stat_up("stamina", False),
            expand=True
        )

        adv = status_bar.add_section("advancement", "Advancement")
        adv.add_item(
            "level", widgets.LabeledVariable(
                adv, "Level", font=status_bar._font_item
            )
        )
        adv.add_item(
            "exp", widgets.LabeledVariable(
                adv, "Exp", font=status_bar._font_item
            )
        )
        adv.add_item(
            "Money", widgets.LabeledVariable(
                adv, "Money", font=status_bar._font_item
            )
        )

        world = status_bar.add_section("world", "World")
        world.add_item(
            "time", widgets.LabeledVariable(
                world, "Time", font=status_bar._font_item
            )
        )
        world.add_item(
            "date", widgets.LabeledVariable(
                world, "Date", font=status_bar._font_item
            )
        )

        return status_bar

    def __init__(self, root: 'tk.Frame', game: 'Game',
                 *args, **kwargs) -> None:
        """Initialize and layout the StatusBar.

        :param root: The root frame that this StatusBar is to be added to
        :param args: Extra arguments for the main frame
        :param kwargs: Keyword arguments for the main frame
        """
        tk.Frame.__init__(self, root, *args, **kwargs)
        self._game = game
        self._font_name = ('Arial', 10, 'bold')
        self._font_header = ('Arial', 9, 'bold')
        self._font_item = ('Arial', 7)

        self._sections = dict()  # type: Dict[str, StatusBarSection]

    def add_section(self, key: str, header: 'Optional[str]',
                    side: str = 'top') -> StatusBarSection:
        """Add a section to the StatusBar.

        :param key: The key used to look this section up from
        :param header: The section to add
        :param side: How to lay this section out
        """
        section = StatusBarSection(self, header, self._font_header)
        section.pack(side=side, expand=True, anchor='w', fill='x')
        self._sections[key] = section
        return section

    def get_section(self, key: str) -> 'Optional[StatusBarSection]':
        return self._sections.get(key, None)

    def update_widgets(self, _actor: 'Actor', _game: 'Game') -> None:
        """Update the actor attribute fields.

        :param _actor: The actor to get values from
        :param _game: The Game instance
        """
        for section in self._sections.values():
            section.update_widgets(_actor, _game)


class AttributeWidget(tk.Frame):
    """Widget for editing an attribute of an actor.

    This widget is used by the AttributeEditorFrame to implement character
    attribute improvements.
    """

    def __init__(self, root: 'tk.Frame', name: str, points: 'tk.IntVar',
                 initial_value: int = 10, min_value: int = 8,
                 max_value: int = 18) -> None:
        """Initialize the AttributeWidget.

        For initial set-up, the default minimum value of 8 should be used. For
        level-up attribute changes, the min_value argument should be equal to
        the initial_value argument; this keeps the player from lowering an
        attribute on level up to get more points.

        :param root: The root frame to place this AttributeWidget in
        :param name: The name of the attribute
        :param points: The IntVar used to track how many points may be spent
        :param initial_value: The starting value of the attribute
        :param min_value: The lowest the tracked value may be set to
        :param max_value: The maximum the tracked value may be set to
        """
        tk.Frame.__init__(self, root)
        self.value = tk.IntVar(self, initial_value)
        self._point_var = points
        self._initial_value = initial_value
        self._min_value = min_value
        self._max_value = max_value
        self._name = name

        self._lblName = tk.Label(self, text=name)
        self._btnIncrease = widgets.Button(self, "+", self._action_inc)
        self._lblDisplay = tk.Label(self, textvariable=self.value)
        self._btnDecrease = widgets.Button(self, "-", self._action_dec)

        self._lblName.pack(side='top')
        self._btnIncrease.pack(side='top')
        self._lblDisplay.pack(side='top')
        self._btnDecrease.pack(side='top')

    def update_value(self, value: int, min_value: 'Optional[int]' = None,
                     max_value: 'Optional[int]' = None) -> None:
        """Change the initial_value, min_value, and max_value arguments of this
        AttributeWidget.

        :param value: The new value/initial value of the widget
        :param min_value: The new minimum value of the widget (use None to keep
                          the old value)
        :param max_value: The new maximum value of the widget (use None to keep
                          the old value)
        """
        self.value.set(value)
        self._initial_value = value
        if min_value is not None:
            self._min_value = min_value
        if max_value is not None:
            self._max_value = max_value

    def reset_value(self) -> None:
        """Reset the value of this widget to the initial value, refunding any
        points spent.
        """
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


class AttributeEditorFrame(tk.Frame):
    """Frame which aggregates AttributeWidgets for each attribute a player may
    edit.

    This component also initializes the shared IntVar for the points that each
    AttributeWidget requires.
    """

    def __init__(self, root: 'tk.Frame', initial_points: int) -> None:
        """Initialize the AttributeEditorFrame.

        :param root: The root Frame to place this AttributeEditorFrame in
        :param initial_points: How many attribute points are available
        """
        tk.Frame.__init__(self, root)
        self._points = tk.IntVar(self, initial_points)

        self._frmPoints = tk.Frame(self)
        self._lblPointsLabel = tk.Label(self._frmPoints, text="Points:")
        self._lblPointsDisplay = tk.Label(
            self._frmPoints, textvariable=self._points
        )

        self._frmStr = AttributeWidget(self, "Str", self._points)
        self._frmDex = AttributeWidget(self, "Dex", self._points)
        self._frmCon = AttributeWidget(self, "Con", self._points)
        self._frmAgl = AttributeWidget(self, "Agl", self._points)
        self._frmInt = AttributeWidget(self, "Int", self._points)
        self._frmWis = AttributeWidget(self, "Wis", self._points)
        self._frmCha = AttributeWidget(self, "Cha", self._points)
        self._frmLck = AttributeWidget(self, "Lck", self._points)

        self._lblPointsLabel.pack(side='left')
        self._lblPointsDisplay.pack(side='left')
        self._frmPoints.grid(row=0, column=0, columnspan=8)
        self._frmStr.grid(row=1, column=0)
        self._frmDex.grid(row=1, column=1)
        self._frmCon.grid(row=1, column=2)
        self._frmAgl.grid(row=1, column=3)
        self._frmInt.grid(row=1, column=4)
        self._frmWis.grid(row=1, column=5)
        self._frmCha.grid(row=1, column=6)
        self._frmLck.grid(row=1, column=7)

    def read(self, _actor: 'Player') -> None:
        """Set the AttributeWidget values to the Attribute levels of the given
        player.

        :param _actor: The Player instance to use for values
        """
        self._points.set(_actor.attribute_points)
        self._frmStr.value.set(_actor.stats.strength.value())
        self._frmDex.value.set(_actor.stats.dexterity.value())
        self._frmCon.value.set(_actor.stats.constitution.value())
        self._frmAgl.value.set(_actor.stats.agility.value())
        self._frmInt.value.set(_actor.stats.intelligence.value())
        self._frmWis.value.set(_actor.stats.wisdom.value())
        self._frmCha.value.set(_actor.stats.charisma.value())
        self._frmLck.value.set(_actor.stats.luck.value())

    def write(self, actor: 'Player') -> None:
        """Set the Attribute levels of the given player to the values in the
        AttributeWidgets.

        :param actor: The Player instance to set values on
        """
        actor.attribute_points = self._points.get()
        actor.stats.strength.level_up(
            self._frmStr.value.get() - actor.stats.strength.value()
        )
        actor.stats.dexterity.level_up(
            self._frmDex.value.get() - actor.stats.dexterity.value()
        )
        actor.stats.constitution.level_up(
            self._frmCon.value.get() - actor.stats.constitution.value()
        )
        actor.stats.agility.level_up(
            self._frmAgl.value.get() - actor.stats.agility.value()
        )
        actor.stats.intelligence.level_up(
            self._frmInt.value.get() - actor.stats.intelligence.value()
        )
        actor.stats.wisdom.level_up(
            self._frmWis.value.get() - actor.stats.wisdom.value()
        )
        actor.stats.charisma.level_up(
            self._frmCha.value.get() - actor.stats.charisma.value()
        )
        actor.stats.luck.level_up(
            self._frmLck.value.get() - actor.stats.luck.value()
        )
        actor.calculate_secondaries()


class StatCanvas(tk.Canvas):
    def __init__(self, root: tk.Frame, title: str, width: int, height: int,
                 color: int) -> None:
        tk.Canvas.__init__(self, root)
        self._width = width
        self._height = height
        self._color = color
        self._title = title

    def draw_self(self):
        self.create_text()


class CombatStatusBar(tk.Frame):
    def __init__(self, root: tk.Frame, **kwargs):
        tk.Frame.__init__(self, root, **kwargs)
        # We want a layout like:
        # Name: Level (buffs)
        # Health | | Mana | | Stamina

        self._var_name = tk.StringVar(self)
        self._var_level = tk.StringVar(self)
        self._var_status = tk.StringVar(self)

        self._title_frame = tk.Frame(self)
        self._stats_frame = tk.Frame(self)

        self._lbl_name = tk.Label(
            self._title_frame, textvariable=self._var_name,
            font=("arial", 14, "bold")
        )
        self._lbl_level = tk.Label(
            self._title_frame, textvariable=self._var_level,
            font=("arial", 10, "bold")
        )
        self._lbl_status = tk.Label(
            self._title_frame, textvariable=self._var_status,
            font=("arial", 10, "bold")
        )

        self._lbl_health = widgets.LabeledVariable(
            self._stats_frame, "Health:"
        )
        self._lbl_mana = widgets.LabeledVariable(
            self._stats_frame, "Mana:"
        )
        self._lbl_stamina = widgets.LabeledVariable(
            self._stats_frame, "Stamina:"
        )

        self._lbl_name.pack(side="left")
        self._lbl_level.pack(side="left")
        self._lbl_status.pack(side="left")

        self._lbl_health.pack(side="left")
        self._lbl_stamina.pack(side="left")
        self._lbl_mana.pack(side="left")

        self._title_frame.pack(side="top", expand=True, fill="x")
        self._stats_frame.pack(side="top", expand=True, fill="x")

    def update_actor(self, actor: 'NonPlayerCharacter'):
        self._var_name.set(actor.name())
        self._var_level.set("(lvl. 1)")
        self._var_status.set("")
        self._lbl_health.get_variable().set(actor.stats.health.string(False))
        self._lbl_stamina.get_variable().set(actor.stats.stamina.string(False))
        self._lbl_mana.get_variable().set(actor.stats.mana.string(False))


class InventoryRow(object):
    def __init__(self, parent: 'tk.Frame', inv: 'Inventory',
                 item_stack: 'ItemStack') -> None:
        self._inventory = inv
        self._item_stack = item_stack
        self._item = item_stack.item().item()
        self.lbl_count = tk.Label(parent, text=str(item_stack.count()))
        self.lbl_name = tk.Label(parent, text=self._item.name())
        self.entry_count = widgets.NumericEntry(
            parent, width=3, validatecommand=self._validate
        )
        self.btn_use = tk.Button(parent, text="Use", command=self._action_use)
        self.btn_delete = tk.Button(
            parent, text="Trash", command=self._action_delete
        )

        self._visible = False

    def grid(self, row, **kwargs):
        if not self._visible:
            self.lbl_count.grid(row=row, column=0, **kwargs)
            self.lbl_name.grid(row=row, column=1, **kwargs)
            self.entry_count.grid(row=row, column=2, **kwargs)
            self.btn_use.grid(row=row, column=3, **kwargs)
            self.btn_delete.grid(row=row, column=4, **kwargs)
            self._visible = True

    def grid_forget(self):
        if self._visible:
            self.lbl_count.grid_forget()
            self.lbl_name.grid_forget()
            self.entry_count.grid_forget()
            self.btn_use.grid_forget()
            self.btn_delete.grid_forget()
            self._visible = False

    # noinspection PyUnusedLocal,SpellCheckingInspection
    @staticmethod
    def _validate(action, index, value_if_allowed, pvalue, _, vtype, ttype,
                  wname):
        if action == '1':
            return value_if_allowed > 0

    def _action_use(self):
        print("Use: {}".format(self._item.name()))

    def _action_delete(self):
        try:
            value = int(self.entry_count.get())
        except ValueError:
            value = 1
        if value > 0:
            self._item_stack.dec(value)
            if self._item_stack.count() <= 0:
                self.grid_forget()
                self._inventory.update()
            else:
                self.lbl_count.configure(text=str(self._item_stack.count()))


class InventoryFrame(tk.Frame):
    def __init__(self, root: tk.Frame, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)

        self._lblTitle = tk.Label(self, text="Inventory")
        self._frmScroll = widgets.VerticalScrolledFrame(self)
        self._interior = self._frmScroll.interior()
        self._widgets = list()  # type: List[InventoryRow]
        self._padx = (0, 5)
        self._pady = (2, 3)

        header_count = tk.Label(self._interior, text="#")
        header_name = tk.Label(self._interior, text="Item Name")

        header_count.grid(row=0, column=0, padx=self._padx, pady=self._pady)
        header_name.grid(row=0, column=1, padx=self._padx, pady=self._pady)

        self._lblTitle.pack(side='top', anchor='w')
        self._frmScroll.pack(
            side='bottom', anchor='nw', fill='both', expand=True
        )

    def build(self, inv: 'Inventory'):
        for row, item_stack in enumerate(inv.slots, 1):
            item = item_stack.item().item()
            if item is not None:
                irow = InventoryRow(self._interior, inv, item_stack)
                self._widgets.append(irow)
                irow.grid(row, padx=self._padx, pady=self._pady)

    def clear(self):
        if len(self._widgets):
            for irow in self._widgets:
                irow.grid_forget()

        self._widgets.clear()
