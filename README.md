# Lotto Analysis

한국 로또 6/45 데이터를 단계적으로 수집하고 검증·분석하기 위한 Python 프로젝트입니다.

사용자가 직접 확인하거나 반복 실행해야 하는 작업은 [사용자 체크리스트](docs/USER_CHECKLIST.md)에서 관리합니다.

단계별 품질 검토와 남은 개선 사항은 [코드 리뷰 기록](docs/reviews/README.md)에서 확인할 수 있습니다.

현재는 공식 데이터 수집과 원본 검증, PostgreSQL 저장, 고급 분석 및 조건 기반 번호 생성을 제공합니다.

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
- PostgreSQL 기반 번호쌍·3개 조합·동반 출현 분석
- 7×7 행렬·조합 수학 특성·과거 조합 유사도 분석
- 조건 기반 균등 무작위 번호 조합 생성
- 전체·최근 빈도 가중 생성과 미래 누수 방지 백테스트
- PostgreSQL 기반 Streamlit 분석·조건 기반 번호 생성 화면

SQLite는 제외했으며 PostgreSQL 17을 Docker Compose로 실행합니다. 명세의 고급 분석, 균등·빈도 가중 번호 생성, 반복 백테스트와 Streamlit 초기 읽기 전용 분석 화면까지 구현했습니다. 추가 생성 전략과 Streamlit 데이터 관리·생성·백테스트 화면은 아직 구현하지 않았습니다.

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

## Streamlit 초기 UI

PostgreSQL 컨테이너를 실행한 상태에서 다음 명령을 사용합니다.

```bash
streamlit run streamlit_app/app.py
```

브라우저에서 `http://localhost:8501`을 열면 데이터 대시보드, 기본·패턴·관계·기간·간격·유사도 분석, 번호 생성과 백테스트 화면을 확인할 수 있습니다. 번호 생성 화면은 균등·전체 빈도·최근 빈도 전략과 포함·제외 번호, 주요 조건 및 seed를 지원합니다. 백테스트 화면은 단일 상세 실행과 전략·조합 수·seed 반복 비교를 제공합니다. 생성·백테스트 결과는 미래 당첨 확률이나 성과를 보장하지 않습니다. 수집·DB 변경 화면은 아직 포함하지 않습니다.

과거 조합 유사도와 최근·직전 기간의 7×7 행렬 출현률 차이도 Streamlit에서 확인할 수 있습니다. 사용자 지정 회차·날짜 범위와 번호쌍 전체 히트맵은 후속 분석 UI 범위입니다.

## FastAPI

PostgreSQL 컨테이너를 실행한 상태에서 개발 API 서버를 시작합니다.

```bash
uvicorn lotto_analysis.api.main:app --reload
```

기본 주소는 `http://127.0.0.1:8000`이며 OpenAPI 문서는 다음 주소에서 확인합니다.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

1차 엔드포인트:

- `GET /api/health`
- `GET /api/draws?recent=20`
- `GET /api/draws/latest`
- `GET /api/draws/1232`
- `GET /api/draws/page?limit=50&offset=0`
- `GET /api/dashboard`
- `GET /api/analysis/basic?recent=20`
- `GET /api/analysis/basic/range?start_draw=1000&end_draw=1100`
- `GET /api/analysis/basic/range?start_date=2025-01-01&end_date=2025-12-31`
- `GET /api/analysis/compare?recent=50&against_all=false`
- `GET /api/analysis/gaps?recent=100`
- `GET /api/analysis/relationships?recent=100&number=1`
- `GET /api/analysis/matrix?recent=100`
- `GET /api/analysis/matrix/compare?recent=50`
- `GET /api/analysis/patterns?recent=100`
- `GET /api/analysis/similarity?recent=100`
- `POST /api/combinations/generate`
- `POST /api/backtests/run`
- `POST /api/backtests/experiment`

번호 생성 요청 예시:

```json
{
  "strategy": "frequency",
  "weight_recent": 50,
  "count": 5,
  "required_numbers": [7],
  "excluded_numbers": [1, 2, 3],
  "odd_minimum": 2,
  "odd_maximum": 4,
  "sum_minimum": 100,
  "sum_maximum": 180,
  "seed": 42
}
```

백테스트 요청 예시:

```json
{
  "strategy": "frequency",
  "target_count": 20,
  "combinations_per_target": 5,
  "base_seed": 42,
  "weight_recent": 50
}
```

반복 비교는 `target_count`, `combination_counts`, `seeds`, `frequency_recent`를 전달합니다. 조합 수가 다른 결과의 최고 일치 수를 전략 성능으로 직접 비교하면 안 됩니다.

