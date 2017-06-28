
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
    def __init__(self, path_name: 'Optional[str]'=None):
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
        self.include = False  # type: bool
        self.resources = resources.Resources()

        if path_name:
            self.load(path_name)

    def load(self, path_name: str) -> int:
        if not os.path.exists(path_name):
            raise FileNotFoundError("Path '{}' does not exist".format(path_name))

        self._is_dir = os.path.isdir(path_name)
        self._is_file = os.path.isfile(path_name)
        self._path = path_name

        if self._is_dir:
            return self._load_dir(path_name)
        elif self._is_file:
            return self._load_file(path_name)
        else:
            raise IOError("Path '{}' is neither a file nor directory".format(path_name))

    def is_directory(self) -> bool:
        return self._is_dir

    def is_file(self) -> bool:
        return self._is_file

    def is_loaded(self) -> bool:
        return self._path is not None and (self.is_directory() or self.is_file())

    def author(self) -> 'Optional[str]':
        return self._author

    def version(self) -> 'Optional[str]':
        return self._version

    def dependencies(self) -> 'Optional[List[str]]':
        return self._dependencies

    def initialize(self, game: 'app.Game'):
        for func in self._init:
            try:
                func(game)
            except Exception as e:
                game.log.error("Exception in initialize function {}: {}\n{}", func.__name__, e, e.__traceback__)

    def finalize(self, game: 'app.Game'):
        for func in self._finalize:
            try:
                func(game)
            except Exception as e:
                game.log.error("Exception in finalize function {}: {}\n{}", func.__name__, e, e.__traceback__)

    def _load_dir(self, dir_path: str, root_path: 'Optional[str]'=None) -> 'Tuple[int, Optional[str]]':
        loaded_items = 0
        err_str = ""

        for file_name in os.listdir(dir_path):
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
    
    def _load_file(self, file_path: str, root_path: 'Optional[str]'=None) -> Tuple[int, Optional[str]]:
        _loaded_items = 0
        _err_str = ""
        try:
            _module = module.load_from_file(file_path, root_path)
            _author = getattr(_module, "Author", None)
            if _author is not None:
                if type(_author) is not str:
                    _err_str += "Value of special symbol 'Author' is not a string\n"
                else:
                    self._author = _author
            _version = getattr(_module, "Version", None)
            if _version is not None:
                if type(_version) is not str:
                    _err_str += "Value of special symbol 'Version' is not a string\n"
                else:
                    self._version = _version

            _dependencies = getattr(_module, "Dependencies", None)  # type: List[str]
            if _dependencies is not None:
                try:
                    for dep in _dependencies:
                        if dep not in self._dependencies:
                            self._dependencies.append(dep)
                except Exception as e:
                    _err_str += "Could not add dependencies from module: {}\n".format(e)

            for _item_name in dir(_module):
                if _item_name.startswith("_"):
                    continue

                _package_obj = getattr(_module, _item_name)
                if inspect.isclass(_package_obj):
                    _package_cls = _package_obj
                    if issubclass(type(_package_cls), resource.Resource):
                        try:
                            _package_obj = _package_cls()
                            self.resources.add(_package_obj)
                        except Exception as e:
                            _err_str += "Could not add Resource from class {}: {}\n".format(_package_cls, e)
                else:
                    if issubclass(type(_package_obj), resource.Resource):
                        self.resources.add(_package_obj)
        except Exception as e:
            _err_str += "{}:\n{}".format(e, e.__traceback__)
        return _loaded_items, (_err_str if _err_str != "" else None)
