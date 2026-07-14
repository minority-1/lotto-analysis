import logging
from pathlib import Path

import pytest

from lotto_analysis.logging_config import configure_logging


def test_configure_logging_sets_level_and_writes_file(tmp_path: Path) -> None:
    log_file = tmp_path / "nested" / "application.log"

    configure_logging(level="DEBUG", log_file=log_file)
    logging.getLogger("lotto_analysis.test").debug("test message")

    assert logging.getLogger().level == logging.DEBUG
    assert "test message" in log_file.read_text(encoding="utf-8")


def test_configure_logging_rejects_unknown_level() -> None:
    with pytest.raises(ValueError, match="Invalid logging level"):
        configure_logging(level="NOT_A_LEVEL")