`recent=0`은 전체 범위를 의미합니다. 보유 회차보다 큰 최근 범위는 축소하지 않고 `422`를 반환합니다. 페이지 조회는 회차 오름차순이며 `limit`은 최대 200입니다. 존재하지 않는 단일 회차는 `404`, 데이터베이스 장애는 접속 상세를 숨긴 `503` 응답으로 반환합니다.

사용자 지정 기본 분석은 `start_draw`·`end_draw` 또는 `start_date`·`end_date` 한 쌍만 전달합니다. 시작과 끝은 모두 포함하며 두 범위 방식을 섞거나 결과가 없는 범위는 `422`입니다.

Next.js 로컬 개발 origin은 기본적으로 `http://localhost:3000`과 `http://127.0.0.1:3000`을 허용합니다. 다른 origin은 `.env`의 `LOTTO_CORS_ORIGINS`에 쉼표로 구분해 지정합니다. 백테스트는 현재 동기 실행이므로 API 요청 스키마의 실행량 상한을 적용합니다.

## Next.js 사용자 화면

FastAPI를 먼저 실행한 뒤 별도 터미널에서 프런트엔드를 시작합니다. Node.js 20.9 이상과 pnpm이 필요합니다.

```bash
cd frontend
cp .env.local.example .env.local
pnpm install
pnpm dev
```

브라우저에서 `http://localhost:3000`을 엽니다. `LOTTO_API_BASE_URL`은 Next.js 서버가 접근할 FastAPI 주소이며 기본값은 `http://127.0.0.1:8000/api`입니다. 첫 화면은 최신 회차, 수집·누락 현황, 최근 8회 기록과 최근 100회 출현 빈도 상위를 표시합니다.

`--recent N`을 사용하는 분석 명령은 보유 회차보다 N이 크면 전체 데이터로 조용히 대체하지 않고 실제 보유 건수를 포함한 오류를 반환합니다.

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

### 번호 관계 분석

PostgreSQL에 저장된 회차를 대상으로 번호쌍과 3개 조합의 동시 출현 횟수를 계산합니다. 기본 출력은 각각 상위 20개입니다.

```bash
lotto-analysis relationships
lotto-analysis relationships --recent 100 --top 10
```

특정 번호가 나온 회차에서 함께 나온 번호와 조건부 비율을 확인하고 전체 결과를 JSON으로 저장할 수 있습니다.

```bash
lotto-analysis relationships --number 7
lotto-analysis relationships --recent 100 --number 7 --export
```

`Draw rate`는 분석 회차 중 해당 조합이 등장한 회차 비율이며, 특정 번호의 동반 `Rate`는 그 번호가 나온 회차 중 상대 번호도 함께 나온 비율입니다. 실제 등장한 조합만 집계하며 횟수 내림차순, 번호 오름차순으로 정렬합니다.

같은 명령에서 다음 관계도 함께 출력합니다.

- 15개 번호쌍의 절대 거리 분포와 전체 번호쌍 중 비율
- 차이가 1인 번호쌍의 총 개수와 포함 회차 비율
- 끝수가 같은 번호쌍의 총 개수와 포함 회차 비율
- 길이 2 이상인 최대 연속번호 그룹
- 분석 범위 안에서 정확히 1·2·3회 전 회차와 겹친 번호 개수 분포
- 각 회차의 보너스 번호가 정확히 1·2·3회 뒤 일반번호로 나온 횟수와 비율

최근 N회 분석의 이전·이후 회차 비교는 선택 범위 밖의 회차를 가져오지 않습니다. 따라서 최근 100회의 1회 간격 비교 대상은 99개입니다. 보너스 후속 출현 비율의 분모도 실제 후속 회차가 범위 안에 있는 기준 회차 수입니다. 모두 과거 관계 기록이며 미래 당첨 확률이나 번호 간 인과관계를 의미하지 않습니다.

### 7×7 번호 행렬

PostgreSQL의 일반 당첨번호 출현 횟수를 1~7, 8~14 순서의 고정 7×7 위치에 배치합니다. 46~49에 해당하는 마지막 네 칸은 빈 셀입니다.

```bash
lotto-analysis matrix
lotto-analysis matrix --recent 100
lotto-analysis matrix --recent 100 --export
```

터미널 셀은 `번호:출현 횟수` 형식이며 행·열별 전체 출현 횟수와 회차당 사용한 서로 다른 행·열의 평균도 표시합니다. JSON에는 각 셀의 출현 횟수와 `출현 횟수 ÷ 분석 회차 수` 비율이 함께 저장됩니다.

