"""Data coverage dashboard view."""

import streamlit as st

from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import DashboardService


def render_dashboard(repository: PostgresDrawRepository) -> None:
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
