# User Checklist

이 문서는 프로젝트 진행 중 사용자가 직접 실행하거나 확인하고 결정해야 할 작업을 지속적으로 관리한다.

상태 표기:

* `[완료]`: 확인 또는 실행이 끝난 항목
* `[대기]`: 다음 진행 전에 사용자가 확인해야 하는 항목
* `[정기]`: 운영 중 반복하는 항목
* `[선택]`: 필요할 때만 수행하는 항목

## 현재 데이터 상태

2026-07-15 기준으로 로컬 `data/raw/`를 검사한 결과다.

* `[완료]` 공식 데이터 1회부터 1232회까지 수집
* `[완료]` 유효한 회차별 원본 JSON 1232개 확인
* `[완료]` 1~1232회 사이 누락 0개 확인
* `[완료]` `data/raw/conflicts/` 충돌 파일 0개 확인
* `[완료]` 원본 파일이 요청 회차 한 건의 공식 레코드 형식인지 확인
* `[완료]` 수집 실행 이력과 실패 회차를 `data/collection_history/`에 영구 저장하도록 구현
* `[완료]` 수집 진행률 표시 구현
* `[완료]` 회전 파일 로그 구현
* `[완료]` 1단계 데이터 수집 전체 기능 구현 및 자동 테스트 완료

`data/`는 Git에 포함되지 않는다. GitHub에 코드를 푸시해도 수집한 원본 데이터는 로컬에만 남는다.

## 지금 사용자가 확인할 작업

* `[대기]` Git 커밋 작성자 `seungwon <lee@seungwonui-MacBookPro.local>`가 원하는 이름과 이메일인지 확인한다. GitHub 기여 내역과 연결하려면 GitHub 계정에 등록된 이메일로 설정하는 것을 권장한다.
* `[대기]` 중요한 원본 데이터라면 `data/raw/`를 별도 디스크나 개인 백업 저장소에 복사할지 결정한다.
* `[선택]` 임의의 몇 개 회차를 동행복권 공식 결과 화면과 비교한다. 권장 표본은 1회, 1070회, 최신 회차다.
* `[완료]` SQLite를 제외하고 정제·유효성 검사 및 CSV 생성을 진행하기로 결정

## 1단계 최종 사용자 확인

다음 명령을 실행한다. 기존 1~3회 파일은 다시 요청하지 않고 건너뛴다.

```bash
source .venv/bin/activate
lotto-analysis collect-range 1 3
```

다음 세 가지를 확인한다.

* `[완료]` 터미널에 `Progress:` 줄과 `3/3 (100.0%)`가 표시되는지 확인
* `[완료]` 터미널 마지막에 `History:` JSON 경로가 표시되는지 확인
* `[완료]` `logs/lotto-analysis.log` 파일에 `Skipping stored draw` 로그가 기록되는지 확인

확인 명령:

```bash
tail -n 10 logs/lotto-analysis.log
```

## 정기 수집 작업

새로운 추첨 회차만 추가한다.

```bash
source .venv/bin/activate
lotto-analysis collect-incremental
```

중간에 없거나 읽을 수 없는 원본을 보완한다.

```bash
lotto-analysis collect-missing
```

전체 범위를 검사하면서 유효한 기존 파일은 건너뛴다. 수집 중단 후 이어받을 때도 같은 명령을 사용한다.

```bash
lotto-analysis collect-all
```

## 문제 발생 시 확인

수집 결과에 실패가 있으면 다음을 확인한다.

* 네트워크 연결과 동행복권 공식 사이트 접속 여부
* 로그에 표시된 실패 회차와 오류 유형
* `data/raw/conflicts/`에 신규 충돌 파일이 생성됐는지 여부
* 충돌 메시지에 표시된 변경 필드
* 터미널 마지막에 출력된 `History:` 경로의 실행 이력 JSON

최근 실행 이력 파일을 확인한다.

```bash
ls -lt data/collection_history | head
```

이력 JSON의 `status` 값은 다음 의미다.

* `success`: 모든 대상이 성공하거나 유효한 기존 파일로 건너뜀
* `partial_failure`: 일부 회차는 처리됐지만 실패 회차가 있음
* `failed`: 최신 회차 확인 등으로 수집 실행 자체가 중단됨

