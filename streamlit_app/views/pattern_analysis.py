"""Matrix and mathematical pattern analysis view."""

from typing import Dict, List, Union

import streamlit as st

from lotto_analysis.models import MatrixAnalysisResult
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import AnalysisService


def render_pattern_analysis(repository: PostgresDrawRepository) -> None:
    """Render matrix, AC, sum-band, diagonal, and consecutive summaries."""
    st.header("패턴 분석")
    recent = st.selectbox(
        "분석 범위", (0, 20, 30, 50, 100), index=0, key="pattern_recent"
    )
    service = AnalysisService(repository)
    matrix = service.matrix(recent=recent)
    patterns = service.patterns(recent=recent)
    basics = service.analyze(recent=recent)
    scope = "전체" if recent == 0 else "최근 {0}회".format(recent)
    st.caption(
        "{0} · {1}~{2}회 · 과거 조합의 형태를 설명하며 미래 예측 지표가 아닙니다.".format(
            scope, matrix.start_draw, matrix.end_draw
        )
    )

    metrics = st.columns(4)
    metrics[0].metric("분석 회차", matrix.total_draws)
    metrics[1].metric("평균 사용 행", "{0:.2f}".format(matrix.average_distinct_rows))
    metrics[2].metric(
        "평균 사용 열", "{0:.2f}".format(matrix.average_distinct_columns)
    )
    metrics[3].metric(
        "연속번호 포함 회차",
        "{0} ({1:.1%})".format(
            basics.summary.consecutive_draw_count,
            basics.summary.consecutive_draw_rate,
        ),
    )

    st.subheader("7×7 번호 행렬 출현 횟수")
    st.dataframe(matrix_count_rows(matrix), hide_index=True, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("AC 값 분포")
        st.bar_chart(
            [
                {"AC": item.value, "회차": item.count}
                for item in patterns.ac_distribution
            ],
            x="AC",
            y="회차",
        )
    with right:
        st.subheader("합계 구간 분포")
        st.bar_chart(
            [
                {
                    "합계 구간": "{0}-{1}".format(item.minimum, item.maximum),
                    "회차": item.count,
                }
                for item in patterns.sum_band_distribution
            ],
            x="합계 구간",
            y="회차",
        )

    st.subheader("대각선 통계")
    st.dataframe(
        [
            {
                "대각선": "주대각선" if item.name == "main" else "역대각선",
                "번호": ", ".join(str(number) for number in item.numbers),
                "총 출현": item.total_appearances,
                "포함 회차": item.draw_count,
                "포함률": item.draw_rate,
            }
            for item in matrix.diagonals
        ],
        hide_index=True,
        width="stretch",
    )


def matrix_count_rows(
    result: MatrixAnalysisResult,
) -> List[Dict[str, Union[int, str]]]:
    """Convert fixed matrix cells into seven display rows."""
    rows: List[Dict[str, Union[int, str]]] = []
    for row_index in range(7):
        row: Dict[str, Union[int, str]] = {"행": row_index + 1}
        for column_index in range(7):
            cell = result.cells[row_index * 7 + column_index]
            row["열 {0}".format(column_index + 1)] = (
                "-" if cell.number is None else "{0} ({1})".format(cell.number, cell.count)
            )
        rows.append(row)
    return rows
