
import importlib
import importlib.util
import os
import os.path

import typing
if typing.TYPE_CHECKING:
    from types import ModuleType
    from typing import Optional


def parse_name(path: str, root: 'Optional[str]'=None) -> str:
    """Generate a name for a python module based on the given path.

    :param path: The path to parse into a name
    :param root: A root path for this file
    :return: A name for a python module at the given path
    """
    name = os.path.splitext(os.path.normpath(os.path.relpath(path, root)))[0]
    return name.replace(os.sep, ".")


def load_from_file(path: str, root: 'Optional[str]'=None, name: 'Optional[str]'=None) -> 'ModuleType':
    """Load a module from the filesystem and return its module object.

    :param path: The path to the module file
    :param root: The root path to ignore - used when naming the module
    :param name: The name of the module; see module.parse_name()
    :return: The module object of the python module located at the given path
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    if name is None:
        name = parse_name(path, root)

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise RuntimeError("Could not load python module from " + path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reload(module_obj: 'ModuleType') -> 'ModuleType':
    """Reload a module which has already been loaded.

    :param module_obj: The module object to reload
    :return: A reference to the module after re-loading it
    """
    return importlib.reload(module_obj)
