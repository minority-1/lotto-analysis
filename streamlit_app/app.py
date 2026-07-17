"""Initial read-only Streamlit UI backed by application services."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from lotto_analysis.config import Settings
from lotto_analysis.database import create_database_engine
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import AnalysisService, DashboardService


st.set_page_config(page_title="Lotto Analysis", page_icon="🎱", layout="wide")


@st.cache_resource
def _repository() -> PostgresDrawRepository:
    """Create and cache the PostgreSQL repository for the UI process."""
    settings = Settings.from_env()
    return PostgresDrawRepository(create_database_engine(settings))


def _dashboard(repository: PostgresDrawRepository) -> None:
    """Render normalized data coverage and the latest winning numbers."""
    summary = DashboardService(repository).summarize()
    st.header("데이터 대시보드")
    if summary.latest_draw is None:
        st.warning("PostgreSQL에 저장된 회차가 없습니다.")
        return

    latest = summary.latest_draw
    columns = st.columns(4)
    columns[0].metric("저장 회차", summary.total_draws)
    columns[1].metric("최신 회차", latest.draw_number)
    columns[2].metric("최신 추첨일", latest.draw_date.isoformat())
    columns[3].metric("누락 회차", len(summary.missing_draw_numbers))

    st.subheader("최근 당첨번호")
    st.write(
        "{0}회: {1} + 보너스 {2}".format(
            latest.draw_number,
            ", ".join(str(number) for number in latest.numbers),
            latest.bonus_number,
        )
    )
    if latest.collected_at is not None:
        st.caption("수집 시각: {0}".format(latest.collected_at.isoformat()))
    if summary.missing_draw_numbers:
        st.warning(
            "누락 회차: {0}".format(
                ", ".join(str(value) for value in summary.missing_draw_numbers)
            )
        )


def _basic_statistics(repository: PostgresDrawRepository) -> None:
    """Render existing basic-analysis service results."""
    st.header("기본 통계")
    recent = st.selectbox("분석 범위", (0, 5, 10, 20, 30, 50, 100), index=0)
    result = AnalysisService(repository).analyze(recent=recent)
    scope = "전체" if recent == 0 else "최근 {0}회".format(recent)
    st.caption(
        "{0} · {1}~{2}회 · 과거 출현을 설명하며 미래 당첨 확률이 아닙니다.".format(
            scope, result.start_draw, result.end_draw
        )
    )

    rows = [
        {
            "번호": item.number,
            "일반번호 출현": item.main_count,
            "회차당 출현률": item.main_rate,
            "현재 미출현 회차": item.absence_draws,
        }
        for item in result.number_statistics
    ]
    st.bar_chart(rows, x="번호", y="일반번호 출현")
    st.dataframe(rows, hide_index=True, width="stretch")


def main() -> None:
    """Render the selected initial UI page."""
    st.title("한국 로또 6/45 분석")
    page = st.sidebar.radio("화면", ("대시보드", "기본 통계"))
    try:
        repository = _repository()
        if page == "대시보드":
            _dashboard(repository)
        else:
            _basic_statistics(repository)
    except (SQLAlchemyError, ValueError, RuntimeError) as exc:
        st.error("화면을 불러오지 못했습니다: {0}".format(exc))


main()
