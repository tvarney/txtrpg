
"""Definitions of general purpose aggregate widgets.

This module is used for classes which aggregate tkinter widgets in a way that they are general purpose.

"""

import tkinter

import typing
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Tuple


def shift(event):
    return (event.state & 0x0001) != 0


def caps_lock(event):
    return (event.state & 0x0002) != 0


def control(event):
    return (event.state & 0x0004) != 0


def numlock(event):
    return (event.state & 0x0008) != 0


def alt(event):
    return (event.state & 0x20000) != 0


def modifier_string(event):
    return "Ctrl-" if control(event) else "" + (
        "Alt-" if alt(event) else "") + (
        "Shift-" if shift(event) else "") + event.keysym


class Button(tkinter.Button):

    """Wrapper around a tkinter.Button which supports setting the text and command on initialization.

    """

    def __init__(self, root: tkinter.Frame, text: str, command: 'Callable', *args, **kwargs) -> None:
        """Initialize this button

        :param root: The tkinter.Frame which this button is being placed in
        :param text: The text displayed on the button
        :param command: The callback function used when this button is pressed
        :param args: Additional arguments for the button
        :param kwargs: Additional keyword arguments for the button
        """
        tkinter.Button.__init__(self, root, *args, **kwargs)
        self['text'] = text
        self['command'] = command


class LabeledEntry(tkinter.Frame):

    """A tkinter.Entry object with an associated label.

    This is for the common case of needing an entry which has a label displaying what the entry is for.
    The component widgets can be accessed by:
        LabeledEntry.label -> The tkinter.Label widget
        LabeledEntry.entry -> The tkinter.Entry widget

    """

    def __init__(self, root: tkinter.Frame, label: str, entry_size: int=20, orientation: str=tkinter.LEFT) -> None:
        """Initialize the widget

        :param root: The tkinter.Frame in which to place this entry
        :param label: The label text displayed on this entry
        :param entry_size: How many characters wide the entry is
        :param orientation: How the label should be oriented relative to the entry
        """
        tkinter.Frame.__init__(self, root)
        self.label = tkinter.Label(self, text=label)
        self.entry = tkinter.Entry(self)
        self.entry.config(width=entry_size)

        self.label.pack(side=orientation)
        self.entry.pack(side=orientation)


class LabeledVariable(tkinter.Frame):

    """A tkinter.Label widget which has a static label decorating a label which can have its contents changed.

    """

    def __init__(self, root: tkinter.Frame, label: str, var: 'Optional[tkinter.StringVar]'=None, **kwargs) -> None:
        """

        Keyword arguments unless otherwise noted are for the parent frame.
        Special keyword arguments handled are:
            "cnf_lbl": A dictionary of keyword arguments used for the static label
            "cnf_var": A dictionary of keyword arguments used for the variable label
            "orientation": The orientation of the static label with respect to the variable label
            "font": The font to use for both the static and variable label

        :param root: The root tkinter.Frame to place this widget in
        :param label: The label text
        :param var: A variable to use, or None to create a new variable
        :param kwargs: Additional keyword arguments to apply to the frame
        """
        tkinter.Frame.__init__(self, root)
        self._variable = var if var is not None else tkinter.Variable()

        if "cnf_lbl" in kwargs:
            cnf_lbl = kwargs["cnf_lbl"]
            del kwargs["cnf_lbl"]
        else:
            cnf_lbl = dict()

        if "cnf_var" in kwargs:
            cnf_var = kwargs["cnf_var"]
            del kwargs["cnf_var"]
        else:
            cnf_var = dict()

        orientation = tkinter.LEFT
        if "orientation" in kwargs:
            orientation = kwargs["orientation"]
            del kwargs["orientation"]
        reverse_orientation = tkinter.LEFT if orientation == tkinter.RIGHT else tkinter.RIGHT
        anchor_lbl = 'w' if orientation == tkinter.LEFT else 'e'
        anchor_var = 'e' if orientation == tkinter.LEFT else 'w'
        cnf_var['anchor'] = anchor_var  # Anchor is used to place the text inside the label

        if "font" in kwargs:
            font = kwargs["font"]
            cnf_lbl["font"] = font
            cnf_var["font"] = font
            del kwargs["font"]

        cnf_lbl["text"] = label
        cnf_var["textvariable"] = self._variable

        expand = False
        if 'expand' in kwargs:
            expand = kwargs['expand']
            del kwargs['expand']
        sticky = None if not expand else 'x'

        self.label = tkinter.Label(self, **cnf_lbl)
        self.variable = tkinter.Label(self, **cnf_var)

        self.label.pack(side=orientation, expand=False, anchor=anchor_lbl)
        self.variable.pack(side=reverse_orientation, expand=expand, fill=sticky)
        self.configure(kwargs)

    def get_variable(self):
        """Get the tkinter variable.

        :return: The tkinter.StringVar instance used to control the variable label
        """
        return self._variable


