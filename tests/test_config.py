from pathlib import Path

import pytest

from lotto_analysis.config import Settings


def test_settings_use_project_relative_defaults(tmp_path: Path) -> None:
    settings = Settings.from_env(environ={}, project_root=tmp_path)

    assert settings.project_root == tmp_path.resolve()
    assert settings.data_dir == (tmp_path / "data").resolve()
    assert settings.raw_data_dir == (tmp_path / "data" / "raw").resolve()
    assert settings.processed_data_dir == (tmp_path / "data" / "processed").resolve()
    assert settings.analysis_data_dir == (tmp_path / "data" / "analysis").resolve()
    assert settings.collection_history_dir == (
        tmp_path / "data" / "collection_history"
    ).resolve()
    assert settings.database_dir == (tmp_path / "database").resolve()
    assert settings.log_dir == (tmp_path / "logs").resolve()
    assert settings.log_file == (tmp_path / "logs" / "lotto-analysis.log").resolve()


def test_settings_honor_path_overrides(tmp_path: Path) -> None:
    settings = Settings.from_env(
        environ={
            "LOTTO_DATA_DIR": "custom-data",
            "LOTTO_LOG_LEVEL": "debug",
            "LOTTO_SOURCE_BASE_URL": "https://example.test/",
            "LOTTO_REQUEST_TIMEOUT_SECONDS": "3.5",
            "LOTTO_REQUEST_INTERVAL_SECONDS": "0.25",
            "LOTTO_REQUEST_MAX_RETRIES": "4",
            "LOTTO_REQUEST_RETRY_BACKOFF_SECONDS": "0.75",
            "LOTTO_USER_AGENT": "test-agent",
            "LOTTO_COLLECTION_HISTORY_DIR": "history",
            "LOTTO_ANALYSIS_DATA_DIR": "analysis-output",
            "LOTTO_LOG_FILE": "custom.log",
            "LOTTO_LOG_MAX_BYTES": "1024",
            "LOTTO_LOG_BACKUP_COUNT": "2",
            "POSTGRES_HOST": "db.test",
            "POSTGRES_PORT": "5544",
            "POSTGRES_DB": "lotto db",
            "POSTGRES_USER": "lotto user",
            "POSTGRES_PASSWORD": "p@ss word",
        },
        project_root=tmp_path,
    )

    assert settings.data_dir == (tmp_path / "custom-data").resolve()
    assert settings.raw_data_dir == (tmp_path / "custom-data" / "raw").resolve()
    assert settings.log_level == "DEBUG"
    assert settings.source_base_url == "https://example.test"
    assert settings.request_timeout_seconds == 3.5
    assert settings.request_interval_seconds == 0.25
    assert settings.request_max_retries == 4
    assert settings.request_retry_backoff_seconds == 0.75
    assert settings.user_agent == "test-agent"
    assert settings.collection_history_dir == (tmp_path / "history").resolve()
    assert settings.analysis_data_dir == (tmp_path / "analysis-output").resolve()
    assert settings.log_file == (tmp_path / "custom.log").resolve()
    assert settings.log_max_bytes == 1024
    assert settings.log_backup_count == 2
    assert settings.postgres_host == "db.test"
    assert settings.postgres_port == 5544
    assert settings.database_url == (
        "postgresql+psycopg://lotto%20user:p%40ss%20word@db.test:5544/lotto%20db"
    )


@pytest.mark.parametrize("port", ["invalid", "0", "65536"])
def test_settings_reject_invalid_postgres_port(tmp_path: Path, port: str) -> None:
    with pytest.raises(ValueError, match="POSTGRES_PORT"):
        Settings.from_env(environ={"POSTGRES_PORT": port}, project_root=tmp_path)


@pytest.mark.parametrize("timeout", ["invalid", "0", "-1"])
def test_settings_reject_invalid_timeout(tmp_path: Path, timeout: str) -> None:
    with pytest.raises(ValueError, match="LOTTO_REQUEST_TIMEOUT_SECONDS"):
        Settings.from_env(
            environ={"LOTTO_REQUEST_TIMEOUT_SECONDS": timeout},
            project_root=tmp_path,
        )


@pytest.mark.parametrize("interval", ["invalid", "-1"])
def test_settings_reject_invalid_interval(tmp_path: Path, interval: str) -> None:
    with pytest.raises(ValueError, match="LOTTO_REQUEST_INTERVAL_SECONDS"):
        Settings.from_env(
            environ={"LOTTO_REQUEST_INTERVAL_SECONDS": interval},
            project_root=tmp_path,
        )


@pytest.mark.parametrize("retries", ["invalid", "-1"])
def test_settings_reject_invalid_retry_count(tmp_path: Path, retries: str) -> None:
    with pytest.raises(ValueError, match="LOTTO_REQUEST_MAX_RETRIES"):
        Settings.from_env(
            environ={"LOTTO_REQUEST_MAX_RETRIES": retries},
            project_root=tmp_path,
        )


@pytest.mark.parametrize("backoff", ["invalid", "-1"])
def test_settings_reject_invalid_retry_backoff(
    tmp_path: Path, backoff: str
) -> None:
    with pytest.raises(ValueError, match="LOTTO_REQUEST_RETRY_BACKOFF_SECONDS"):
        Settings.from_env(
            environ={"LOTTO_REQUEST_RETRY_BACKOFF_SECONDS": backoff},
            project_root=tmp_path,
        )


@pytest.mark.parametrize("max_bytes", ["invalid", "0", "-1"])
def test_settings_reject_invalid_log_max_bytes(
    tmp_path: Path, max_bytes: str
) -> None:
    with pytest.raises(ValueError, match="LOTTO_LOG_MAX_BYTES"):
        Settings.from_env(
            environ={"LOTTO_LOG_MAX_BYTES": max_bytes},
            project_root=tmp_path,
        )


@pytest.mark.parametrize("backup_count", ["invalid", "-1"])
def test_settings_reject_invalid_log_backup_count(
    tmp_path: Path, backup_count: str
) -> None:
    with pytest.raises(ValueError, match="LOTTO_LOG_BACKUP_COUNT"):
        Settings.from_env(
            environ={"LOTTO_LOG_BACKUP_COUNT": backup_count},
            project_root=tmp_path,
        )


def test_ensure_directories_creates_runtime_paths(tmp_path: Path) -> None:
    settings = Settings.from_env(environ={}, project_root=tmp_path)

    settings.ensure_directories()

    assert settings.raw_data_dir.is_dir()
    assert settings.processed_data_dir.is_dir()
    assert settings.analysis_data_dir.is_dir()
    assert settings.collection_history_dir.is_dir()
    assert settings.database_dir.is_dir()
    assert settings.log_dir.is_dir()
