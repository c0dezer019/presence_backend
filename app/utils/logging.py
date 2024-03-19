# Internal modules
from logging import getLogger, basicConfig, Formatter, Filter, LogRecord, INFO
from logging.handlers import RotatingFileHandler
from os import getenv
from os.path import relpath

# External modules
from dotenv import load_dotenv

# Internal Modules
from ..lib.types import FilterLevels, filter_args

load_dotenv()


def rel(file: str) -> str:
    return relpath(file, getenv('START_PATH')).replace("/", ".").replace('.py', '')


class Logger:
    """
    Creates a logging instance for logging.

    :param file_name: The file to log to.
    :param module: __name__ of the current module.
    """

    def __init__(self, file_name: str, module: str):
        basicConfig()
        self._lvl_filter = None
        self._file = file_name
        self._logger = getLogger(module)
        self._logger.setLevel(INFO)
        self._handler = RotatingFileHandler(f'logs/{file_name}', maxBytes=500000, backupCount=5)
        self._formatter = Formatter("%(asctime)s | %(name)s | %(levelname)s | %(process)d | %(message)s")
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

    def logger(self, clear_logs: bool = False):
        """
        The logger.

        :param clear_logs: setting True will erase the contents of the log.
        """
        if clear_logs:
            self.clear_logs(self._file)

        return self._logger

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
