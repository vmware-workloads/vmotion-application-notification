import logging

from logging import handlers
from pathlib import Path
from typing import Union

from vmotion_notification import logger


def get_logging_level(level: str) -> int:

    default_log_level = logging.DEBUG

    if not isinstance(level, str):
        return default_log_level

    match level.upper():
        case "INFO":
            return logging.INFO
        case "DEBUG":
            return logging.DEBUG
        case "WARNING":
            return logging.WARNING
        case "ERROR":
            return logging.ERROR
        case "CRITICAL":
            return logging.CRITICAL
        case _:
            return default_log_level


def create_folders(folder_path: Union[str, Path]) -> Path:
    try:
        path = Path(folder_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError:
        print(f"Insufficient permissions to create folder '{ folder_path }'")
        exit(1)


def create_logger(logfile: str, log_level: int, console_level: int, logfile_maxsize_bytes: int, logfile_count: int):

    # Set logging level
    logger.setLevel(log_level)

    # Set log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(logfile,
                                                        maxBytes=logfile_maxsize_bytes,
                                                        backupCount=logfile_count)
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
