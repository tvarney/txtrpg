
"""Defines an object used to load resource packages.

"""

import inspect
import os
import os.path
from rpg.data import resource, resources
from rpg.io import module

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from typing import Callable, List, Optional, Tuple


class Package(object):

    """A resources collection along with information identifying how it was loaded.

    """

    def __init__(self, path_name: 'Optional[str]'=None, root_path: 'Optional[str]'=None) -> None:
        """Initialize the package instance.

        If the path_name was given then the resource located at the given path are loaded into the managed Resources
        collection.

        :param path_name: A path name to load resources from, or None to delay this operation
        :param root_path: A base root from which the resource package name can be derived
        """
        self._name = ""
        self._path = ""
        self._is_dir = False  # type: bool
        self._is_file = False  # type: bool

        self._author = None  # type: Optional[str]
        self._version = None  # type: Optional[str]
        self._dependencies = list()  # type: List[str]
        self._init = list()  # type: List[Optional[Callable[[app.Game], None]]]
        self._finalize = list()  # type: List[Optional[Callable[[app.Game], None]]]

        # Public Data Members
        self.include = True  # type: bool
        self.resources = resources.Resources()

        if path_name:
            self.load(path_name, root_path)

    def load(self, path_name: str, root_path: 'Optional[str]'=None) -> 'Tuple[int, Optional[str]]':
        """Load data from the given path, using the root_path option if provided to parse the name of the package.

        :param path_name: The path to load the package from
        :param root_path: A base root used to derive the name of the package from
        :return: A tuple with how many resources were loaded and an optional error string
        """
        if not os.path.exists(path_name):
            raise FileNotFoundError("Path '{}' does not exist".format(path_name))

        self._is_dir = os.path.isdir(path_name)
        self._is_file = os.path.isfile(path_name)
        self._path = path_name

        if self._is_dir:
            resource_count, err_str = self._load_dir(path_name, root_path)
            if self._name is None or self._name == "":
                self._name = os.path.normpath(os.path.relpath(path_name, root_path))
            return resource_count, err_str
        elif self._is_file:
            resource_count, err_str = self._load_file(path_name, root_path)
            if self._name is None or self._name == "":
                self._name = os.path.splitext(os.path.normpath(os.path.relpath(path_name, root_path)))[0]
            return resource_count, err_str
        else:
            raise IOError("Path '{}' is neither a file nor directory".format(path_name))

    def is_directory(self) -> bool:
        """Check if this package was loaded from a directory based package.

        :return: If this package was loaded from a directory
        """
        return self._is_dir

    def is_file(self) -> bool:
        """Check if this package was loaded from a single file.

        :return: If this package was loaded from a single file.
        """
        return self._is_file

    def is_loaded(self) -> bool:
        """Check if this package has been loaded.

        :return: If this package has loaded all available data from the package definition
        """
        return self._path is not None and (self.is_directory() or self.is_file())

    def name(self) -> 'Optional[str]':
        """Get the name of the package.

        This name is determined by the Package.load(...) method, which uses the file or directory name as the name of
        the package.

        Package names are used to check masters when merging Resources collections.

        :return: The name of the package
        """
        return self._name

    def author(self) -> 'Optional[str]':
        """Get the author(s) of the package.

        The value returned by this is defined by a package variable 'Author' which must be a string.

        :return: The author of the package
        """
        return self._author

    def version(self) -> 'Optional[str]':
        """Get the version of the package.

        The value returned by this is defined by a package variable 'Version' which must be a string.

        :return: The version of the package
        """
        return self._version

    def dependencies(self) -> 'Optional[List[str]]':
        """Get a list of package names which this package depends on being loaded prior to it.

        The value returned by this is defined by a package variable 'Dependencies' which must be a list of strings.

        :return: A list of package names which this package depends on being loaded prior to it
        """
        return self._dependencies

    def initialize(self, game: 'app.Game') -> None:
        """Call initialization callbacks defined in this package.

        :param game: The app.Game instance to initialize this package for
        """
        for func in self._init:
            try:
                func(game)
            except Exception as e:
                game.log.error("Exception in initialize function {}: {}\n{}", func.__name__, e, e.__traceback__)

    def finalize(self, game: 'app.Game') -> None:
        """Call finalization callbacks defined in this package.

        :param game: The app.Game instance to run finalization routines for
        """
        for func in self._finalize:
            try:
                func(game)
            except Exception as e:
                game.log.error("Exception in finalize function {}: {}\n{}", func.__name__, e, e.__traceback__)

    def _load_dir(self, dir_path: str, root_path: 'Optional[str]'=None) -> 'Tuple[int, Optional[str]]':
        """Load all files from the given directory.

        This method is recursively called for all subdirectories located in the package. This method does not set the
        package name. This method is private; use the Package.load(...) method instead.

        :param dir_path: The directory path to load resources from
        :param root_path: A base root directory from which to derive the package name from
        :return: A tuple with how many resources were loaded and an optional error string
        """
        loaded_items = 0
        err_str = ""

        for file_name in os.listdir(dir_path):
            if file_name == "__pycache__":
                continue

            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                file_loaded_items, file_errors = self._load_file(file_path, root_path)
                loaded_items += file_loaded_items
                if file_errors is not None and file_errors != "":
                    err_str += "Errors loading package file '{}':\n\n{}\n\n".format(file_path, file_errors)
            elif os.path.isdir(file_path):
                file_loaded_items, file_errors = self._load_dir(file_path, root_path)
                loaded_items += file_loaded_items
                if file_errors is not None and file_errors != "":
                    err_str += file_errors

        return loaded_items, (err_str if err_str != "" else None)

    def _load_file(self, file_path: str, root_path: 'Optional[str]'=None) -> 'Tuple[int, Optional[str]]':
        """Load all resource from the given file.

        This method does not set the package name. This method is private; use the Package.load(...) method instead.

        :param file_path: The path to the file to load
        :param root_path: A base directory from which to derive the package name from
        :return: A tuple with how many resource were loaded and an optional error string
        """
        _loaded_items = 0
        _err_str = ""
        # This is all wrapped in a try block so we can report exceptions while loading in the error string
        try:
            # It might be worth holding onto the module object, but that isn't happening (yet)
            _module = module.load_from_file(file_path, root_path)

            # Attempt to get the author package variable
            _author = getattr(_module, "Author", None)
            if _author is not None:
                if type(_author) is not str:
                    _err_str += "Value of special symbol 'Author' is not a string\n"
                else:
                    self._author = _author

            # Attempt to get the version package variable
            _version = getattr(_module, "Version", None)
            if _version is not None:
                if type(_version) is not str:
                    _err_str += "Value of special symbol 'Version' is not a string\n"
                else:
                    self._version = _version

            # Attempt to get the dependencies package variable; unlike author and version variables, the values in
            # dependencies are appended to the list of dependencies tracked by this package.
            # TODO: Clear the dependencies when reloading the package
            _dependencies = getattr(_module, "Dependencies", None)  # type: List[str]
            if _dependencies is not None:
                try:
                    for dep in _dependencies:
                        if dep not in self._dependencies:
                            self._dependencies.append(dep)
                except Exception as e:
                    _err_str += "Could not add dependencies from module: {}\n".format(e)

            # Get all Resource classes and objects defined by the module
            for _item_name in dir(_module):
                # Skip item names which start with an underscore
                if _item_name.startswith("_"):
                    continue

                # Get the object from the module
                _package_obj = getattr(_module, _item_name)
                # If it is a class, we want to try to create an instance of it and add that to the Resources collection
                if inspect.isclass(_package_obj):
                    _package_cls = _package_obj
                    if issubclass(_package_cls, resource.Resource):
                        # Again, wrap this specifically to avoid a class from aborting the load on the entire file
                        try:
                            _package_obj = _package_cls()
                            self.resources.add(_package_obj)
                            _loaded_items += 1
                        except Exception as e:
                            _err_str += "Could not add Resource from class {}: {}\n".format(_package_cls, e)
                else:
                    # Otherwise, this is an instance object already; just attempt to add it to the Resources collection
                    if issubclass(type(_package_obj), resource.Resource):
                        self.resources.add(_package_obj)
                        _loaded_items += 1
        except Exception as e:
            _err_str += "{}:\n{}".format(e, str(e.__traceback__))

        # We want to return None for the error string if no errors occurred so error checking is as simple as:
        #    num, errstr = pkg.load(...)
        #    if errstr is not None:
        #        pass
        return _loaded_items, (_err_str if _err_str != "" else None)