class StaticTextArea(tkinter.Text):

    """Wrapper around a tkinter.Text object to provide a simple text area which can not be edited.

    This subclass of tkinter.Text forces itself to be non-editable by the user at all times. As such, it is intended as
    a simple display of multi-line text.

    The insert and delete methods are overloaded to correctly work with a disabled tkinter.Text object
    """

    def __init__(self, root: tkinter.Frame, *args, **kwargs) -> None:
        """Initialize this tkinter.Text area

        :param root: The root tkinter.Frame to place this Text widget in
        :param args: Additional arguments for the text widget
        :param kwargs: Additional keyword arguments for the text widget
        """
        tkinter.Text.__init__(self, root, *args, **kwargs)
        self.tag_config("wrap", wrap=tkinter.WORD)
        self.config(state='disabled')

    def insert(self, index, chars, *args):
        """Insert text into the text area starting at the given index.

        Text inserted with this method automatically has the "wrap" tag applied to it which wraps on word boundaries.

        :param index: The index to insert the text at
        :param chars: The text to insert at the given index
        :param args: tags for the inserted text
        """
        self.config(state='normal')
        tkinter.Text.insert(self, index, chars, ("wrap", *args))
        self.config(state='disabled')

    def delete(self, index1, index2=None) -> None:
        """Delete text between the two indices.

        If the second index is None (the default value), then the deletion will remove all text after the first index

        :param index1: The starting index to delete from
        :param index2: The end index to delete to
        """
        self.config(state='normal')
        tkinter.Text.delete(self, index1, index2)
        self.config(state='disabled')

    def replace(self, chars, *tags) -> None:
        """Replace all text in the text instance with the given text.

        :param chars: The new text to display
        :param tags: Any tags to apply to the text
        """
        self.config(state='normal')
        tkinter.Text.delete(self, 1.0, 'end')
        tkinter.Text.insert(self, 'end', chars, "wrap", *tags)
        self.config(state='disabled')

    def clear(self) -> None:
        """Alias to the delete method which removes all text."""
        self.delete(1.0, 'end')


