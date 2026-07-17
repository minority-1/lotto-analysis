"""Historical number relationship analysis view."""

from typing import Dict, List, Tuple, Union

import streamlit as st

from lotto_analysis.models import CombinationFrequency
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import AnalysisService


def render_relationship_analysis(repository: PostgresDrawRepository) -> None:
    """Render pair, triple, companion, distance, and lag relationships."""
    st.header("관계 분석")
    controls = st.columns(3)
    recent = controls[0].selectbox(
        "분석 범위", (0, 20, 50, 100), index=0, key="relationship_recent"
    )
    anchor = controls[1].selectbox(
        "기준 번호", tuple(range(1, 46)), index=0, key="relationship_anchor"
    )
    top = controls[2].slider(
        "상위 결과 수", min_value=5, max_value=30, value=10, step=5
    )

    result = AnalysisService(repository).relationships(
        recent=recent, anchor_number=anchor
    )
    scope = "전체" if recent == 0 else "최근 {0}회".format(recent)
    st.caption(
        "{0} · {1}~{2}회 · 과거 동시 출현 관계이며 미래 당첨 가능성을 뜻하지 않습니다.".format(
            scope, result.start_draw, result.end_draw
        )
    )

    metrics = st.columns(4)
    metrics[0].metric("분석 회차", result.total_draws)
    metrics[1].metric("기준 번호 출현", result.anchor_appearance_count)
    metrics[2].metric(
        "±1 포함 회차",
        "{0} ({1:.1%})".format(
            result.adjacent_draw_count, result.adjacent_draw_rate
        ),
    )
    metrics[3].metric(
        "같은 끝수 포함 회차",
        "{0} ({1:.1%})".format(
            result.same_last_digit_draw_count, result.same_last_digit_draw_rate
        ),
    )

    st.subheader("{0}번과 함께 나온 번호".format(anchor))
    companion_rows = [
        {
            "번호": item.number,
            "동시 출현": item.count,
            "조건부 비율": item.conditional_rate,
        }
        for item in result.companions[:top]
    ]
    if companion_rows:
        st.bar_chart(companion_rows, x="번호", y="동시 출현")
        st.dataframe(companion_rows, hide_index=True, width="stretch")
    else:
        st.info("선택한 범위에서 기준 번호가 출현하지 않았습니다.")

    pairs, triples = st.columns(2)
    with pairs:
        st.subheader("상위 번호쌍")
        st.dataframe(
            combination_rows(result.pairs[:top]), hide_index=True, width="stretch"
        )
    with triples:
        st.subheader("상위 3개 조합")
        st.dataframe(
            combination_rows(result.triples[:top]), hide_index=True, width="stretch"
        )

    st.subheader("번호 간 거리 분포")
    st.bar_chart(
        [
            {
                "거리": item.distance,
                "번호쌍 관측": item.count,
                "관측 비율": item.observation_rate,
            }
            for item in result.distances
        ],
        x="거리",
        y="번호쌍 관측",
    )

    lag_column, bonus_column = st.columns(2)
    with lag_column:
        st.subheader("이전 회차 중복")
        st.dataframe(
            [
                {
                    "이전 회차": item.lag,
                    "비교 회차": item.compared_draws,
                    "평균 중복": item.average_overlap,
                    "0~6개 분포": ", ".join(
                        str(value) for value in item.overlap_distribution
                    ),
                }
                for item in result.lag_overlaps
            ],
            hide_index=True,
            width="stretch",
        )
    with bonus_column:
        st.subheader("보너스 번호의 후속 일반번호 출현")
        st.dataframe(
            [
                {
                    "이후 회차": item.lag,
                    "비교 가능 회차": item.eligible_draws,
                    "일반번호 출현": item.main_appearances,
                    "출현률": item.appearance_rate,
                }
                for item in result.bonus_followups
            ],
            hide_index=True,
            width="stretch",
        )


def combination_rows(
    items: Tuple[CombinationFrequency, ...],
) -> List[Dict[str, Union[int, float, str]]]:
    """Convert pair or triple frequency models into display rows."""
    return [
        {
            "번호": ", ".join(str(number) for number in item.numbers),
            "출현": item.count,
            "회차당 비율": item.draw_rate,
        }
        for item in items
    ]
