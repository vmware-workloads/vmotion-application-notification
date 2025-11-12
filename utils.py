import logging

from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


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
