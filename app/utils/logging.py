# Internal modules
from logging import getLogger, basicConfig, Formatter, Filter, LogRecord, INFO, Logger as L
from logging.handlers import RotatingFileHandler
from os import getenv
from os.path import relpath
from typing import Optional

# External modules
from dotenv import load_dotenv

from ..graphql.lib.types import Snowflake
# Internal Modules
from ..lib.types import FilterLevels, filter_args

load_dotenv()


def rel(file: str) -> str:
    return relpath(file, getenv('START_PATH')).replace("/", ".").replace('.py', '')


class Logger:
    """
    A wrapper for the logging module that provides advanced features. Gives complete control over logging and
    encapsulates common logging function such as error, info, exception, etc. providing them with defaults args. Allows
    easy integration of logging into complex systems in order to track event and debug errors.

    :param file_name: The file to log to.
    :param module: __name__ of the current module.
    :param exc_info: Provides should exc_info be provided for level >20<=30 log messages?
    :param stack_info: Should stack_info be provided for level >30 messages?
    """

    def __init__(self, file_name: str, module: str, exc_info: bool = True, stack_info: bool = True):
        basicConfig()
        self._lvl_filter = None
        self._file = rel(file_name)
        self._exc_info = exc_info
        self._stack_info = stack_info
        self._logger = getLogger(module)
        self._logger.setLevel(INFO)
        self._handler = RotatingFileHandler(f'logs/{file_name}', maxBytes=500000, backupCount=5)
        self._formatter = Formatter('%(name)s: %(asctime)s | %(levelname)s | %(filename)s%(lineno)s | %(process)d | '
                                    '%(src)s >>> %(message)s')
        self._handler.setFormatter(self._formatter)
        self._logger.addHandler(self._handler)

    def level_filter(self, *f_args: filter_args):
        """
        Filters specific levels of logging.

        Use to isolate warnings and errors from info logs.

        :param f_args: A tuple containing a log level.
        :returns: The instance object.
        """
        self._lvl_filter = LevelFilter(FilterLevels(*f_args))
        self._logger.addFilter(self._lvl_filter)

        return self

    def logger(self, clear_logs: bool = False) -> L:
        """
        The logger.

        :param clear_logs: setting True will erase the contents of the log.
        """
        if clear_logs:
            self.clear_logs(self._file)

        return self._logger

    def debug(self, exception: Exception, src='general'):
        self._logger.debug(exception, exc_info=True, stack_info=True, extra={'src': src})

    def info(self, msg: str, src='general'):
        self._logger.info(msg, extra={'src': src})

    def warning(self, msg: str | Exception, src: str | Snowflake = 'general', exc_info: Optional[bool] = None,
                stack_info: Optional[bool] = None):
        self._logger.warning(
            msg,
            exc_info=exc_info if exc_info is not None else self._exc_info,
            stack_info=stack_info if stack_info is not None else self._stack_info,
            extra={'src': src})

    def error(self, msg: str | Exception, src: Optional[str | Snowflake] = 'general', exc_info: Optional[bool] = None,
              stack_info: Optional[bool] = None):
        self._logger.error(
            msg,
            exc_info=exc_info if exc_info is not None else self._exc_info,
            stack_info=stack_info if stack_info is not None else self._stack_info,
            extra={'src': src}
        )

    def exception(self, msg: str | Exception, src: str | Snowflake = 'general', exc_info: Optional[bool] = None,
                  stack_info: Optional[bool] = None):
        self._logger.exception(
            msg,
            exc_info=exc_info if exc_info is not None else self._exc_info,
            stack_info=stack_info if stack_info is not None else self._stack_info,
            extra={'src': src}
        )

    def critical(self, msg: str | Exception, src: str | Snowflake = 'general',
                 exc_info: Optional[bool] = None, stack_info: Optional[bool] = None):
        self._logger.critical(
            msg,
            exc_info=exc_info if exc_info is not None else self._exc_info,
            stack_info=stack_info if stack_info is not None else self._stack_info,
            extra={'src': src}
        )

    @staticmethod
    def clear_logs(file: str) -> None:
        """
        Erases the file data.

        :param file: The file to clear.
        """
        with open(f'logs/{file}', 'w') as f:
            f.truncate(0)
        f.close()


class LevelFilter(Filter):
    """
    A filter object.

    :param levels: A tuple containing one or more levels to filter.
    """

    def __init__(self, levels):
        super().__init__()
        self._levels = levels

    def filter(self, record: LogRecord) -> bool | None:
        return record.levelno in self._levels
