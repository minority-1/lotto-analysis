# Lotto Analysis Project Instructions

## Project overview

이 프로젝트는 한국 로또 6/45 데이터를 수집하고 통계 분석하며, 조건 기반 번호 조합 생성과 백테스트를 제공하는 애플리케이션이다.

전체 요구사항은 `docs/PROJECT_SPEC.md`를 기준으로 한다.

개발 과정에서 확정된 결정은 `docs/DECISIONS.md`에 기록한다.

## Architecture

최종 구조는 다음을 목표로 한다.

* 분석 엔진 및 백엔드: Python
* 초기 분석 UI: Streamlit
* API: FastAPI
* 최종 사용자 UI: Next.js
* 초기 데이터베이스: SQLite
* 최종 데이터베이스: PostgreSQL

Python 분석 엔진은 Streamlit, FastAPI, Next.js에 종속되지 않아야 한다.

Streamlit과 FastAPI는 동일한 Service 계층을 사용해야 한다.

Next.js는 FastAPI를 통해서만 Python 백엔드 기능을 사용한다.

## Development rules

* 현재 요청받은 단계만 구현한다.
* 관련 없는 미래 기능을 미리 구현하지 않는다.
* 한 파일에 모든 기능을 작성하지 않는다.
* 데이터 수집, 검증, 저장, 분석, 번호 생성, 백테스트, UI를 분리한다.
* 파일과 디렉터리 경로에는 `pathlib`을 사용한다.
* Python 타입 힌트를 작성한다.
* 주요 함수와 클래스에는 docstring을 작성한다.
* 예외 처리와 logging을 적용한다.
* 설정값과 경로를 코드에 하드코딩하지 않는다.
* Python 3.9 이상에서 동작하도록 작성한다.
* macOS와 Windows에서 모두 실행 가능한 구조를 유지한다.
* 분석 로직을 Streamlit 화면이나 FastAPI 라우터에 직접 작성하지 않는다.
* 통계 결과를 당첨 확률 또는 미래 예측으로 표현하지 않는다.
* 사용자가 승인하지 않은 대규모 구조 변경을 하지 않는다.

## Work process

코드를 수정하기 전에 다음을 확인한다.

1. `docs/PROJECT_SPEC.md`
2. `docs/DECISIONS.md`
3. 현재 프로젝트 구조
4. 기존 테스트와 실행 방법

구현 전에는 이번 작업에서 생성하거나 수정할 파일을 먼저 설명한다.

구현 후에는 다음을 수행한다.

1. 변경 파일 목록 확인
2. 테스트 실행
3. 실패 원인 수정
4. 실행 방법 설명
5. 남은 문제와 다음 단계 정리

## Testing

새로운 핵심 기능에는 테스트를 추가한다.

버그 수정 시 가능하면 해당 버그를 재현하는 테스트를 먼저 작성한다.

테스트를 실행하지 못했다면 실행하지 못한 이유를 명확히 설명한다.

## Documentation

설계나 기술 선택이 확정되면 `docs/DECISIONS.md`에 기록한다.

프로젝트 실행 방법이 변경되면 `README.md`도 함께 수정한다.
