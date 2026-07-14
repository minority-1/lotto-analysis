from pathlib import Path

from lotto_analysis.config import Settings


def test_settings_use_project_relative_defaults(tmp_path: Path) -> None:
    settings = Settings.from_env(environ={}, project_root=tmp_path)

    assert settings.project_root == tmp_path.resolve()
    assert settings.data_dir == (tmp_path / "data").resolve()
    assert settings.raw_data_dir == (tmp_path / "data" / "raw").resolve()
    assert settings.processed_data_dir == (tmp_path / "data" / "processed").resolve()
    assert settings.database_dir == (tmp_path / "database").resolve()
    assert settings.log_dir == (tmp_path / "logs").resolve()


def test_settings_honor_path_overrides(tmp_path: Path) -> None:
    settings = Settings.from_env(
        environ={"LOTTO_DATA_DIR": "custom-data", "LOTTO_LOG_LEVEL": "debug"},
        project_root=tmp_path,
    )

    assert settings.data_dir == (tmp_path / "custom-data").resolve()
    assert settings.raw_data_dir == (tmp_path / "custom-data" / "raw").resolve()
    assert settings.log_level == "DEBUG"


def test_ensure_directories_creates_runtime_paths(tmp_path: Path) -> None:
    settings = Settings.from_env(environ={}, project_root=tmp_path)

    settings.ensure_directories()

    assert settings.raw_data_dir.is_dir()
    assert settings.processed_data_dir.is_dir()
    assert settings.database_dir.is_dir()
    assert settings.log_dir.is_dir()

