"""Period comparison and historical appearance-gap view."""

from typing import Dict, List, Union

import streamlit as st

from lotto_analysis.models import GapAnalysisResult, PeriodComparisonResult
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import AnalysisService


def render_period_and_gaps(repository: PostgresDrawRepository) -> None:
    """Render rate comparisons and descriptive number appearance gaps."""
    st.header("기간 비교·출현 간격")
    comparison_tab, gap_tab = st.tabs(("기간 비교", "출현 간격"))
    service = AnalysisService(repository)

    with comparison_tab:
        controls = st.columns(2)
        recent = controls[0].selectbox(
            "최근 비교 회차",
            (10, 20, 30, 50, 100),
            index=3,
            key="comparison_recent",
        )
        baseline = controls[1].radio(
            "기준 기간",
            ("직전 동일 기간", "전체 기간"),
            horizontal=True,
            key="comparison_baseline",
        )
        comparison = service.compare(
            recent=recent, against_all=baseline == "전체 기간"
        )
        _render_comparison(comparison)

    with gap_tab:
        gap_recent = st.selectbox(
            "간격 분석 범위",
            (0, 20, 30, 50, 100),
            index=0,
            key="gap_recent",
        )
        gaps = service.gaps(recent=gap_recent)
        _render_gaps(gaps, gap_recent)


def _render_comparison(result: PeriodComparisonResult) -> None:
    """Render normalized rate and rank changes between two periods."""
    st.caption(
        "기준 {0}~{1}회({2}회) 대비 최근 {3}~{4}회({5}회). "
        "비율 차이는 미래 추세가 아닙니다.".format(
            result.baseline_start_draw,
            result.baseline_end_draw,
            result.baseline_total_draws,
            result.comparison_start_draw,
            result.comparison_end_draw,
            result.comparison_total_draws,
        )
    )
    rows = comparison_rows(result)
    st.bar_chart(rows, x="번호", y=["기준 출현률", "최근 출현률"])
    st.dataframe(rows, hide_index=True, width="stretch")


def _render_gaps(result: GapAnalysisResult, recent: int) -> None:
    """Render historical gap statistics without predictive wording."""
    scope = "전체" if recent == 0 else "최근 {0}회".format(recent)
    st.caption(
        "{0} · {1}~{2}회. 출현 간격은 과거 분포이며 다음 출현 시점을 예측하지 않습니다.".format(
            scope, result.start_draw, result.end_draw
        )
    )
    rows = gap_rows(result)
    most_absent = sorted(rows, key=lambda item: (-int(item["현재 미출현"]), int(item["번호"])))
    st.subheader("현재 미출현 회차 상위 10개")
    st.bar_chart(most_absent[:10], x="번호", y="현재 미출현")
    st.dataframe(rows, hide_index=True, width="stretch")


def comparison_rows(
    result: PeriodComparisonResult,
) -> List[Dict[str, Union[int, float]]]:
    """Convert period comparison results into display rows."""
    return [
        {
            "번호": item.number,
            "기준 출현": item.baseline_count,
            "최근 출현": item.comparison_count,
            "기준 출현률": item.baseline_rate,
            "최근 출현률": item.comparison_rate,
            "출현률 차이": item.rate_difference,
            "기준 순위": item.baseline_rank,
            "최근 순위": item.comparison_rank,
            "순위 변화": item.rank_change,
        }
        for item in result.numbers
    ]


def gap_rows(result: GapAnalysisResult) -> List[Dict[str, Union[int, float, str]]]:
    """Convert optional gap statistics into display-safe rows."""
    return [
        {
            "번호": item.number,
            "출현 횟수": len(item.appearance_draws),
            "평균 간격": _optional_number(item.mean_gap),
            "중앙 간격": _optional_number(item.median_gap),
            "최소 간격": _optional_number(item.minimum_gap),
            "최대 간격": _optional_number(item.maximum_gap),
            "최근 간격": _optional_number(item.latest_gap),
            "현재 미출현": item.current_absence,
            "표준편차": _optional_number(item.gap_standard_deviation),
        }
        for item in result.numbers
    ]


def _optional_number(value: Union[int, float, None]) -> Union[int, float, str]:
    return "-" if value is None else value
