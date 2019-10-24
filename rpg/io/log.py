
from enum import IntEnum, unique

import typing
if typing.TYPE_CHECKING:
    from typing import Optional


@unique
class LogLevel(IntEnum):

    """Level descriptor for logging operations.

    """

    Debug = 0
    Verbose = 1
    Info = 2
    Warning = 3
    Error = 4
    Fatal = 5


class Log(object):

    """Wrapper around a file object which tracks a log level

    """

    _level_lookup = {
        'debug': LogLevel.Debug, 'verbose': LogLevel.Verbose, 'info': LogLevel.Info, 'warning': LogLevel.Warning,
        'error': LogLevel.Error, 'fatal': LogLevel.Fatal
    }

    @classmethod
    def parse_level(cls, level_str: 'str') -> 'Optional[LogLevel]':
        return Log._level_lookup.get(level_str.lower(), None)

    def __init__(self, echo: bool=False, level: LogLevel=LogLevel.Info) -> None:
        """Initialize the Log object

        :param echo: If this log should echo statements to standard output
        :param level: The logging level threshold
        """
        self._file_path = None  # type: Optional[str]
        self._echo = echo  # type: bool
        self._level = level  # type: LogLevel
        self._fp = None

    def level(self, level: 'Optional[LogLevel]'=None) -> LogLevel:
        """Get the logging level, optionally changing it.

        :param level: The logging level to set this log object to, or None to leave it the same
        :return: The logging level after optionally changing it
        """
        if level is not None:
            self._level = level
        return self._level

    def echo(self, on: 'Optional[bool]'=None) -> bool:
        """Get if this Log is echoing output to stdout, optionally changing said behaviour.

        :param on: If echoing should be performed, otherwise None to leave behaviour the same
        :return: If this Log object echos messages to stdout
        """
        if on is not None:
            self._echo = on
        return self._echo

    def open(self, file_path: 'str', append: bool=True) -> None:
        """Open the log file for writing.

        :param file_path: The path of the file to open
        :param append: If the log file should be opened for appending
        """
        if self._fp is None:
            self._file_path = file_path
            self._fp = open(self._file_path, "a" if append else "w")

    def close(self) -> None:
        """Close the log file"""
        if self._fp is not None:
            self._fp.close()
            self._fp = None

    def write(self, level: LogLevel, message: str, *args, **kwargs) -> bool:
        """Write a log statement with the given level if that level is at least the current log level.

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
        """Write a debug message to this log object.

        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Debug, message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> bool:
        """Write an informational message to this log object.

        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Info, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> bool:
        """Write a warning message to this log object.

        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Warning, message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> bool:
        """Write an error message to this log object.

        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Error, message, *args, **kwargs)

    def fatal(self, message: str, *args, **kwargs) -> bool:
        """Write a fatal error message to this log object.

        :param message: The message to write
        :param args: positional arguments to format into the message
        :param kwargs: keyword arguments to format into the message
        :return: If the message was written
        """
        return self.write(LogLevel.Fatal, message, *args, **kwargs)
