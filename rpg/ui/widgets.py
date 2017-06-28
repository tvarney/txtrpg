
import tkinter

import typing
if typing.TYPE_CHECKING:
    from typing import Callable


class Button(tkinter.Button):
    """
    Wrapper around a tkinter.Button which supports setting the text and command on initialization
    """
    def __init__(self, root: tkinter.Frame, text: str, command: 'Callable', *args, **kwargs):
        tkinter.Button.__init__(self, root, *args, **kwargs)
        self['text'] = text
        self['command'] = command


class LabeledEntry(tkinter.Frame):
    def __init__(self, root: tkinter.Frame, label: str, entry_size: int=20, orientation: str=tkinter.LEFT):
        tkinter.Frame.__init__(self, root)
        self.label = tkinter.Label(self, text=label)
        self.entry = tkinter.Entry(self)
        self.entry.config(width=entry_size)

        self.label.pack(side=orientation)
        self.entry.pack(side=orientation)


class LabeledVariable(tkinter.Frame):
    def __init__(self, root: tkinter.Frame, label: str, var=None, **kwargs):
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

        orientation=tkinter.LEFT
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

        self.label.pack(orientation=orientation)
        self.variable.pack(orientation=orientation)
        self.configure(kwargs)

    def get_variable(self):
        return self._variable


class StaticTextArea(tkinter.Text):
    """
    Wrapper around a tkinter.Text object to provide a simple text area which can not be edited.

    The insert and delete methods are overloaded to correctly work with a disabled tkinter.Text object
    """
    def __init__(self, root: tkinter.Frame, *args, **kwargs):
        tkinter.Text.__init__(self, root, *args, **kwargs)
        self.tag_config("wrap", wrap=tkinter.WORD)
        self.config(state='disabled')

    def insert(self, index, chars, *args):
        """
        Insert text into the text area starting at the given index

        Text inserted with this method automatically has the "wrap" tag applied to it which wraps on word boundaries.
        :param index: The index to insert the text at
        :param chars: The text to insert at the given index
        :param args: tags for the inserted text
        """
        self.config(state='normal')
        tkinter.Text.insert(self, index, chars, "wrap", *args)
        self.config(state='disabled')

    def delete(self, index1, index2=None):
        """
        Delete text between the two indices

        If the second index is None (the default value), then the deletion will remove all text after the first index
        :param index1: The starting index to delete from
        :param index2: The end index to delete to
        """
        self.config(state='normal')
        tkinter.Text.delete(self, index1, index2)
        self.config(state='disabled')

    def replace(self, chars, *tags):
        """
        Replace all text in the text instance with the given text
        :param chars: The new text to display
        :param tags: Any tags to apply to the text
        """
        self.config(state='normal')
        tkinter.Text.delete(self, 1.0, 'end')
        tkinter.Text.insert(self, 'end', chars, "wrap", *tags)
        self.config(state='disabled')

    def clear(self):
        """
        Alias to the delete method which removes all text
        """
        self.delete(1.0, 'end')


