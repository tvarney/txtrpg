
"""Definitions of general purpose aggregate widgets.

This module is used for classes which aggregate tkinter widgets in a way that they are general purpose.

"""

import tkinter

import typing
if typing.TYPE_CHECKING:
    from typing import Callable, Optional


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
        self._variable = var if var is not None else tkinter.StringVar()

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

        if "font" in kwargs:
            font = kwargs["font"]
            cnf_lbl["font"] = font
            cnf_var["font"] = font
            del kwargs["font"]

        cnf_lbl["text"] = label
        cnf_var["textvariable"] = self._variable

        self.label = tkinter.Label(self, **cnf_lbl)
        self.variable = tkinter.Label(self, **cnf_var)

        self.label.pack(side=orientation)
        self.variable.pack(side=orientation)
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
        tkinter.Text.insert(self, index, chars, "wrap", *args)
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