기존 데이터까지 공식 서버에서 다시 확인하는 명령은 모든 회차를 재요청하므로 필요한 경우에만 실행한다.

```bash
lotto-analysis collect-all --refresh
```

충돌 파일이 생기면 기존 원본과 충돌 파일 중 어느 쪽도 직접 삭제하거나 교체하지 말고 먼저 차이를 검토한다.

## 다음 개발 단계 전 확인

1단계 코드 리뷰에서 확인된 보완 작업:

* `[완료]` 정규화 실패 원본이 이어받기에서 유효한 회차로 오인되는 P1 결함 수정
* `[완료]` 정수 필드의 실수 절삭 방지와 모델 타입 검증 강화
* `[완료]` CLI 초기화 실패의 실행 이력 처리 범위 정리
* `[보류]` 동시 프로세스 파일 쓰기 보호는 병렬 수집 도입 시 검토
* `[보류]` Windows 자동 검증은 GitHub Actions 도입 시 검토

상세 내용은 [1단계 데이터 수집 코드 리뷰](reviews/2026-07-15-stage-1-collection.md)를 참고한다.

정제·검증 단계에서 다음 항목을 구현할 예정이다.

* `[완료]` 번호 범위와 중복 검사
* `[완료]` 보너스 번호 중복 검사
* `[완료]` 날짜와 금액 타입 검사
* `[완료]` 회차 중복 및 누락 검사
* `[완료]` 정제 CSV 생성
* `[완료]` 오류 데이터 분리

사용자 확인 명령:

```bash
lotto-analysis process
```

예상 결과는 `1232 valid; 0 errors; 0 missing`이며, 새 회차를 수집한 뒤에는 전체 파일 수와 정상 건수가 함께 증가한다. `data/processed/lotto_draws.csv`의 행 수는 헤더를 포함하므로 정상 건수보다 1개 많다.

## 기본 통계 분석 확인

전체 회차와 최근 50회 분석을 실행한다.

```bash
lotto-analysis analyze
lotto-analysis analyze --recent 50
```

확인 항목:

* `[대기]` 전체 분석에 `Analyzed 1232 draws (1-1232)`가 표시되는지 확인
* `[대기]` 최근 분석에 `Analyzed 50 draws (1183-1232)`가 표시되는지 확인
* `[대기]` 번호 1~45가 각각 한 줄씩 표시되는지 확인
* `[대기]` `Main`, `Rate`, `Bonus`, `Last`, `Absent` 값이 표시되는지 확인

새로운 회차를 수집·정제하면 전체 건수와 마지막 회차는 달라질 수 있다. 분석 수치는 미래 당첨 가능성을 의미하지 않는다.

## PostgreSQL 전 분석 확인

```bash
lotto-analysis analyze --export
lotto-analysis compare 50 --export
lotto-analysis compare 50 --against-all
lotto-analysis gaps --export
```

확인 항목:

* `[대기]` `data/analysis/basic_analysis_all.json` 생성 확인
* `[대기]` 직전 50회와 최근 50회 범위가 각각 `1133-1182`, `1183-1232`로 표시되는지 확인
* `[대기]` 전체와 최근 50회 비교가 `1-1232`, `1183-1232`로 표시되는지 확인
* `[대기]` 출현 간격 분석에 번호 1~45와 평균·중앙·최소·최대·최근·미출현·표준편차가 표시되는지 확인
* `[대기]` `data/analysis/comparison_previous_recent_50.json`과 `gap_analysis_all.json` 생성 확인

새 회차가 추가되면 위 회차 범위는 달라진다. 이 확인을 마치면 PostgreSQL 설치·Repository 구현 단계로 진행할 수 있다.

## PostgreSQL 개발 환경 확인

```bash
docker compose up -d postgres
docker compose ps
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select current_database(), current_user;"'
```

확인 항목:

* `[완료]` Docker Desktop 설치 및 엔진 실행 확인
* `[완료]` 로컬 `.env` 생성과 Git 제외 확인
* `[완료]` `docker compose ps`에서 PostgreSQL 상태가 `healthy`인지 확인
* `[완료]` 접속 결과가 `lotto_analysis / lotto_app / PostgreSQL 17.10`인지 확인
* `[완료]` 컨테이너 제거·재생성 후에도 명명 볼륨의 확인 데이터가 유지되는지 확인

