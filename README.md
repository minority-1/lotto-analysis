# Lotto Analysis

한국 로또 6/45 데이터를 단계적으로 수집하고 검증·분석하기 위한 Python 프로젝트입니다.

사용자가 직접 확인하거나 반복 실행해야 하는 작업은 [사용자 체크리스트](docs/USER_CHECKLIST.md)에서 관리합니다.

단계별 품질 검토와 남은 개선 사항은 [코드 리뷰 기록](docs/reviews/README.md)에서 확인할 수 있습니다.

현재는 공식 데이터 수집과 원본 검증, 정제 CSV 생성을 제공합니다.

- 설정 및 경로 관리
- 로또 회차 데이터 모델
- 단일 회차 수집기 인터페이스
- 동행복권 공식 사이트 기반 단일 회차 수집기
- 최신 회차 확인과 범위·전체 순차 수집
- 자동 재시도와 중단 후 이어받기
- 증분 수집과 누락 회차 보완
- 회차별 공식 원본 레코드 JSON 저장
- 수집 실행 이력과 실패 회차 영구 기록
- 수집 진행률 표시와 회전 파일 로그
- 기본 logging 설정
- pytest 구성
- 원본 전체 유효성 검사와 오류 분리
- 정제 CSV와 JSON 검증 보고서 생성
- CSV Repository와 기본 기술통계 분석

SQLite는 제외했으며 PostgreSQL 17을 Docker Compose로 실행합니다. PostgreSQL 스키마·Repository와 CSV 동기화·검증 기능까지 구현했으며, 고급 분석과 Streamlit 화면은 아직 구현하지 않았습니다.

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

모든 수집 명령의 실행 결과는 기본적으로 `data/collection_history/`에 JSON 파일로 저장됩니다. 각 파일에는 명령, 실행 시간, 대상 범위, 성공·건너뜀·실패 회차와 실패 사유가 포함됩니다. 명령 실행이 끝나면 터미널에 생성된 이력 파일 경로가 표시됩니다.

설정값 자체를 해석할 수 없거나 이력 디렉터리에 쓸 수 없는 경우에는 이력 파일 대신 터미널에 원래 오류와 이력 저장 불가 사유가 표시됩니다.

범위 수집 중에는 처리 건수, 전체 건수, 백분율, 현재 회차와 상태가 표시됩니다. 긴 전체 수집에서는 약 1% 단위로 출력하며 실패는 즉시 출력합니다.

콘솔 로그는 기본적으로 `logs/lotto-analysis.log`에도 저장됩니다. 로그 파일이 5 MiB를 넘으면 최대 3개의 백업 파일로 회전합니다.

최근 실행 이력을 확인하는 예시는 다음과 같습니다.

```bash
ls -lt data/collection_history | head
```

공식 결과 화면 내부에서 사용하는 JSON 엔드포인트는 공개 API 문서가 확인되지 않았으므로 사이트 응답 구조가 변경되면 수집기도 함께 갱신해야 합니다.

## 데이터 검증 및 정제 CSV

로컬 원본 전체를 검증하고 정제 CSV를 생성합니다. 네트워크는 사용하지 않습니다.

```bash
lotto-analysis process
```

정상 데이터는 `data/processed/lotto_draws.csv`, 전체 검증 결과와 오류 사유는 `data/processed/validation_report.json`에 저장됩니다. 잘못된 원본이 있어도 정상 회차는 CSV에 기록되지만 명령은 종료 코드 `1`을 반환합니다.

현재 원본에는 수집 시각이 포함되지 않으므로 CSV의 `collected_at`은 빈 값입니다. 파일 수정 시각을 실제 수집 시각으로 추정하지 않습니다.

## 기본 통계 분석

정제 CSV 전체를 대상으로 번호별 출현 통계와 회차별 조합 특성을 계산합니다.

```bash
lotto-analysis analyze
```

최근 N회만 분석할 수 있습니다.

```bash
lotto-analysis analyze --recent 50
```

전체 상세 결과를 JSON으로 내보냅니다.

```bash
lotto-analysis analyze --export
lotto-analysis analyze --recent 50 --export
```

출력에는 번호별 일반번호·보너스번호 출현 횟수, 출현 비율, 마지막 출현 회차, 현재 미출현 회차 수와 전체 조합의 평균 합계·홀수·저번호·연속번호 요약이 포함됩니다.

출현 비율은 `해당 번호의 일반번호 출현 횟수 ÷ 분석 회차 수`입니다. 저번호는 `1~22`, 고번호는 `23~45`로 정의하며 구간은 `1~10 / 11~20 / 21~30 / 31~40 / 41~45`를 사용합니다. 이 결과는 과거 데이터의 기술통계이며 미래 당첨 확률이나 예측을 의미하지 않습니다.

### 기간 비교

최근 50회와 그 직전 50회의 번호별 출현률·순위 변화를 비교합니다.