행렬은 번호의 위치별 과거 분포를 보기 위한 표현 방식입니다. 특정 위치나 행·열의 빈도가 미래 당첨 가능성을 높인다는 의미가 아닙니다.

기본 행렬에는 다음 두 대각선의 구성 번호, 총 출현 횟수와 하나 이상 포함한 회차 비율도 표시합니다.

- 주대각선: `1, 9, 17, 25, 33, 41`
- 역대각선: `7, 13, 19, 25, 31, 37, 43`

최근 N회와 그 직전 N회의 셀별 출현률 차이를 비교합니다.

```bash
lotto-analysis matrix-compare 100
lotto-analysis matrix-compare 100 --export
```

차이는 `최근 N회 출현률 - 직전 N회 출현률`입니다. `+10%`는 최근 기간에 해당 번호가 나온 회차 비율이 직전 기간보다 10%포인트 높았다는 의미일 뿐, 이후 상승 추세나 예측을 뜻하지 않습니다.

### 조합 수학 특성

각 회차의 당첨번호 조합에서 AC 값, 정렬된 인접 번호 간격, 소수·합성수·제곱수 개수, 번호 합계 구간과 끝수 합계를 계산합니다.

```bash
lotto-analysis patterns
lotto-analysis patterns --recent 100
lotto-analysis patterns --recent 100 --export
```

AC 값은 15개 번호쌍에서 나온 서로 다른 차이의 개수에서 5를 뺀 값으로, 조합의 번호 간격 다양성을 나타냅니다. 숫자 1은 소수와 합성수 어디에도 포함하지 않으며 제곱수는 `1, 4, 9, 16, 25, 36`입니다.

번호 합계 구간은 가능한 합계 21~255를 다음처럼 나눕니다.

```text
21-100 / 101-120 / 121-140 / 141-160 / 161-180 / 181-255
```

인접 번호 간격은 정렬된 6개 번호 사이의 5개 차이이며, 끝수 합계는 각 번호를 10으로 나눈 나머지의 합입니다. 이 특성들은 과거 조합의 수학적 형태를 설명하며 당첨 가능성을 의미하지 않습니다.

### 과거 당첨 조합 유사도

선택한 범위의 각 회차를 그 범위 안의 이전 회차들과 비교해 공통 일반번호 수와 Jaccard 유사도를 계산합니다.

```bash
lotto-analysis similarity
lotto-analysis similarity --recent 100 --top 10
lotto-analysis similarity --recent 100 --export
```

전체 결과에는 모든 순서 없는 회차쌍의 0~6개 번호 중복 분포가 포함됩니다. 회차별 결과에는 비교한 이전 회차 수, 최대 중복 번호 수, 최대 Jaccard 유사도, 가장 유사한 이전 회차와 정확히 3·4·5·6개가 겹친 이전 조합 수가 기록됩니다.

Jaccard 유사도는 `공통 번호 수 ÷ 두 조합의 합집합 번호 수`입니다. 예를 들어 4개 번호가 같으면 합집합은 8개이므로 50%입니다. `--recent N`은 최근 N회 안에서만 비교하며 범위 밖 과거 회차는 포함하지 않습니다. 유사도는 과거 조합 중복을 설명하거나 향후 동일·유사 조합을 거르는 용도이며 당첨 가능성 점수가 아닙니다.

## 조건 기반 번호 조합 생성

PostgreSQL의 과거 당첨번호를 참조하면서 균등 무작위 전략으로 중복 없는 후보 조합을 생성합니다. 같은 seed와 데이터·조건을 사용하면 결과를 재현할 수 있습니다.

```bash
lotto-analysis generate --count 5 --seed 42
```

포함·제외 번호와 주요 조합 조건을 함께 지정할 수 있습니다.

```bash
lotto-analysis generate \
  --count 5 \
  --seed 20260717 \
  --include 7 \
  --exclude 1,2,3 \
  --odd-min 2 --odd-max 4 \
  --low-min 2 --low-max 4 \
  --sum-min 100 --sum-max 180 \
  --prime-min 1 --prime-max 4 \
  --ac-min 6 --ac-max 10 \
  --max-consecutive-pairs 1 \
  --export
```

낮은 번호는 1~22, 높은 번호는 23~45입니다. 짝수와 높은 번호 개수는 각각 `6-홀수`, `6-낮은 번호`이므로 별도 옵션 없이 함께 표시합니다. 연속번호 조건은 정렬된 번호에서 차이가 1인 인접 번호쌍의 최대 개수입니다.