이 단계의 구체적인 생성·수정 파일은 구현 전에 별도로 설명한다.

## PostgreSQL 데이터 이관 확인

```bash
lotto-analysis db-upgrade
lotto-analysis db-import
lotto-analysis db-verify
```

확인 항목:

* `[완료]` Alembic 최초 마이그레이션 적용
* `[완료]` 정제 CSV 1232회차를 PostgreSQL에 저장
* `[완료]` 같은 이관 명령 재실행 후에도 1232건 유지
* `[완료]` CSV와 PostgreSQL의 전체 데이터 일치 확인
* `[완료]` 두 Repository의 기본 분석 결과 일치 확인
* `[완료]` 실제 PostgreSQL Repository 통합 테스트 통과
* `[선택]` DBeaver Community를 설치하고 `lotto_draws` 테이블을 화면에서 확인

새 회차 수집 후에는 `process`로 CSV를 갱신하고 `db-import`, `db-verify`를 차례로 실행한다.

## 번호 관계 분석 확인

```bash
lotto-analysis relationships --top 5
lotto-analysis relationships --recent 100 --number 7 --top 5 --export
```

확인 항목:

* `[완료]` PostgreSQL 전체 1232회차의 번호쌍·3개 조합 분석 실행
* `[완료]` 최근 100회 범위가 `1133-1232`로 표시되는지 확인
* `[완료]` 번호 7의 출현 15회와 동반 번호 결과 출력 확인
* `[완료]` `data/analysis/relationship_analysis_recent_100_number_7.json` 생성 확인
* `[완료]` 전체 1232회에서 거리 1 번호쌍 816개, 포함 회차 638개 출력 확인
* `[완료]` 전체 1232회에서 같은 끝수 번호쌍 1490개, 포함 회차 961개 출력 확인
* `[완료]` 최근 100회의 직전 1·2·3회 비교 대상이 99·98·97개인지 확인
* `[완료]` 최대 연속번호 그룹별 횟수와 출현 회차 비율 출력 확인
* `[완료]` 전체 회차의 보너스 번호가 1·2·3회 뒤 일반번호로 나온 횟수 168·165·146 확인
* `[완료]` 최근 100회의 보너스 후속 비교 대상이 99·98·97개인지 확인
* `[대기]` 사용자가 관심 있는 번호와 기간으로 결과를 직접 확인

표시되는 빈도와 비율은 과거 데이터의 동시 출현 기록이며 추천이나 미래 당첨 확률이 아니다.

## 변경 이력

* 2026-07-15: 최초 작성. 전체 원본 수집 완료 상태와 정기 운영 명령 기록.
* 2026-07-15: 수집 실행 이력 확인 방법과 1단계 필수 기능 완료 상태 기록.
* 2026-07-15: 진행률, 회전 파일 로그와 1단계 최종 사용자 확인 절차 기록.
* 2026-07-15: 사용자가 진행률, 실행 이력과 파일 로그의 정상 동작을 최종 확인.
* 2026-07-15: 1단계 전체 코드 리뷰 결과와 다음 단계 전 보완 항목 기록.
* 2026-07-15: P1·P2 리뷰 보완 완료, 전체 테스트와 기존 원본 필수 필드 검사 통과.
* 2026-07-15: SQLite 제외 결정과 원본 검증·정제 CSV 생성 기능 구현.
* 2026-07-17: CSV Repository와 1차 기본 통계 분석 및 사용자 확인 명령 추가.
* 2026-07-17: 분석 요약 JSON, 기간 비교와 출현 간격 분석 및 DB 전 확인 명령 추가.
* 2026-07-17: Docker 기반 PostgreSQL 개발 환경과 사용자 확인 명령 추가.
* 2026-07-17: PostgreSQL 스키마·Repository, CSV 이관과 동등성 검증 결과 추가.
* 2026-07-17: PostgreSQL 기반 번호쌍·3개 조합·특정 번호 동반 출현 분석 추가.
* 2026-07-17: 번호 거리, ±1, 같은 끝수, 연속 그룹과 이전 1·2·3회 중복 분석 추가.
* 2026-07-17: 보너스 번호의 1·2·3회 뒤 일반번호 출현 빈도 분석 추가.
