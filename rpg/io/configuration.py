
import ast
import os
import os.path
import platform
from rpg import util
import shutil
import typing
if typing.TYPE_CHECKING:
    from typing import Any, Optional, Tuple


class Config(object):
    @staticmethod
    def folder() -> str:
        """Get the folder where the configuration file should be read from

        :return: The folder where the configuration file should be read from
        """
        if platform.win32_ver()[0] != '':
            # This is windows
            return os.path.expandvars("%APPDATA%\\txtrpg")
        if platform.mac_ver()[0] != '':
            return os.path.expanduser("~/Library/Application Support/txtrpg")

        # Assume this is a Unix-like system
        return os.path.expanduser("~/.local/share/txtrpg")

    def __init__(self):
        self._folder = Config.folder()
        self._path = os.path.join(self._folder, "config.txt")
        self._template = './config.txt'
        self._config = {
            'log': {
                'level': 'Info',
                'file': './log.txt',
                'echo': True,
                'append': False
            }
        }

    @staticmethod
    def _fmt_key(root: 'str', key: 'str'):
        """Format a key from the given root key and current key value

        :param root: The root key of the current key
        :param key: The current key
        :return: A combination of the root and current key
        """
        return '.'.join((root, key)) if root != '' else key

    def _copy(self, config: 'dict', values: 'dict', root='') -> 'Optional[str]':
        """Copy data from the given values dictionary to the config dictionary

        :param config: The configuration dictionary to write to
        :param values: The configuration dictionary to take values from
        :param root: A root prefix used in error reporting
        :return: An optional string describing any errors when parsing the file
        """
        errors = []

        for key in values.keys():
            if key not in config:
                errors.append("Unknown Key: {}".format(Config._fmt_key(root, key)))
            else:
                config_value = config[key]
                values_value = values[key]
                cv_type = type(config_value)
                vv_type = type(values_value)
                if cv_type is not vv_type:
                    errors.append("Type mismatch for key {}: Expected {}, got {}".format(Config._fmt_key(root, key),
                                                                                         cv_type, vv_type))
                else:
                    if vv_type is dict:
                        self._copy(config_value, values_value, Config._fmt_key(root, key))
                    else:
                        config[key] = values_value

    def _copy_file(self, overwrite: bool=False) -> bool:
        """Attempt to copy the template file to the configuration folder

        :param overwrite: If the configuration file should be replaced if it already exists
        :return: If the file was written
        """
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

        if not os.path.exists(self._path):
            shutil.copy(self._template, self._path)
            return True
        elif overwrite:
            if os.path.isdir(self._path):
                os.removedirs(self._path)
            else:
                os.remove(self._path)
            shutil.copy(self._template, self._path)
            return True
        return False

    def _write_template(self, overwrite: bool=False):
        """Write the template file if possible

        This may actually run into a problem on most operating systems if installed system-wide, as writing to the
        folder may run afoul of user restrictions (C:/Program Files (x86)/, /Applications/, /usr/local/bin/ are all
        locked to administrator accounts)

        :param overwrite: If the template file should be replaced if it exists
        """
        if os.path.exists(self._template):
            if overwrite:
                if os.path.isdir(self._template):
                    os.removedirs(self._template)
                else:
                    os.remove(self._template)
            else:
                return
        with open(self._template, 'w') as fp:
            fp.write(repr(self._config))
            fp.write('\n')

    def _read_file(self) -> 'Tuple[bool, Optional[str]]':
        """Attempt to read the configuration file

        :return: A tuple of the read status and an optional error string
        """
        try:
            with open(self._path, 'r') as fp:
                data = ast.literal_eval(fp.read())
                if type(data) is dict:
                    return True, self._copy(self._config, data)
            return False, None
        except Exception as e:
            return False, util.format_exception(e, True)

    def load(self) -> 'Optional[str]':
        """Attempt to load the configuration file

        :return: An optional error string describing any errors that occurred while reading the configuration file
        """
        self._write_template(False)
        fresh = self._copy_file(False)
        good, errstr = self._read_file()
        if good:
            return errstr

        if not fresh:
            self._copy_file(True)
            good, errstr = self._read_file()
            if good:
                return errstr

        self._write_template(True)
        self._copy_file(True)
        good, errstr = self._read_file()
        return errstr

    def get(self, *keys, default: 'Any'=None) -> 'Any':
        """Read a key from the configuration object

        This method is a intended to replace a lookup like:

          config.get('system', dict()).get('log', dict()).get('level', 'Debug')
        with:
          config.get('system', 'log', 'level', default='Debug')

        :param keys: A listing of sequential keys used to look the value up
        :param default: The default value if any of the keys are missing
        :return: The value stored under the given key sequence, or None if any of the keys are missing
        """
        if len(keys) == 0:
            return default

        item = self._config
        try:
            for key in keys:
                item = item[key]
        except RuntimeError:
            return default
        except TypeError as te:
            print(util.format_exception(te, True))
            print("Keys: {}".format(repr(keys)))
        return item
