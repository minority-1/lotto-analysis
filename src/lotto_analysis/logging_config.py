"""Shared logging configuration for command-line and future UI adapters."""

import logging
from pathlib import Path
from typing import Optional


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
) -> None:
    """Configure root logging with a console and optional file handler."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid logging level: {0}".format(level))

    handlers = [logging.StreamHandler()]
    if log_file is not None:
        resolved_log_file = Path(log_file).expanduser()
        resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(resolved_log_file, encoding="utf-8"))

    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=handlers,
        force=True,
    )

