
import tkinter as tk
from rpg import util
from rpg.ui import widgets

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import Any, Optional


class ConsoleState(object):

    """Definition of the state of the debug console

    This class defines all members of the console required to run code through it. This can be used to evaluate scripts.

    """

    def __init__(self, game: 'app.Game') -> None:
        self.history = list()
        self.environ = {'game': game, 'console': self, 'print': self.print, 'close': self.close, 'reset': self.reset,
                        'clear': self.clear}
        self._saved_state = dict(self.environ)
        self._game = game
        self._window = None

    def bind(self, console_window: 'ConsoleWindow') -> None:
        """Bind the ConsoleState to a given ConsoleWindow instance

        :param console_window: The window to bind this state to
        """
        self._window = console_window

    def unbind(self) -> None:
        """Unbind the ConsoleState from the bound ConsoleWindow"""
        self._window = None

    def clear(self) -> None:
        """Clear the ConsoleWindow if bound"""
        if self._window is not None:
            self._window.clear()

    def close(self) -> None:
        """Close the ConsoleWindow if bound"""
        if self._window is not None:
            self._window.close()

    def reset(self) -> None:
        """Reset the ConsoleState to the initial state"""
        self.environ = dict(self._saved_state)
        self.history.clear()
        self.clear()

    def print(self, *objects, sep='', end='\n', file=None) -> None:
        """Print replacement which writes to a bound ConsoleWindow

        :param objects: The objects to print
        :param sep: The string used to separate the objects being printed (default='')
        :param end: The string to terminate the printed string with (default='\n')
        :param file: An IO object to write the string to (default=None)
        """
        if file is not None:
            file.write(sep.join(str(obj) for obj in objects) + end)
        else:
            if self._window is not None:
                self._window.print(*objects, sep=sep, end=end)
            else:
                print(*objects, sep=sep, end=end)

    def evaluate(self, code_string) -> 'Any':
        """Attempt to run some code against the ConsoleState

        This method does not attempt to do any kind of sandboxing as that is not possible. This means that the user
        of the debug console is able to run any valid python program.

        :param code_string: The code to evaluate
        :return: The results of evaluating the code
        """
        # Ensure that game and console are always correct
        code_string = code_string.strip()

        # The exception here is thrown away on purpose
        # noinspection PyBroadException
        try:
            return eval(code_string, self.environ)
        except Exception as _:
            pass
        # Let any exceptions thrown here be passed up to the caller
        exec(code_string, self.environ)


class ConsoleWindow(tk.Toplevel):

    """A window which allows a user to interact with a ConsoleState object

    """

    def __init__(self, root: 'tk.Tk', state: ConsoleState, **kwargs) -> None:
        # noinspection PyCallByClass,PyTypeChecker
        tk.Toplevel.__init__(self, root, **kwargs)  # For some reason, aliasing tkinter to tk causes warnings here
        self.protocol("WM_DELETE_WINDOW", self.close)

        self._closing = False

        self._state = state
        self._state.bind(self)
        self._hist_line = 0
        self._stash = ""

        self._frame = tk.Frame(self)
        self._scrollOutput = tk.Scrollbar(self._frame)
        self._scrollInput = tk.Scrollbar(self._frame)
        self._txtOutput = widgets.StaticTextArea(self._frame, yscrollcommand=self._scrollOutput.set)
        self._txtInput = widgets.CustomTextArea(self._frame, height=1, yscrollcommand=self._scrollInput.set)

        self._txtInput.bind("<Return>", self._on_enter)
        self._txtInput.bind("<Up>", self._arrow_up)  # Move to previous history line
        self._txtInput.bind("<Down>", self._arrow_down)  # Move to next history line
        self._txtInput.bind("<D>", lambda e: self.close() if widgets.control(e) and not widgets.alt(e) else None)

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

    def clear(self) -> None:
        """Remove all text in the ConsoleWindow"""
        self._txtOutput.delete('1.0', 'end')

    def close(self) -> None:
        """Close the ConsoleWindow object and unbind from the ConsoleState"""
        self._state.unbind()
        self._closing = True
        self.destroy()

    def print(self, *objects, sep='', end='\n') -> None:
        """Replacement for the print function

        :param objects: The objects to print
        :param sep: The string used to separate the objects to be printed
        :param end: The string used to terminate the string being printed
        """
        txt_result = sep.join(str(obj) for obj in objects) + end
        self._txtOutput.insert("end", txt_result, "o")
        self._txtOutput.see('end')

    def _on_enter(self, event) -> 'Optional[str]':
        """Handle the "Enter" or "Return" key

        This method will evaluate the code in the input text box as python code, using the ConsoleState object bound
        to it to execute the code.

        :param event: The event to process
        :return: "break" if the event was handled, or None
        """
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
                if not self._closing:
                    self._txtOutput.insert('end', "{}\n".format(repr(return_value)), "o")
        except Exception as e:
            if not self._closing:
                self._txtOutput.insert("end", util.format_exception(e), "e")

        # Make sure the output is focused at the end of the text in it
        if not self._closing:
            self._txtOutput.see("end")
        return "break"

    def _arrow_up(self, _) -> 'Optional[str]':
        """Handle the up arrow key

        :param _: The event (ignored)
        :return: "break" if the event was handled or None
        """
        y, x = self._txtInput.get_index('insert')
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

    def _arrow_down(self, _) -> 'Optional[str]':
        """Handle the down arrow

        :param _: The event (ignored)
        :return: "break" if the event was handled or None
        """
        y, x = self._txtInput.get_index('insert')
        max_y, max_x = self._txtInput.get_index('end')
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