기본적으로 다음 조합은 제외합니다.

- 과거 1등 조합과 완전히 같은 조합
- 과거 당첨 조합과 5개 이상 겹치는 조합
- 같은 실행에서 이미 생성된 조합과 5개 이상 겹치는 조합

허용 최대 중복은 `--max-historical-overlap`, `--max-result-overlap`으로 바꿀 수 있습니다. 과거 완전 동일 조합을 허용하려면 `--allow-exact-historical --max-historical-overlap 6`을 함께 사용해야 합니다.

기본 최대 시도 횟수는 10,000회입니다. 조건이 너무 엄격하면 무한 반복하지 않고 생성된 개수, 주요 거절 조건과 함께 실패 종료합니다. 결과는 `data/analysis/generated_combinations_*.json`으로 내보낼 수 있습니다. 생성 결과는 조건을 만족하는 무작위 후보이며 추천 점수나 실제 당첨 확률을 의미하지 않습니다.

과거 일반번호 출현 빈도에 가중치를 둔 전략도 사용할 수 있습니다.

```bash
# 전체 회차 빈도
lotto-analysis generate --strategy frequency --count 5 --seed 42

# 최근 50회 빈도
lotto-analysis generate \
  --strategy frequency --weight-recent 50 \
  --count 5 --seed 42 --export
```

번호별 기본 가중치는 분석 범위의 `일반번호 출현 횟수 + 1`입니다. 특정 번호로 확률이 과도하게 집중되지 않도록 각 가중치를 전체 평균의 0.5배~1.5배 범위로 제한한 뒤, 중복 없이 6개를 차례로 추출합니다. 결과에는 가중치에 사용한 회차 수와 공식이 함께 표시됩니다.

`--weight-recent`는 `--strategy frequency`에서만 사용할 수 있으며 보유 회차보다 크면 오류를 반환합니다. 내보내기 파일명에는 전략, 전체·최근 범위와 seed가 포함되어 서로 다른 전략 결과를 덮어쓰지 않습니다. 빈도 가중은 과거 출현을 사용자의 선호 가중치로 반영할 뿐 미래 당첨 확률을 뜻하지 않습니다.

## 생성 전략 백테스트

최근 K개 과거 회차를 목표로 선택하고, 각 목표 회차보다 앞선 데이터만 사용해 번호를 생성한 뒤 실제 당첨번호와 비교합니다.

```bash
# 균등 무작위
lotto-analysis backtest \
  --strategy uniform --targets 20 --combinations 5 --seed 42 --export

# 각 목표 회차 이전의 최근 50회 빈도 가중
lotto-analysis backtest \
  --strategy frequency --weight-recent 50 \
  --targets 20 --combinations 5 --seed 42 --export
```

목표 회차 T의 학습 데이터는 반드시 T보다 작은 회차뿐입니다. 회차별 seed는 `기준 seed + 목표 회차 번호`로 정해 재현할 수 있습니다. 결과에는 생성 조합, 실제 일반·보너스 번호, 일반번호 일치 개수, 보너스 포함 여부, 학습 범위와 시도 횟수가 기록됩니다.

터미널은 모든 생성 조합의 0~6개 일치 분포와 목표 회차별 최고 일치 개수 분포를 따로 표시합니다. 회차당 조합 수가 늘면 최고 일치 수가 자연스럽게 올라갈 수 있으므로 서로 다른 조합 수의 결과를 전략 성능 차이로 비교하면 안 됩니다. 현재 백테스트는 당첨 등수·상금·수익률을 계산하지 않으며, 단일 seed·짧은 기간 결과만으로 전략 우열을 결론 내리지 않습니다.

같은 목표 회차에서 전략·조합 수·seed를 반복 비교하려면 실험 명령을 사용합니다.

```bash
lotto-analysis backtest-experiment \
  --targets 20 --combinations 1,5,10,50 \
  --seeds 41,42,43 --frequency-recent 50 --export
```

이 명령은 균등, 전체 빈도 가중, 최근 N회 빈도 가중 전략을 모두 실행하고 전략·조합 수별 평균 일반번호 일치 수와 목표별 평균 최고 일치 수를 집계합니다. 동일한 조합 수 행끼리 전략을 비교하고, seed 수와 목표 회차 수가 적은 결과는 탐색적 참고 자료로만 사용해야 합니다. 내보내기 파일명에는 모든 실험 조건이 포함됩니다.

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
