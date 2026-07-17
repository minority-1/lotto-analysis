"""Programmatic Alembic migration entry point."""

from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade_database(project_root: Path) -> None:
    """Upgrade the configured database to the latest schema revision."""
    config = Config(str(Path(project_root) / "alembic.ini"))
    command.upgrade(config, "head")
