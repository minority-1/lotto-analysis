# Lotto Analysis

한국 로또 6/45 데이터를 단계적으로 수집하고 검증·분석하기 위한 Python 프로젝트입니다.

사용자가 직접 확인하거나 반복 실행해야 하는 작업은 [사용자 체크리스트](docs/USER_CHECKLIST.md)에서 관리합니다.

현재는 1단계 수집 기능으로 공식 출처의 단일·범위·전체 회차 수집과 원본 JSON 저장을 제공합니다.

- 설정 및 경로 관리
- 로또 회차 데이터 모델
- 단일 회차 수집기 인터페이스
- 동행복권 공식 사이트 기반 단일 회차 수집기
- 최신 회차 확인과 범위·전체 순차 수집
- 자동 재시도와 중단 후 이어받기
- 증분 수집과 누락 회차 보완
- 회차별 공식 원본 레코드 JSON 저장
- 기본 logging 설정
- pytest 구성

SQLite 및 정제 CSV 저장, Streamlit 화면은 아직 구현하지 않았습니다.

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

기본 테스트는 외부 네트워크를 사용하지 않습니다. 공식 사이트까지 확인하는 선택적 테스트는 다음과 같이 실행합니다.

```bash
LOTTO_RUN_EXTERNAL_TESTS=1 pytest -m external
```

## 데이터 수집

다음 예시는 동행복권 공식 결과 데이터에서 1070회 한 건을 가져옵니다.

```bash
lotto-analysis collect-one 1070
```

지정 범위를 수집합니다.

```bash
lotto-analysis collect-range 1 10
```

기본적으로 이미 유효한 원본 파일이 있는 회차는 건너뜁니다. 기존 회차도 공식 서버에서 다시 확인하려면 `--refresh`를 사용합니다.

```bash
lotto-analysis collect-range 1 10 --refresh
```

1회부터 공식 사이트의 최신 완료 회차까지 수집합니다.

```bash
lotto-analysis collect-all
```

저장된 가장 큰 회차 다음부터 최신 회차까지만 수집합니다.

```bash
lotto-analysis collect-incremental
```

1회부터 최신 회차 사이에서 파일이 없거나 유효하지 않은 회차만 수집합니다.

```bash
lotto-analysis collect-missing
```

원본 레코드는 기본적으로 `data/raw/draw_0001.json` 형식으로 저장됩니다. 같은 회차의 공식 레코드가 달라지면 기존 파일은 유지하고 새 레코드는 `data/raw/conflicts/`에 내용 해시를 붙여 보존합니다. 실행 결과에는 변경된 필드가 실패 사유로 표시됩니다.

`collect-all`을 중단한 뒤 같은 명령을 다시 실행하면 저장된 유효 회차는 건너뛰고 나머지만 계속합니다.

공식 결과 화면 내부에서 사용하는 JSON 엔드포인트는 공개 API 문서가 확인되지 않았으므로 사이트 응답 구조가 변경되면 수집기도 함께 갱신해야 합니다.

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
| `LOTTO_SOURCE_BASE_URL` | `https://www.dhlottery.co.kr` |
| `LOTTO_REQUEST_TIMEOUT_SECONDS` | `10` |
| `LOTTO_REQUEST_INTERVAL_SECONDS` | `0.5` |
| `LOTTO_REQUEST_MAX_RETRIES` | `3` |
| `LOTTO_REQUEST_RETRY_BACKOFF_SECONDS` | `0.5` |
| `LOTTO_USER_AGENT` | `lotto-analysis/0.1` |

애플리케이션 코드에서 `Settings.from_env()`로 설정을 읽고, 실행 시점에 `settings.ensure_directories()`를 호출하면 필요한 디렉터리를 생성할 수 있습니다.
