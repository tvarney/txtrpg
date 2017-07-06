
"""Definitions for OptionLists.

Most parts of the game shouldn't need to worry about creating and managing tkinter.Button instances for options; as
such, this module defines an API for creating an 'OptionList' which does not require an active instance of tkinter and
can create a new tkinter.Frame with the appropriate buttons when needed.

"""

import inspect
import tkinter
from rpg import event
from rpg.ui import widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import List, Optional, Tuple, Union


class Option(object):

    """The definition of an option on the GameView.

    An option encodes a name, an event, and if it is enabled.

    """

    def __init__(self, name, event_instance: 'event.GameEvent', visible: bool=True) -> None:
        """Initialize the option.

        :param name: The name of the option, used for the text on the button
        :param event_instance: A GameEvent instance which can be applied on the button press event
        :param visible: If the option is visible
        """
        self.name = name
        self.event = event_instance
        self.visible = visible
        if inspect.isclass(self.event):
            raise Exception("Class passed when instance expected for option '{}'".format(self.name))

    def generate(self, game: 'app.Game', root: 'tkinter.Frame') -> 'Union[tkinter.Label, widgets.Button]':
        """Create a button or label, dependent on the self.visible parameter.

        :param game: The app.Game instance
        :param root: The tkinter.Frame to place this tkinter widget into
        :return: A tkinter.Button or tkinter.Label for this option.
        """
        def _do_apply():
            self.event.apply(game)
        return widgets.Button(root, self.name, _do_apply) if self.visible else tkinter.Label(root)


class OptionFrame(tkinter.Frame):

    """A tkinter.Frame which implements a custom layout for options.

    This widget does not need to be used by anything outside of the rpg.ui.options package.

    """

    def __init__(self, parent: tkinter.Frame, game: 'app.Game', opts: 'List[List[Optional[Option]]]', **kwargs) -> None:
        """Initialize this OptionFrame instance with the list of options.

        :param parent: The root tkinter.Frame to place this OptionFrame in
        :param game: The app.Game instance
        :param opts: A list of options to place in this frame
        :param kwargs: Any additional keyword arguments for this frame
        """
        tkinter.Frame.__init__(self, parent, **kwargs)
        # TODO: Figure out why the frame doesn't auto-resize
        self.configure(width=800, height=OptionList.RowSize*OptionList.MaxRows)
        self.bind("<Configure>", self._on_resize)
        self._children = list()  # type: List[Tuple[widgets.Button, int, int]]
        for row in range(len(opts)):
            olist = opts[row]
            for col in range(len(olist)):
                opt = olist[col]
                if opt is not None:
                    self._children.append((opt.generate(game, self), row, col))

    def _do_place(self, width, height) -> None:
        full_width = max(width, 800)
        space_width = (full_width - 800) / 2
        part_width = full_width - space_width
        portion = 1 / OptionList.MaxColumns
        rel_size = (part_width / full_width) * portion
        offset = (portion * 0.5) * (space_width / full_width)
        new_height = 80 + (max(600, height) - 600) * 0.5

        self.configure(width=full_width, height=new_height)
        for opt, row, col in self._children:
            opt.place(relheight=1 / OptionList.MaxRows, relwidth=rel_size, relx=col / OptionList.MaxColumns + offset,
                      rely=row / OptionList.MaxRows)

    def _on_resize(self, tk_event) -> None:
        for opt, _, _ in self._children:
            opt.place_forget()
        self._do_place(tk_event.width, tk_event.height)


