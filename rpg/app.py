
from rpg.io import log
import sys
import tkinter

import typing
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from typing import ModuleType


class Game(object):
    def __init__(self):
        self._root = None  # type: Optional[tkinter.Tk]
        self._modules = dict()  # type: Dict[ModuleType]
        self._return_value = 0  # type: int
        self._initial_view = None  # type: None
        
        self.resources = None  # type: None
        self.stack = None  # type: None
        self.state = None  # type: None
        self.log = log.Log  # type: log.Log

    def root(self) -> 'Optional[tkinter.Frame]':
        """Get the root tkinter frame
        :return: The tkinter root window if initialized or None
        """
        return self._root

    def quit(self, return_value: int=0):
        """Destroy the tkinter window and exit the application
        :param return_value: The return value to quit with
        """
        if self._root:
            root = self._root
            self._root = None

            root.quit()
            root.destroy()
            self._return_value = return_value

    def run(self) -> int:
        """Run the application
        :return: The return value specified by the first call to Application.quit()
        """
        self._root = tkinter.Tk()
        # Set a minimum size
        # TODO: save the geometry in some settings file somewhere and use the last saved size
        self._root.geometry("800x600")
        self._root.minsize(800, 600)

        try:
            tkinter.mainloop()
        except Exception as e:
            # This will force a full shutdown
            self._abort("Caught Exception at top level: {}\n{}", e, e.__traceback__)

        return self._return_value

    def _abort(self, message, *vargs):
        print()
        self._root.destroy()
        self._root = None
        sys.exit(-1)
