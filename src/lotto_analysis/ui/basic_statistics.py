"""Basic descriptive statistics view."""

import streamlit as st

from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import AnalysisService


def render_basic_statistics(repository: PostgresDrawRepository) -> None:
    """Render existing basic-analysis service results."""
    st.header("기본 통계")
    recent = st.selectbox(
        "분석 범위", (0, 5, 10, 20, 30, 50, 100), index=0, key="basic_recent"
    )
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
