"""Application settings and filesystem path management."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping, Optional
from urllib.parse import quote

from dotenv import load_dotenv


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
    analysis_data_dir: Path
    collection_history_dir: Path
    database_dir: Path
    log_dir: Path
    log_file: Path
    log_level: str = "INFO"
    log_max_bytes: int = 5 * 1024 * 1024
    log_backup_count: int = 3
    source_base_url: str = "https://www.dhlottery.co.kr"
    request_timeout_seconds: float = 10.0
    request_interval_seconds: float = 0.5
    request_max_retries: int = 3
    request_retry_backoff_seconds: float = 0.5
    user_agent: str = "lotto-analysis/0.1"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_database: str = "lotto_analysis"
    postgres_user: str = "lotto_app"
    postgres_password: str = ""

    @classmethod
    def from_env(
        cls,
        environ: Optional[Mapping[str, str]] = None,
        project_root: Optional[Path] = None,
    ) -> "Settings":
        """Build settings from environment variables and safe defaults."""
        root = (
            Path(project_root).expanduser().resolve()
            if project_root is not None
            else Path(__file__).resolve().parents[2]
        )
        if environ is None:
            load_dotenv(root / ".env")
            env = os.environ
        else:
            env = environ
        data_dir = _resolve_path(env.get("LOTTO_DATA_DIR", "data"), root)

        try:
            postgres_port = int(env.get("POSTGRES_PORT", "5432"))
        except ValueError as exc:
            raise ValueError("POSTGRES_PORT must be an integer") from exc
        if not 1 <= postgres_port <= 65535:
            raise ValueError("POSTGRES_PORT must be between 1 and 65535")

        try:
            request_timeout_seconds = float(
                env.get("LOTTO_REQUEST_TIMEOUT_SECONDS", "10")
            )
        except ValueError as exc:
            raise ValueError("LOTTO_REQUEST_TIMEOUT_SECONDS must be a number") from exc
        if request_timeout_seconds <= 0:
            raise ValueError("LOTTO_REQUEST_TIMEOUT_SECONDS must be positive")
        try:
            request_interval_seconds = float(
                env.get("LOTTO_REQUEST_INTERVAL_SECONDS", "0.5")
            )
        except ValueError as exc:
            raise ValueError("LOTTO_REQUEST_INTERVAL_SECONDS must be a number") from exc
        if request_interval_seconds < 0:
            raise ValueError("LOTTO_REQUEST_INTERVAL_SECONDS cannot be negative")
        try:
            request_max_retries = int(env.get("LOTTO_REQUEST_MAX_RETRIES", "3"))
        except ValueError as exc:
            raise ValueError("LOTTO_REQUEST_MAX_RETRIES must be an integer") from exc
        if request_max_retries < 0:
            raise ValueError("LOTTO_REQUEST_MAX_RETRIES cannot be negative")
        try:
            request_retry_backoff_seconds = float(
                env.get("LOTTO_REQUEST_RETRY_BACKOFF_SECONDS", "0.5")
            )
        except ValueError as exc:
            raise ValueError(
                "LOTTO_REQUEST_RETRY_BACKOFF_SECONDS must be a number"
            ) from exc
        if request_retry_backoff_seconds < 0:
            raise ValueError(
                "LOTTO_REQUEST_RETRY_BACKOFF_SECONDS cannot be negative"
            )
        try:
            log_max_bytes = int(
                env.get("LOTTO_LOG_MAX_BYTES", str(5 * 1024 * 1024))
            )
        except ValueError as exc:
            raise ValueError("LOTTO_LOG_MAX_BYTES must be an integer") from exc
        if log_max_bytes <= 0:
            raise ValueError("LOTTO_LOG_MAX_BYTES must be positive")
        try:
            log_backup_count = int(env.get("LOTTO_LOG_BACKUP_COUNT", "3"))
        except ValueError as exc:
            raise ValueError("LOTTO_LOG_BACKUP_COUNT must be an integer") from exc
        if log_backup_count < 0:
            raise ValueError("LOTTO_LOG_BACKUP_COUNT cannot be negative")

        log_dir = _resolve_path(env.get("LOTTO_LOG_DIR", "logs"), root)

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
            analysis_data_dir=_resolve_path(
                env.get("LOTTO_ANALYSIS_DATA_DIR", str(data_dir / "analysis")),
                root,
            ),
            collection_history_dir=_resolve_path(
                env.get(
                    "LOTTO_COLLECTION_HISTORY_DIR",
                    str(data_dir / "collection_history"),
                ),
                root,
            ),
            database_dir=_resolve_path(
                env.get("LOTTO_DATABASE_DIR", "database"), root
            ),
            log_dir=log_dir,
            log_file=_resolve_path(
                env.get("LOTTO_LOG_FILE", str(log_dir / "lotto-analysis.log")),
                root,
            ),
            log_level=env.get("LOTTO_LOG_LEVEL", "INFO").upper(),
            log_max_bytes=log_max_bytes,
            log_backup_count=log_backup_count,
            source_base_url=env.get(
                "LOTTO_SOURCE_BASE_URL", "https://www.dhlottery.co.kr"
            ).rstrip("/"),
            request_timeout_seconds=request_timeout_seconds,
            request_interval_seconds=request_interval_seconds,
            request_max_retries=request_max_retries,
            request_retry_backoff_seconds=request_retry_backoff_seconds,
            user_agent=env.get("LOTTO_USER_AGENT", "lotto-analysis/0.1"),
            postgres_host=env.get("POSTGRES_HOST", "127.0.0.1"),
            postgres_port=postgres_port,
            postgres_database=env.get("POSTGRES_DB", "lotto_analysis"),
            postgres_user=env.get("POSTGRES_USER", "lotto_app"),
            postgres_password=env.get("POSTGRES_PASSWORD", ""),
        )

    @property
    def database_url(self) -> str:
        """Return a psycopg SQLAlchemy URL with escaped credentials."""
        return "postgresql+psycopg://{0}:{1}@{2}:{3}/{4}".format(
            quote(self.postgres_user, safe=""),
            quote(self.postgres_password, safe=""),
            self.postgres_host,
            self.postgres_port,
            quote(self.postgres_database, safe=""),
        )

    def ensure_directories(self) -> None:
        """Create directories required by runtime file operations."""
        for directory in (
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.analysis_data_dir,
            self.collection_history_dir,
            self.database_dir,
            self.log_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
