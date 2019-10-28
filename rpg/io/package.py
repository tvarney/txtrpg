
"""Defines an object used to load resource packages.

"""

import inspect
import os
import os.path
from rpg import util
from rpg.data import resource, resources
from rpg.io import module

import typing
if typing.TYPE_CHECKING:
    from rpg import app
    from rpg.io.log import Log
    from typing import List, Optional

PackageCallback = typing.Callable[[app.Game], None]
LoadResults = typing.Tuple[int, typing.Optional[str]]
_pkgLoadErrorFmt = "cannot load package from {}; {}"


class PackageLoadError(IOError):
    def __init__(self, path: str, reason: str) -> None:
        IOError.__init__(self, _pkgLoadErrorFmt.format(path, reason))


class PackageNotFoundError(FileNotFoundError):
    def __init__(self, path: str) -> None:
        FileNotFoundError.__init__(
            self,
            "Package at '{}' does not exist".format(path)
        )


class PackageContext(object):
    def __init__(self, name: str, file: str,
                 logger: 'Optional[Log]' = None) -> None:
        self.package_name = name
        self.file = file
        self._error_count = 0
        self._logger = logger

    def error(self, message: str, *args, **kwargs) -> None:
        if self._logger is not None:
            self._logger.error(message, *args, **kwargs)
        self._error_count += 1

    @property
    def error_count(self) -> int:
        return self._error_count


