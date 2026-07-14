"""Shared logging configuration for command-line and future UI adapters."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Optional


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> None:
    """Configure console logging and an optional rotating UTF-8 file."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid logging level: {0}".format(level))
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")
    if backup_count < 0:
        raise ValueError("backup_count cannot be negative")

    handlers: List[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        resolved_log_file = Path(log_file).expanduser()
        resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                resolved_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
        )

    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=handlers,
        force=True,
    )
