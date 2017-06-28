
from enum import IntEnum, unique

import typing
if typing.TYPE_CHECKING:
    from typing import Optional


@unique
class LogLevel(IntEnum):
    Debug = 0
    Info = 1
    Warning = 2
    Error = 3
    Fatal = 4


class Log(object):
    def __init__(self, file_path: str, echo: bool=False, level: LogLevel=LogLevel.Info):
        """
        :param file_path: The path name of the log file to write to
        :param echo: If this log should echo statements to standard output
        :param level: The logging level threshold
        """
        self._file_path = file_path  # type: str
        self._echo = echo  # type: bool
        self._level = level  # type: LogLevel
        self._fp = None

    def level(self, level: 'Optional[LogLevel]'=None) -> LogLevel:
        if level:
            self._level = level
        return self._level

    def echo(self, on: 'Optional[bool]'=None) -> bool:
        if on is not None:
            self._echo = on
        return self._echo

    def open(self, append: bool=True):
        """
        Open the log file for writing
        :param append: If the log file should be opened for appending
        """
        if self._fp is None:
            self._fp = open(self._file_path, "a" if append else "w")

    def close(self):
        """
        Close the log file
        """
        if self._fp is not None:
            self._fp.close()
            self._fp = None

    def write(self, level: LogLevel, message: str, *args, **kwargs) -> bool:
        """
        Write a log statement with the given level. If the level is less than the current log level nothing is written
        :param level: The logging level of this message
        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        wrote_message = False
        if level >= self._level:
            msg = "[{}] {}".format(level.name, message.format(*args, **kwargs))
            if self.echo:
                print(msg)
                wrote_message = True
            if self._fp is not None:
                self._fp.write(msg)
                self._fp.write("\n")
                wrote_message = True
        return wrote_message

    def debug(self, message: str, *args, **kwargs) -> bool:
        """
        Write a debug message to this log object
        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Debug, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> bool:
        """
        Write an informational message to this log object
        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Info, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> bool:
        """
        Write a warning message to this log object
        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Warning, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> bool:
        """
        Write an error message to this log object
        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Error, message, *args, **kwargs)

    def fatal(self, message: str, *args, **kwargs) -> bool:
        """
        Write a fatal error message to this log object
        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Fatal, message, *args, **kwargs)
