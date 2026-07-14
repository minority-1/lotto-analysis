"""Application settings and filesystem path management."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping, Optional


def _resolve_path(value: str, project_root: Path) -> Path:
    """Resolve an absolute path or a path relative to the project root."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


@dataclass(frozen=True)
class Settings:
    """Filesystem and logging settings used by the application."""

    project_root: Path
    data_dir: Path
    raw_data_dir: Path
    processed_data_dir: Path
    database_dir: Path
    log_dir: Path
    log_level: str = "INFO"

    @classmethod
    def from_env(
        cls,
        environ: Optional[Mapping[str, str]] = None,
        project_root: Optional[Path] = None,
    ) -> "Settings":
        """Build settings from environment variables and safe defaults."""
        env = os.environ if environ is None else environ
        root = (
            Path(project_root).expanduser().resolve()
            if project_root is not None
            else Path(__file__).resolve().parents[2]
        )
        data_dir = _resolve_path(env.get("LOTTO_DATA_DIR", "data"), root)

        return cls(
            project_root=root,
            data_dir=data_dir,
            raw_data_dir=_resolve_path(
                env.get("LOTTO_RAW_DATA_DIR", str(data_dir / "raw")), root
            ),
            processed_data_dir=_resolve_path(
                env.get("LOTTO_PROCESSED_DATA_DIR", str(data_dir / "processed")),
                root,
            ),
            database_dir=_resolve_path(
                env.get("LOTTO_DATABASE_DIR", "database"), root
            ),
            log_dir=_resolve_path(env.get("LOTTO_LOG_DIR", "logs"), root),
            log_level=env.get("LOTTO_LOG_LEVEL", "INFO").upper(),
        )

    def ensure_directories(self) -> None:
        """Create directories required by runtime file operations."""
        for directory in (
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.database_dir,
            self.log_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