class OptionList(object):

    """A 3x8 grid of options which can generate an OptionFrame at runtime.

    This is the class which the GameView expects for the set_options() method. Do not change the OptionList.MaxRows or
    OptionList.MaxColumns variables; these should be treated as constants. The OptionList.RowSize and
    OptionList.ColumnSize variables represent the minimum sizes that the OptionFrame should assume work.

    """

    MaxRows = 3
    MaxColumns = 8
    RowSize = 30
    ColumnSize = 100

    @staticmethod
    def generate_paged_list(options: 'List[Tuple[str, event.GameEvent]]') -> 'OptionList':
        """Generate a set of OptionList objects which can be paged through.

        This static method will create a number of OptionList objects which link to each other through automatically
        generated 'Next' and 'Previous' options, then return the first such OptionList.

        :param options: A listing of names and GameEvents to convert into an OptionList group
        :return: The first OptionList object in the set generated
        """
        opts_per_page = OptionList.MaxRows * OptionList.MaxColumns
        num_opts = len(options)
        num_pages = int(num_opts // opts_per_page) + 1

        # Initialize the List of OptionList instances
        opt_lists = list()  # type: List[OptionList]
        for i in range(num_pages):
            opts = OptionList()
            base = i * opts_per_page
            for j in range(min(num_opts - base, opts_per_page)):
                option = options[base + j]
                row = int(j // OptionList.MaxColumns)
                col = int(j % OptionList.MaxRows)
                opts.set(Option(option[0], option[1]), row, col)

            opt_lists.append(opts)

        # Add the next/prev/cancel buttons
        next_row = 0
        prev_row = next_row + 1
        cancel_row = OptionList.MaxRows - 1
        last_col = OptionList.MaxColumns - 1

        if num_pages > 1:
            opt_lists[0].set(Option("Next", event.UpdateOptionsEvent(opt_lists[1])), next_row, last_col)
            opt_lists[0].set(Option("Cancel", event.OptionListReturnEvent()), cancel_row, last_col)
            for i in range(1, num_pages-1):
                opt_lists[i].set(Option("Next", event.UpdateOptionsEvent(opt_lists[i+1])), next_row, last_col)
                opt_lists[i].set(Option("Prev", event.UpdateOptionsEvent(opt_lists[i-1])), prev_row, last_col)
                opt_lists[i].set(Option("Cancel", event.OptionListReturnEvent()), cancel_row, last_col)
            opt_lists[-1].set(Option("Prev", event.UpdateOptionsEvent(opt_lists[-2])), prev_row, last_col)
            opt_lists[-1].set(Option("Cancel", event.OptionListReturnEvent()), cancel_row, last_col)
        else:
            opt_lists[0].set(Option("Cancel", event.OptionListReturnEvent()), cancel_row, last_col)

        return opt_lists[0]

    def __init__(self, *options: 'Tuple[Option, int, int]') -> None:
        """Initialize the OptionList with the given options.

        If no options are given, each slot in this OptionList is filled with None instead of an option.

        :param options: Optional listing of Option instances and the (row, column) that the option is located at
        """
        r = OptionList.MaxRows
        c = OptionList.MaxColumns
        self._options = [[None for _ in range(c)] for _ in range(r)]  # type: List[List[Optional[Option]]]
        for opt, row, col in options:
            self.set(opt, row, col)

    def clear(self) -> None:
        """Set all options of this OptionList to None."""
        for row in range(OptionList.MaxRows):
            for col in range(OptionList.MaxColumns):
                self._options[row][col] = None

    def set(self, option: 'Optional[Option]', row: int, column: int) -> None:
        """Set the option at (row, column) to the given option.

        :param option: The option to set the slot at (row, column) to
        :param row: The row of the option slot to set
        :param column: The column of the option slot to set
        """
        self._options[row][column] = option

    def get(self, row: int, column: int) -> 'Optional[Option]':
        """Get the option at the given (row, column), or None if no option has been assigned there.

        :param row: The row of the option slot to query
        :param column: The column of the option slot to query
        :return: The option at the given (row, column) slot, or None if not set
        """
        return self._options[row][column]

    def generate(self, game: 'app.Game', parent: tkinter.Frame) -> tkinter.Frame:
        """Create a new tkinter.Frame object holding all the options set.

        This method is a wrapper for the OptionFrame constructor.

        :param game: The app.Game instance
        :param parent: The root frame to place the generated tkinter.Frame into
        :return: A tkinter.Frame instance with buttons corresponding to the options in this list
        """
        return OptionFrame(parent, game, self._options)
