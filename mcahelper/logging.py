import logging
import logging.handlers
import sys
from pathlib import Path

logging.addLevelName(logging.FATAL, "FATAL")
logging.addLevelName(logging.WARN, "WARN")

logging.raiseExceptions = False
logging.Formatter.default_msec_format = '%s.%03d'

_FORMATTER = logging.Formatter("<{asctime}> [{levelname}] [{funcName}] {message}", style='{')


class VVCLogger(logging.Logger):
    def __init__(self, name: str = '', stream_log_level: int = logging.DEBUG) -> None:
        if name == '':
            name = Path(sys.argv[0]).stem
        super().__init__(name)

        stream_hd = logging.StreamHandler(sys.stdout)
        stream_hd.setLevel(stream_log_level)
        stream_hd.setFormatter(_FORMATTER)
        self.addHandler(stream_hd)


LOGGER = VVCLogger()


def get_logger() -> VVCLogger:
    global LOGGER

    if LOGGER is None:
        LOGGER = VVCLogger()

    return LOGGER


def set_logger(new_logger: logging.Logger) -> None:
    global LOGGER
    LOGGER = new_logger


def set_formatter(formatter: logging.Formatter) -> None:
    global _FORMATTER
    _FORMATTER = formatter

    if LOGGER is not None:
        for hd in LOGGER.handlers:
            hd.setFormatter(formatter)


_FILELOG_ENABLED = False


def enable_filelog(log_level: int = logging.INFO, log_dir: Path = Path('log'), backup_count: int = 5) -> None:
    global _FILELOG_ENABLED

    if _FILELOG_ENABLED:
        return

    log_dir = Path(log_dir)
    log_dir.mkdir(0o755, parents=True, exist_ok=True)

    file_hd = logging.handlers.TimedRotatingFileHandler(
        log_dir / f"{LOGGER.name}.log", when='MIDNIGHT', backupCount=backup_count, encoding='utf-8'
    )
    file_hd.setLevel(log_level)
    file_hd.setFormatter(_FORMATTER)
    LOGGER.addHandler(file_hd)

    _FILELOG_ENABLED = True