class CustomTextArea(tkinter.Text):
    def __init__(self, root: 'tkinter.Frame', *args, **kwargs):
        tkinter.Text.__init__(self, root, *args, **kwargs)
        self._mark = None
        self.bind_multiple(('<a>', self._keycode_a), ('<b>', self._keycode_b), ('<d>', self._keycode_d),
                           ('<e>', self._keycode_e), ('<f>', self._keycode_f), ('<n>', self._keycode_n),
                           ('<p>', self._keycode_p), ('<y>', self._keycode_y), ('<w>', self._keycode_w),
                           ('<k>', self._keycode_k),
                           ('<BackSpace>', self._keycode_backspace), ("<Button-1>", self._action_click),
                           ('<space>', self._keycode_space))

    def move_cursor(self, index: str):
        """Move the insertion cursor to the given index

        This method attempts to make sure that selections and marks are handled appropriately

        :param index: The index (mark, tag, or index) to move the insertion cursor to
        """
        self.mark_set('insert', index)
        if self._mark is None:
            self.mark_set('tk::anchor1', index)
            try:
                self.tag_remove('sel', '0.1', 'end')
            except tkinter.TclError:
                pass
        else:
            iy, ix = self.get_index('insert')
            my, mx = self.get_index('mark')
            self.tag_remove('sel', '0.1', 'end')
            if iy < my or (iy == my and ix < mx):
                self.tag_add('sel', self.index('insert'), self.index('mark'))
            elif iy > my or (iy == my and ix > mx):
                self.tag_add('sel', self.index('mark'), self.index('insert'))

    def clipboard_replace(self, text):
        """Replace the contents of the clipboard with the given text

        :param text: The text to place on the clipboard
        """
        self.clipboard_clear()
        self.clipboard_append(text)

    def set_custom_mark(self):
        """Set the custom mark to the current insertion cursor index"""
        if self._mark is None:
            self._mark = self.index('insert')
            self.tag_remove('sel', '0.1', 'end')
            self.mark_set('mark', 'insert')
            self.mark_set('tk::anchor1', 'insert')
            self.tag_delete('sel')

    def unset_custom_mark(self):
        """Remove the custom mark from the text, removing any selection that may have been created by it"""
        if self._mark is not None:
            self._mark = None
            self.tag_remove('sel', '0.1', 'end')
            self.mark_unset('mark')
            self.mark_set('tk::anchor1', 'insert')

    def bind_multiple(self, *args):
        """Bind multiple events to this Text instance

        :param args: Tuples of (binding_string, callback) to bind
        """
        for keycode, event in args:
            self.bind(keycode, event)

    def get_index(self, mark_name: str) -> 'Tuple[int, int]':
        """Parse and return a two-tuple of (y, x) which represents the given index

        :param mark_name: The name of the mark to parse
        :returns: A two-tuple of (y, x), representing the location of the mark
        """
        px, py = self.index(mark_name).split('.', 2)
        return int(px), int(py)

    def _action_click(self, event):
        if not shift(event):
            self.unset_custom_mark()

    def _keycode_a(self, event) -> 'Optional[str]':
        # TODO: Provide key binding for selecting whole text - ctrl-a as start of line is shadows native select all
        if control(event) and not alt(event):
            y, x = self.get_index('insert')
            self.move_cursor('{}.{}'.format(y, 0))
            return "break"

    def _keycode_b(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            self.move_cursor('insert-1c')
            return "break"
        if alt(event) and not control(event):
            idx = self.search(r'\m\w+\M', 'insert', backwards=True, regexp=True, stopindex='0.1')
            self.move_cursor(idx if idx != "" else '0.1')

    def _keycode_d(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            self.delete('insert', 'insert+1c')
            return 'break'
        if alt(event) and not control(event):
            idx = self.search(r'\M', 'insert+1c', backwards=False, regexp=True, stopindex='end')
            if idx != "":
                self.delete('insert', idx)

    def _keycode_e(self, event) -> 'Optional[str]':
        if control(event)and not alt(event):
            y, x = self.get_index('insert')
            self.move_cursor('{}.end'.format(y))
            return "break"

    def _keycode_f(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            self.move_cursor('insert+1c')
            return "break"
        if alt(event) and not control(event):
            idx = self.search(r'\M', 'insert+1c', backwards=False, regexp=True, stopindex='end')
            self.move_cursor(idx if idx != '' else 'end')
            return "break"

    def _keycode_k(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            y, x = self.get_index('insert')
            text = self.get('insert', '{}.end'.format(y))
            if text != "":
                self.delete('insert', '{}.end'.format(y))
                self.clipboard_replace(text)
                self.unset_custom_mark()
            return "break"

    def _keycode_n(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            self.move_cursor('insert+1l')
            return "break"

    def _keycode_p(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            self.move_cursor('insert-1l')
            return "break"

    def _keycode_w(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            try:
                text = self.get('sel.first', 'sel.last')
                self.clipboard_clear()
                self.clipboard_append(text)
                self.delete('sel.first', 'sel.last')
                self.unset_custom_mark()
            except tkinter.TclError:
                pass
            return "break"
        if alt(event) and not control(event):
            try:
                text = self.get('sel.first', 'sel.last')
                self.clipboard_clear()
                self.clipboard_append(text)
                self.mark_unset('sel.first sel.last')
                self.unset_custom_mark()
            except tkinter.TclError:
                pass
            return "break"

    def _keycode_y(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            clipboard = self.clipboard_get()
            if clipboard != "":
                try:
                    self.delete('sel.first', 'sel.last')
                except tkinter.TclError:
                    pass
                self.insert('insert', clipboard)
            return "break"

    def _keycode_space(self, event) -> 'Optional[str]':
        if control(event) and not alt(event):
            if self._mark is not None:
                self.unset_custom_mark()
            else:
                self.set_custom_mark()

    def _keycode_backspace(self, event) -> 'Optional[str]':
        if alt(event) and not control(event):
            idx = self.search(r'\m\w+\M', 'insert', backwards=True, regexp=True)
            self.delete(idx if idx != "" else '0.1', 'insert')
            return 'break'


class VerticalScrolledFrame(tkinter.Frame):
    def __init__(self, root: tkinter.Frame, *args, **kwargs):
        tkinter.Frame.__init__(self, root, *args, **kwargs)

        self._scrollbar = tkinter.Scrollbar(self, orient="vertical")
        self._scrollbar.pack(fill='y', side="right", expand=0)

        self._canvas = tkinter.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self._scrollbar.set)
        self._canvas.pack(side='right', fill='both', expand=1)
        self._scrollbar.config(command=self._canvas.yview)

        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)
        self._interior = tkinter.Frame(self._canvas)
        self._interior_id = self._canvas.create_window(0, 0, window=self._interior, anchor='nw')

        def _configure_interior(_):
            size = (self._interior.winfo_reqwidth(), self._interior.winfo_reqheight())
            self._canvas.config(scrollregion="0 0 {} {}".format(size[0], size[1]))
            if self._interior.winfo_reqwidth() != self._canvas.winfo_width():
                self._canvas.config(width=self._interior.winfo_reqwidth())
        self._interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(_):
            if self._interior.winfo_reqwidth() != self._canvas.winfo_width():
                self._canvas.itemconfigure(self._interior_id, width=self._canvas.winfo_width())
        self._canvas.bind("<Configure>", _configure_canvas)

    def interior(self) -> tkinter.Frame:
        return self._interior

    def canvas(self) -> tkinter.Canvas:
        return self._canvas