```bash
lotto-analysis compare 50
```

전체 기간과 최근 50회를 비교하거나 결과를 내보낼 수 있습니다.

```bash
lotto-analysis compare 50 --against-all
lotto-analysis compare 50 --export
```

기간 길이가 다를 때는 단순 횟수가 아니라 회차당 출현률 차이를 사용합니다. 순위 변화 역시 과거 두 기간의 상대적 위치 차이일 뿐 미래 추세를 의미하지 않습니다.

### 출현 간격 분석

번호별 출현 회차와 회차 번호 간격의 평균·중앙값·최소·최대·최근 간격·표준편차를 계산합니다.

```bash
lotto-analysis gaps
lotto-analysis gaps --recent 100
lotto-analysis gaps --export
```

JSON 산출물은 기본적으로 `data/analysis/`에 저장됩니다. 출현 간격은 과거 분포를 설명하는 통계이며 다음 출현 시점을 예측하지 않습니다.

## 환경변수

모든 경로는 선택적으로 환경변수로 변경할 수 있습니다. 상대 경로는 프로젝트 루트를 기준으로 해석합니다.

| 환경변수 | 기본값 |
| --- | --- |
| `LOTTO_DATA_DIR` | `data` |
| `LOTTO_RAW_DATA_DIR` | `data/raw` |
| `LOTTO_PROCESSED_DATA_DIR` | `data/processed` |
| `LOTTO_ANALYSIS_DATA_DIR` | `data/analysis` |
| `LOTTO_COLLECTION_HISTORY_DIR` | `data/collection_history` |
| `LOTTO_DATABASE_DIR` | `database` |
| `LOTTO_LOG_DIR` | `logs` |
| `LOTTO_LOG_FILE` | `logs/lotto-analysis.log` |
| `LOTTO_LOG_LEVEL` | `INFO` |
| `LOTTO_LOG_MAX_BYTES` | `5242880` |
| `LOTTO_LOG_BACKUP_COUNT` | `3` |
| `LOTTO_SOURCE_BASE_URL` | `https://www.dhlottery.co.kr` |
| `LOTTO_REQUEST_TIMEOUT_SECONDS` | `10` |
| `LOTTO_REQUEST_INTERVAL_SECONDS` | `0.5` |
| `LOTTO_REQUEST_MAX_RETRIES` | `3` |
| `LOTTO_REQUEST_RETRY_BACKOFF_SECONDS` | `0.5` |
| `LOTTO_USER_AGENT` | `lotto-analysis/0.1` |
| `POSTGRES_HOST` | `127.0.0.1` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `lotto_analysis` |
| `POSTGRES_USER` | `lotto_app` |
| `POSTGRES_PASSWORD` | 설정 필요 |

애플리케이션 코드에서 `Settings.from_env()`로 설정을 읽고, 실행 시점에 `settings.ensure_directories()`를 호출하면 필요한 디렉터리를 생성할 수 있습니다.

## PostgreSQL 실행

`.env.example`을 `.env`로 복사하고 로컬 전용 비밀번호를 설정합니다. `.env`는 Git에 포함되지 않습니다.

```bash
cp .env.example .env
```

PostgreSQL을 백그라운드에서 시작하고 상태를 확인합니다.

```bash
docker compose up -d postgres
docker compose ps
```

컨테이너 내부의 `psql`로 연결을 확인합니다.

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select version();"'
```

컨테이너를 중지하거나 다시 시작합니다. 명명된 볼륨의 DB 데이터는 유지됩니다.

```bash
docker compose stop postgres
docker compose start postgres
```

스키마를 최신 버전으로 올리고, 검증된 정제 CSV를 PostgreSQL에 동기화합니다. 같은 명령을 다시 실행해도 회차 번호를 기준으로 갱신되므로 중복 행은 생기지 않습니다.

```bash
lotto-analysis db-upgrade
lotto-analysis db-import
lotto-analysis db-verify
```

`db-verify`는 CSV와 PostgreSQL의 전체 회차 데이터 및 기본 분석 결과가 같은지 확인합니다. PostgreSQL을 사용하는 선택적 통합 테스트는 다음과 같이 실행합니다.

```bash
LOTTO_RUN_POSTGRES_TESTS=1 pytest -m postgres
```

DB를 화면에서 확인할 때는 무료 오픈소스이며 PostgreSQL 외 다른 DB도 함께 다룰 수 있는 DBeaver Community를 권장합니다. 연결 정보는 Host `127.0.0.1`, Port `.env`의 `POSTGRES_PORT`, Database·Username·Password는 각각 `.env`의 `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`를 사용합니다.

일반 종료는 다음 명령을 사용합니다.

```bash
docker compose down
```

DB 데이터를 포함한 볼륨까지 삭제하는 명령은 모든 로컬 DB 데이터를 잃으므로 초기화가 확실히 필요할 때만 사용합니다.

```bash
docker compose down --volumes
```
