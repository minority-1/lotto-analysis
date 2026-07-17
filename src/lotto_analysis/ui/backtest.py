"""Leakage-safe generation backtest view."""

from typing import Dict, List, Tuple, Union

import streamlit as st

from lotto_analysis.models import BacktestExperimentResult, BacktestResult
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import BacktestExperimentService, BacktestService


def render_backtest(repository: PostgresDrawRepository) -> None:
    """Render individual and repeated comparable historical backtests."""
    st.header("생성 전략 백테스트")
    st.caption(
        "각 목표 회차보다 이전 데이터만 사용합니다. 과거 결과는 미래 성과를 보장하지 않습니다."
    )
    detail_tab, experiment_tab = st.tabs(("단일 상세", "반복 전략 비교"))

    with detail_tab:
        _detail_form(repository)
        result = st.session_state.get("backtest_result")
        if isinstance(result, BacktestResult):
            render_backtest_result(result)

    with experiment_tab:
        _experiment_form(repository)
        experiment = st.session_state.get("backtest_experiment")
        if isinstance(experiment, BacktestExperimentResult):
            render_experiment_result(experiment)


def _detail_form(repository: PostgresDrawRepository) -> None:
    with st.form("backtest_detail_form"):
        controls = st.columns(5)
        strategy = controls[0].selectbox(
            "전략", ("균등 무작위", "전체 빈도 가중", "최근 빈도 가중")
        )
        targets = controls[1].number_input(
            "목표 회차 수", min_value=1, max_value=200, value=20, step=1
        )
        combinations = controls[2].number_input(
            "회차당 조합", min_value=1, max_value=100, value=5, step=1
        )
        seed = controls[3].number_input("기준 seed", value=42, step=1)
        recent = controls[4].number_input(
            "최근 빈도 원본",
            min_value=1,
            max_value=1000,
            value=50,
            step=1,
            disabled=strategy != "최근 빈도 가중",
        )
        submitted = st.form_submit_button("상세 백테스트 실행", type="primary")
    if not submitted:
        return
    strategy_name = "uniform" if strategy == "균등 무작위" else "frequency"
    weight_recent = int(recent) if strategy == "최근 빈도 가중" else 0
    st.session_state["backtest_result"] = BacktestService(repository).run(
        strategy_name=strategy_name,
        target_count=int(targets),
        combinations_per_target=int(combinations),
        base_seed=int(seed),
        weight_recent=weight_recent,
    )


def _experiment_form(repository: PostgresDrawRepository) -> None:
    with st.form("backtest_experiment_form"):
        controls = st.columns(4)
        targets = controls[0].number_input(
            "비교 목표 회차 수", min_value=1, max_value=200, value=20, step=1
        )
        combination_counts = controls[1].multiselect(
            "회차당 조합 수", (1, 5, 10, 50), default=(1, 5, 10, 50)
        )
        seeds_text = controls[2].text_input("Seeds", value="41,42,43")
        frequency_recent = controls[3].number_input(
            "최근 빈도 원본", min_value=1, max_value=1000, value=50, step=1
        )
        submitted = st.form_submit_button("반복 비교 실행")
    if not submitted:
        return
    if not combination_counts:
        raise ValueError("회차당 조합 수를 하나 이상 선택해야 합니다.")
    st.session_state["backtest_experiment"] = BacktestExperimentService(
        repository
    ).run(
        target_count=int(targets),
        combination_counts=tuple(int(value) for value in combination_counts),
        seeds=parse_seed_list(seeds_text),
        frequency_recent=int(frequency_recent),
    )


def render_backtest_result(result: BacktestResult) -> None:
    """Render aggregate distributions and per-target detail."""
    metrics = st.columns(4)
    metrics[0].metric("전략", result.strategy)
    metrics[1].metric("목표 완료", "{0}/{1}".format(result.complete_targets, result.target_count))
    metrics[2].metric("생성 조합", result.total_generated_combinations)
    metrics[3].metric("보너스 포함", result.bonus_match_count)
    left, right = st.columns(2)
    with left:
        st.subheader("전체 조합 일반번호 일치")
        st.bar_chart(distribution_rows(result.main_match_distribution), x="일치", y="개수")
    with right:
        st.subheader("목표 회차별 최고 일치")
        st.bar_chart(distribution_rows(result.best_match_distribution), x="일치", y="개수")
    st.dataframe(backtest_target_rows(result), hide_index=True, width="stretch")


def render_experiment_result(result: BacktestExperimentResult) -> None:
    """Render strategy-and-combination-count repeated summaries."""
    st.caption(
        "목표 {0}회 · seeds {1}. 같은 조합 수 행끼리 비교해야 합니다.".format(
            result.target_count, ", ".join(str(seed) for seed in result.seeds)
        )
    )
    st.dataframe(
        [
            {
                "전략": item.strategy_label,
                "회차당 조합": item.combinations_per_target,
                "완료 실행": "{0}/{1}".format(item.complete_runs, item.run_count),
                "생성 조합": item.total_generated_combinations,
                "평균 일치": item.average_main_match,
                "평균 최고 일치": item.average_best_match,
                "보너스 포함": item.bonus_match_count,
            }
            for item in result.summaries
        ],
        hide_index=True,
        width="stretch",
    )


def parse_seed_list(value: str) -> Tuple[int, ...]:
    """Parse a non-empty comma-separated unique integer seed list."""
    try:
        seeds = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise ValueError("Seeds는 쉼표로 구분한 정수여야 합니다.") from exc
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Seeds는 비어 있지 않은 고유 정수 목록이어야 합니다.")
    return seeds


def distribution_rows(values: Tuple[int, ...]) -> List[Dict[str, int]]:
    """Convert a fixed 0-through-6 distribution into chart rows."""
    return [{"일치": index, "개수": count} for index, count in enumerate(values)]


def backtest_target_rows(
    result: BacktestResult,
) -> List[Dict[str, Union[int, str]]]:
    """Convert target-level outcomes into concise display rows."""
    return [
        {
            "목표 회차": item.target_draw_number,
            "학습 범위": "{0}-{1}".format(
                item.training_start_draw, item.training_end_draw
            ),
            "생성": "{0}/{1}".format(
                item.generated_combinations, item.requested_combinations
            ),
            "최고 일치": item.best_main_match,
            "Seed": item.seed,
        }
        for item in result.targets
    ]
