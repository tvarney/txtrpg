
"""Definition of the main Game controller class.

"""

import io
import os
import os.path
import random
from rpg import state, util
from rpg.io import configuration, log, package
from rpg.ui import components, views
import sys
import tkinter

import typing
if typing.TYPE_CHECKING:
    from typing import List, Optional, TypeVar, Union
    NoReturn = TypeVar('NoReturn')


class Game(object):
    """The main Game application definition.

    This class controls the application lifetime and can be used to access
    various parts of the application.
    """

    def __init__(self) -> None:
        """Initialize the Game app.

        This does not initialize the tkinter.Tk() root, but sets up the various
        objects that the application needs.
        """
        self._root = None                     # type: Optional[tkinter.Tk]
        self._packages = list()               # type: List[package.Package]
        self._return_value = 0                # type: int
        self._initial_view = None             # type: None
        self.log = log.Log()                  # type: log.Log
        self.stack = views.ViewManager(self)  # type: views.ViewManager
        self.state = state.GameData(self)     # type: state.GameData
        self.random = random.Random()
        self._config = configuration.Config({
            'log': configuration.Map({
                'level': configuration.Enum(
                    allowed=(
                        "Debug", "Verbose", "Info", "Warning", "Error", "Fatal"
                    ),
                    default="Info"
                ),
                'file': configuration.String(
                    default="./log.txt", allow_empty=False
                ),
                'echo': configuration.Boolean(default=True),
                'append': configuration.Boolean(default=False),
            })
        })

    def root(self) -> 'Optional[Union[tkinter.Tk, tkinter.Frame]]':
        """Get the root tkinter frame.

        :return: The tkinter root window if initialized or None
        """
        return self._root

    def quit(self, return_value: int = 0) -> None:
        """Destroy the tkinter window and exit the application.

        :param return_value: The return value to quit with
        """
        if self._root:
            root = self._root
            self._root = None

            root.quit()
            root.destroy()
            self._return_value = return_value

    def build_resources(self) -> int:
        """Merges resources from all selected packages into the
        self.state.resources Resources collection."""
        self.log.debug("Building Resources...")
        package_count = 0
        self.state.resources.clear()
        for pkg in self._packages:
            if pkg.include:
                self.log.debug("   merging '{}'...", pkg.name)
                err = self.state.resources.merge(
                    pkg.resources, pkg.dependencies
                )
                if err is not None:
                    self.log.warning(
                        "Errors occurred while merging '{}':\n{}",
                        pkg.name, err
                    )
                package_count += 1
        self.log.debug("Built Resources: Included {} packages", package_count)
        return package_count

    def run(self) -> int:
        """Run the application.

        :return: The return value specified by the first call to
                 Application.quit()
        """
        # Read the configuration
        errstr = ""
        filename = os.path.join(configuration.Config.folder(), "config.yaml")
        if os.path.exists(filename):
            ctx = configuration.Context()
            ctx.writer = io.StringIO()
            self._config.load(filename, None, ctx)
            errstr = ctx.writer.getvalue()
        else:
            self._config.save(filename)

        # Configure the log
        append = self._config.log.append.value  # type: bool
        filename = self._config.log.file.value
        self.log.open(filename, append)

        level_str = self._config.log.level.value  # type: str
        level = log.Log.parse_level(level_str)
        if level is not None:
            self.log.level(level)

        self.log.echo(self._config.log.echo.value)

        # If there were any errors reading the configuration, log them now
        if errstr != "":
            self.log.error("Errors in configuration:\n{}", errstr)

        # Initialize the root window
        self._root = tkinter.Tk()
        # Set a minimum size
        # TODO: save the geometry in some settings file somewhere and use the
        #       last saved size
        self._root.geometry("800x600")
        self._root.minsize(800, 600)

        # Add the root menu
        self._root.config(menu=components.RootMenuBar(self))

        # Load data - this just creates the package listing which can be
        # toggled on/off
        self._load_packages("./data/packages")
        # TODO: load a package list which saves package name/include so we can
        #       persist package selection

        self.stack.load_views()
        if self.stack.initial_view() is None:
            self._abort("No initial view defined")
        self.stack.push(self.stack.initial_view())

        try:
            tkinter.mainloop()
        except Exception as e:
            # This will force a full shutdown
            self._abort(
                "Caught Exception at top level:\n{}",
                util.format_exception(e)
            )

        self.stack.finalize()
        self.stack.clear_views()
        self.log.close()
        return self._return_value

    def _abort(self, message, *vargs, **kwargs) -> None:
        """Private method used to abort the application instantly from
        anywhere.

        This method will call sys.exit(-1); any code which would normally run
        after the run() method returned will not be run after this.

        :param message: The message to log
        :param vargs: Positional arguments to format into the message
        :param kwargs: Keyword arguments to format into the message
        """
        self.log.fatal(message, *vargs, **kwargs)
        self.log.close()
        self._root.destroy()
        self._root = None
        sys.exit(-1)

    def _load_packages(self, root_path: str) -> None:
        """Load all packages located under the root_path given.

        :param root_path: The root path from which to load packages
        """
        self._packages.clear()
        for file_name in os.listdir(root_path):
            # Skip any name which starts with an underscore (private, also used
            # by __pycache__)
            if file_name.startswith("_"):
                continue

            self.log.debug("Attempting to load package from {}", file_name)
            file_path = os.path.join(root_path, file_name)
            _package = package.Package()
            ctx = package.PackageContext("", "", self.log)
            resource_count = _package.load(file_path, root_path, ctx)
            if ctx.error_count == 0:
                self._packages.append(_package)
                self.log.debug("Loaded package: {}", _package.name)
                self.log.debug("  Loaded {} resources", resource_count)
