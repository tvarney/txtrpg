
import inspect
import tkinter
from rpg.ui import widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app, event
    from typing import List, Optional, Tuple, Union

class Option(object):
    def __init__(self, name, event_instance: 'event.GameEvent', visible: bool=True):
        self.name = name
        self.event = event_instance
        self.visible = visible
        if inspect.isclass(self.event):
            raise Exception("Class passed when instance expected for option '{}'".format(self.name))

    def generate(self, game: 'app.Game', root: 'tkinter.Frame') -> 'Union[tkinter.Label, widgets.Button]':
        def _do_apply():
            self.event.apply(game)
        return widgets.Button(root, self.name, _do_apply) if self.visible else tkinter.Label(root)


class OptionFrame(tkinter.Frame):
    def __init__(self, parent: tkinter.Frame, game: 'app.Game', opts: 'List[List[Optional[Option]]]', **kwargs):
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

    def _do_place(self, width, height):
        full_width = max(self.master.winfo_width(), 800)
        space_width = (full_width - 800) / 2
        part_width = full_width - space_width
        portion = 1 / OptionList.MaxColumns
        rel_size = (part_width / full_width) * portion
        offset = (portion * 0.5) * (space_width / full_width)
        new_height = 80 + (max(600, self.master.winfo_height()) - 600) * 0.5

        self.configure(width=full_width, height=new_height)
        for opt, row, col in self._children:
            opt.place(relheight=1 / OptionList.MaxRows, relwidth=rel_size, relx=col / OptionList.MaxColumns + offset,
                      rely=row / OptionList.MaxRows)

    def _on_resize(self, tk_event):
        for opt, _, _ in self._children:
            opt.place_forget()
        self._do_place(tk_event.width, tk_event.height)


class OptionList(object):
    MaxRows = 3
    MaxColumns = 8
    RowSize = 30
    ColumnSize = 100

    @staticmethod
    def generate_paged_list(options: 'List[Tuple[str, event.GameEvent]]') -> 'OptionList':
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

    def __init__(self, *options: 'Tuple[Option, int, int]'):
        r = OptionList.MaxRows
        c = OptionList.MaxColumns
        self._options = [[None for _ in range(c)] for _ in range(r)]  # type: List[List[Optional[Option]]]
        for opt, row, col in options:
            self.set(opt, row, col)

    def clear(self):
        for row in range(OptionList.MaxRows):
            for col in range(OptionList.MaxColumns):
                self._options[row][col]=None

    def set(self, option: Option, row: int, column: int):
        self._options[row][column] = option

    def get(self, row: int, column: int) -> 'Optional[Option]':
        return self._options[row][column]

    def generate(self, game: 'app.Game', parent: tkinter.Frame) -> tkinter.Frame:
        return OptionFrame(parent, game, self._options)
