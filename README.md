# Lotto Analysis

한국 로또 6/45 데이터를 단계적으로 수집하고 검증·분석하기 위한 Python 프로젝트입니다.

현재는 1단계의 기본 골격만 제공합니다.

- 설정 및 경로 관리
- 로또 회차 데이터 모델
- 단일 회차 수집기 인터페이스
- 기본 logging 설정
- pytest 구성

실제 HTTP 수집, 전체·범위 수집, 파일 및 데이터베이스 저장, Streamlit 화면은 아직 구현하지 않았습니다.

## 요구 사항

- Python 3.9 이상

## 개발 환경 설치

macOS 또는 Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 테스트

```bash
pytest
```

## 환경변수

모든 경로는 선택적으로 환경변수로 변경할 수 있습니다. 상대 경로는 프로젝트 루트를 기준으로 해석합니다.

| 환경변수 | 기본값 |
| --- | --- |
| `LOTTO_DATA_DIR` | `data` |
| `LOTTO_RAW_DATA_DIR` | `data/raw` |
| `LOTTO_PROCESSED_DATA_DIR` | `data/processed` |
| `LOTTO_DATABASE_DIR` | `database` |
| `LOTTO_LOG_DIR` | `logs` |
| `LOTTO_LOG_LEVEL` | `INFO` |

애플리케이션 코드에서 `Settings.from_env()`로 설정을 읽고, 실행 시점에 `settings.ensure_directories()`를 호출하면 필요한 디렉터리를 생성할 수 있습니다.

