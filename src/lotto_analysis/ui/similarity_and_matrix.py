"""Historical combination similarity and matrix-period comparison view."""

from typing import Dict, List, Union

import streamlit as st

from lotto_analysis.models import MatrixComparisonResult, SimilarityAnalysisResult
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import AnalysisService


def render_similarity_and_matrix(repository: PostgresDrawRepository) -> None:
    """Render similarity summaries and previous-versus-recent matrix changes."""
    st.header("유사도·행렬 기간 비교")
    similarity_tab, matrix_tab = st.tabs(("과거 조합 유사도", "행렬 기간 차이"))
    service = AnalysisService(repository)

    with similarity_tab:
        controls = st.columns(2)
        similarity_recent = controls[0].selectbox(
            "유사도 분석 범위",
            (50, 100, 200, 500),
            index=1,
            key="similarity_recent",
        )
        shown = controls[1].slider(
            "최근 상세 회차", min_value=5, max_value=50, value=20, step=5
        )
        similarity = service.similarity(recent=similarity_recent)
        _render_similarity(similarity, shown)

    with matrix_tab:
        matrix_recent = st.selectbox(
            "비교 기간 길이",
            (20, 30, 50, 100),
            index=2,
            key="matrix_comparison_recent",
        )
        matrix = service.compare_matrices(recent=matrix_recent)
        _render_matrix_comparison(matrix)


def _render_similarity(result: SimilarityAnalysisResult, shown: int) -> None:
    metrics = st.columns(3)
    metrics[0].metric("분석 회차", result.total_draws)
    metrics[1].metric("비교 회차쌍", result.pair_comparisons)
    metrics[2].metric(
        "5개 이상 중복 쌍",
        result.overlap_distribution[5] + result.overlap_distribution[6],
    )
    st.caption(
        "{0}~{1}회 내부의 과거 조합 비교입니다. 높은 유사도는 미래 성과가 아닙니다.".format(
            result.start_draw, result.end_draw
        )
    )
    st.bar_chart(
        [
            {"공통 번호": overlap, "회차쌍": count}
            for overlap, count in enumerate(result.overlap_distribution)
        ],
        x="공통 번호",
        y="회차쌍",
    )
    st.subheader("최근 회차별 가장 유사한 이전 회차")
    st.dataframe(
        similarity_rows(result)[-shown:][::-1], hide_index=True, width="stretch"
    )


def _render_matrix_comparison(result: MatrixComparisonResult) -> None:
    st.caption(
        "직전 {0}~{1}회 대비 최근 {2}~{3}회의 회차당 출현률 차이입니다. "
        "차이는 미래 추세가 아닙니다.".format(
            result.baseline_start_draw,
            result.baseline_end_draw,
            result.comparison_start_draw,
            result.comparison_end_draw,
        )
    )
    valid_cells = [cell for cell in result.cells if cell.number is not None]
    st.bar_chart(
        [
            {"번호": cell.number, "최근-직전 출현률": cell.rate_difference}
            for cell in valid_cells
        ],
        x="번호",
        y="최근-직전 출현률",
    )
    st.subheader("7×7 출현률 차이 행렬")
    st.dataframe(matrix_difference_rows(result), hide_index=True, width="stretch")
    st.dataframe(
        [
            {
                "번호": cell.number,
                "직전 출현": cell.baseline_count,
                "최근 출현": cell.comparison_count,
                "직전 출현률": cell.baseline_rate,
                "최근 출현률": cell.comparison_rate,
                "출현률 차이": cell.rate_difference,
            }
            for cell in valid_cells
        ],
        hide_index=True,
        width="stretch",
    )


def similarity_rows(
    result: SimilarityAnalysisResult,
) -> List[Dict[str, Union[int, float, str]]]:
    """Convert per-draw similarity summaries into display rows."""
    return [
        {
            "회차": item.draw_number,
            "비교한 이전 회차": item.compared_draws,
            "최대 공통 번호": item.maximum_overlap,
            "가장 유사한 이전 회차": (
                ", ".join(str(value) for value in item.most_similar_draws) or "-"
            ),
            "최대 Jaccard": (
                item.maximum_jaccard if item.maximum_jaccard is not None else "-"
            ),
            "3개 중복": item.overlap_3_count,
            "4개 중복": item.overlap_4_count,
            "5개 중복": item.overlap_5_count,
            "6개 중복": item.overlap_6_count,
        }
        for item in result.draws
    ]


def matrix_difference_rows(
    result: MatrixComparisonResult,
) -> List[Dict[str, Union[int, str]]]:
    """Convert 49 fixed comparison cells into a readable matrix."""
    rows: List[Dict[str, Union[int, str]]] = []
    for row_index in range(7):
        row: Dict[str, Union[int, str]] = {"행": row_index + 1}
        for column_index in range(7):
            cell = result.cells[row_index * 7 + column_index]
            row["열 {0}".format(column_index + 1)] = (
                "-"
                if cell.number is None
                else "{0} ({1:+.1%})".format(cell.number, cell.rate_difference)
            )
        rows.append(row)
    return rows