class Package(object):
    """A resources collection along with information identifying how it was
    loaded.
    """

    def __init__(self, path_name: 'Optional[str]' = None,
                 root_path: 'Optional[str]' = None) -> None:
        """Initialize the package instance.

        If the path_name was given then the resource located at the given path
        are loaded into the managed Resources collection.

        :param path_name: A path name to load resources from
        :param root_path: The root path resources are loaded from
        """
        self._name = ""
        self._path = ""
        self._is_dir = False
        self._is_file = False
        self._author = None          # type: Optional[str]
        self._version = None         # type: Optional[str]
        self._dependencies = list()  # type: List[str]
        self._init = list()          # type: List[Optional[PackageCallback]]
        self._finalize = list()      # type: List[Optional[PackageCallback]]

        # Public Data Members
        self.include = True
        self.resources = resources.Resources()

        if path_name:
            self.load(path_name, root_path)

    def load(self, path_name: str,
             root_path: 'Optional[str]' = None,
             ctx: 'Optional[PackageContext]' = None) -> int:
        """Load data from the given path, using the root_path option if
        provided to parse the name of the package.

        :param path_name: The path to load the package from
        :param root_path: A base root used to derive the name of the package
                          from
        :param ctx: A PackageContext object to use to log errors
        :return: A tuple with how many resources were loaded and an optional
                 error string
        """
        if not os.path.exists(path_name):
            raise PackageNotFoundError(path_name)

        if ctx is None:
            ctx = PackageContext("", "")

        self._is_dir = os.path.isdir(path_name)
        self._is_file = os.path.isfile(path_name)
        self._path = path_name

        if self._is_dir:
            self._name = os.path.normpath(
                os.path.relpath(path_name, root_path)
            )
            ctx.package_name = self._name
            return self._load_dir(ctx, path_name, root_path)
        elif self._is_file:
            self._name = os.path.splitext(
                os.path.normpath(os.path.relpath(path_name, root_path))
            )[0]
            ctx.package_name = self._name
            ctx.file = path_name
            return self._load_file(ctx, path_name, root_path)

        # The path points to something which is not a file or directory
        raise PackageLoadError(path_name, "not a file or directory")

    @property
    def is_dir(self) -> bool:
        """Check if this package was loaded from a directory based package.

        :return: If this package was loaded from a directory
        """
        return self._is_dir

    @property
    def is_file(self) -> bool:
        """Check if this package was loaded from a single file.

        :return: If this package was loaded from a single file.
        """
        return self._is_file

    @property
    def is_loaded(self) -> bool:
        """Check if this package has been loaded.

        :return: If this package has loaded all available data from the package
                 definition.
        """
        return self._path is not None and (self.is_dir or self.is_file)

    @property
    def name(self) -> 'Optional[str]':
        """Get the name of the package.

        This name is determined by the Package.load(...) method, which uses the
        file or directory name as the name of the package. Package names are
        used to check masters when merging Resources collections.

        :return: The name of the package
        """
        return self._name

    @property
    def author(self) -> 'Optional[str]':
        """Get the author(s) of the package.

        The value returned by this is defined by a package variable 'Author'
        which must be a string.

        :return: The author of the package
        """
        return self._author

    @property
    def version(self) -> 'Optional[str]':
        """Get the version of the package.

        The value returned by this is defined by a package variable 'Version'
        which must be a string.

        :return: The version of the package
        """
        return self._version

    @property
    def dependencies(self) -> 'Optional[List[str]]':
        """Get a list of package names which this package depends on being
        loaded prior to it.

        The value returned by this is defined by a package variable
        'Dependencies' which must be a list of strings.

        :return: A list of package names which this package depends on being
                 loaded prior to it
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
                game.log.error(
                    "Exception in initialize function {}:\n{}",
                    func.__name__, util.format_exception(e)
                )

    def finalize(self, game: 'app.Game') -> None:
        """Call finalization callbacks defined in this package.

        :param game: The app.Game instance to run finalization routines for
        """
        for func in self._finalize:
            try:
                func(game)
            except Exception as e:
                game.log.error(
                    "Exception in finalize function {}:\n{}",
                    func.__name__, util.format_exception(e)
                )

    def _load_dir(self, ctx: 'PackageContext', dir_path: str,
                  root_path: 'Optional[str]' = None) -> int:
        """Load all files from the given directory.

        This method is recursively called for all subdirectories located in the
        package. This method does not set the package name. This method is
        private; use the Package.load(...) method instead.

        :param dir_path: The directory path to load resources from
        :param root_path: A base root directory from which to derive the
                          package name from
        :return: A tuple with how many resources were loaded and an optional
                 error string
        """
        loaded_items = 0

        for file_name in os.listdir(dir_path):
            # Skip the compiled cache folder if it exists
            if file_name == "__pycache__":
                continue

            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                ctx.file = file_path
                count = self._load_file(ctx, file_path, root_path)
                loaded_items += count
            elif os.path.isdir(file_path):
                count = self._load_dir(ctx, file_path, root_path)
                loaded_items += count

        return loaded_items

    def _load_file(self, ctx: 'PackageContext', file_path: str,
                   root_path: 'Optional[str]' = None) -> int:
        """Load all resource from the given file.

        This method does not set the package name. This method is private; use
        the Package.load(...) method instead.

        :param file_path: The path to the file to load
        :param root_path: A base directory from which to derive the package
                          name from
        :return: A tuple with how many resource were loaded and an optional
                 error string
        """
        _loaded_items = 0

        # This is all wrapped in a try block so we can report exceptions while
        # loading in the error string
        try:
            # It might be worth holding onto the module object, but that isn't
            # happening (yet)
            _module = module.load_from_file(file_path, root_path)

            # Attempt to get the author package variable
            _author = getattr(_module, "Author", None)
            if _author is not None:
                if type(_author) is not str:
                    ctx.error("Special variable Author is not a string")
                else:
                    self._author = _author

            # Attempt to get the version package variable
            _version = getattr(_module, "Version", None)
            if _version is not None:
                if type(_version) is not str:
                    ctx.error("Special variable Version is not a string")
                else:
                    self._version = _version

            # Attempt to get the dependencies package variable; unlike author
            # and version variables, the values in dependencies are appended to
            # the list of dependencies tracked by this package.
            # TODO: Clear the dependencies when reloading the package
            _dependencies: 'List[str]'
            _dependencies = getattr(_module, "Dependencies", None)
            if _dependencies is not None:
                try:
                    for dep in _dependencies:
                        if dep not in self._dependencies:
                            self._dependencies.append(dep)
                except Exception as e:
                    ctx.error("Could not add dependencies from module: {}", e)

            # Get all Resource classes and objects defined by the module
            for _item_name in dir(_module):
                # Skip item names which start with an underscore
                if _item_name.startswith("_"):
                    continue

                # Get the object from the module
                _package_obj = getattr(_module, _item_name)
                # If it is a class, we want to try to create an instance of it
                # and add that to the Resources collection
                if inspect.isclass(_package_obj):
                    _package_cls = _package_obj
                    if issubclass(_package_cls, resource.Resource):
                        # Again, wrap this specifically to avoid a class from
                        # aborting the load on the entire file
                        try:
                            _package_obj = _package_cls()
                            self.resources.add(_package_obj)
                            _loaded_items += 1
                        except Exception as e:
                            ctx.error(
                                "Could not add Resource from class {}: {}",
                                _package_cls, e
                            )
                else:
                    # Otherwise, this is an instance object already; just
                    # attempt to add it to the Resources collection
                    if issubclass(type(_package_obj), resource.Resource):
                        self.resources.add(_package_obj)
                        _loaded_items += 1
        except Exception as e:
            ctx.error(util.format_exception(e, True))

        return _loaded_items
