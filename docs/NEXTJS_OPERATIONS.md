# Next.js 운영 안내

## 환경 설정

* `LOTTO_API_BASE_URL`: Next.js 서버에서 접근할 FastAPI `/api` 주소
* `LOTTO_API_TIMEOUT_MS`: FastAPI 요청 제한 시간. 기본 10,000ms, 허용 범위 100~120,000ms

범위를 벗어나거나 숫자가 아닌 타임아웃 값은 안전한 기본값 10,000ms로 대체한다. 브라우저에 노출해야 하는 값이 아니므로 두 설정 모두 서버 환경변수로 관리한다.

## 상태 점검

배포 플랫폼의 health check는 `GET /api/health`를 사용한다.

* `200`: Next.js가 FastAPI의 process health 응답을 확인함
* `503`: FastAPI 연결 실패, 응답 오류 또는 타임아웃

이 경로는 PostgreSQL 준비 상태가 아니라 Next.js와 FastAPI 프로세스 사이의 연결만 확인한다. 데이터베이스까지 포함하는 readiness check는 실제 배포 인프라 요구가 정해질 때 별도 경로로 추가한다.

## 오류 로그와 요청 ID

Next.js가 FastAPI를 호출할 때 요청별 UUID를 `X-Request-ID`로 전달한다. 실패 로그는 표준 오류 출력에 한 줄 JSON으로 기록하며 다음 필드를 포함한다.

* `event`, `timestamp`, `level`
* `request_id`, `method`, `path`, `status`, `duration_ms`, `error`

요청 본문, 전체 API URL과 환경변수는 로그에 남기지 않는다. 배포 환경에서는 표준 출력을 수집하는 플랫폼 로그에서 `event=fastapi_request_failed` 또는 health 응답의 `request_id`로 검색한다.
