import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from lotto_analysis.logging_config import configure_logging


def test_configure_logging_sets_level_and_writes_file(tmp_path: Path) -> None:
    log_file = tmp_path / "nested" / "application.log"

    configure_logging(level="DEBUG", log_file=log_file)
    logging.getLogger("lotto_analysis.test").debug("test message")

    assert logging.getLogger().level == logging.DEBUG
    assert "test message" in log_file.read_text(encoding="utf-8")
    assert any(
        isinstance(handler, RotatingFileHandler)
        for handler in logging.getLogger().handlers
    )


def test_configure_logging_rotates_file_at_size_limit(tmp_path: Path) -> None:
    log_file = tmp_path / "application.log"
    configure_logging(
        level="INFO",
        log_file=log_file,
        max_bytes=120,
        backup_count=1,
    )

    logger = logging.getLogger("lotto_analysis.rotation")
    for index in range(10):
        logger.info("message %s with enough text to rotate the file", index)

    assert log_file.is_file()
    assert (tmp_path / "application.log.1").is_file()


def test_configure_logging_rejects_unknown_level() -> None:
    with pytest.raises(ValueError, match="Invalid logging level"):
        configure_logging(level="NOT_A_LEVEL")


@pytest.mark.parametrize(
    ("max_bytes", "backup_count", "message"),
    [(0, 1, "max_bytes"), (100, -1, "backup_count")],
)
def test_configure_logging_rejects_invalid_rotation_settings(
    max_bytes: int, backup_count: int, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        configure_logging(max_bytes=max_bytes, backup_count=backup_count)
