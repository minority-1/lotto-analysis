"""Condition-based number generation view."""

from typing import Dict, List, Optional, Tuple, Union

import streamlit as st

from lotto_analysis.generators import (
    FrequencyWeightedStrategy,
    build_frequency_weights,
)
from lotto_analysis.models import GenerationConditions, GenerationResult
from lotto_analysis.repositories import PostgresDrawRepository
from lotto_analysis.services import GenerationService


def render_generation(repository: PostgresDrawRepository) -> None:
    """Render generation controls and transparent combination results."""
    st.header("번호 생성")
    st.caption(
        "설정한 조건을 만족하는 후보를 생성합니다. 결과는 추천 순위나 당첨 확률이 아닙니다."
    )

    with st.form("generation_form"):
        first = st.columns(3)
        strategy_label = first[0].selectbox(
            "생성 전략", ("균등 무작위", "전체 빈도 가중", "최근 빈도 가중")
        )
        count = first[1].number_input(
            "생성 개수", min_value=1, max_value=50, value=5, step=1
        )
        seed_text = first[2].text_input("Random seed", value="42")

        second = st.columns(3)
        required_text = second[0].text_input("포함 번호", placeholder="예: 7, 21")
        excluded_text = second[1].text_input("제외 번호", placeholder="예: 1, 2, 3")
        frequency_recent = second[2].number_input(
            "최근 빈도 원본 회차",
            min_value=1,
            max_value=1000,
            value=50,
            step=1,
            disabled=strategy_label != "최근 빈도 가중",
        )

        odd_range = st.slider("홀수 개수", 0, 6, (0, 6))
        low_range = st.slider("낮은 번호(1~22) 개수", 0, 6, (0, 6))
        sum_range = st.slider("번호 합계", 21, 255, (21, 255))
        prime_range = st.slider("소수 개수", 0, 6, (0, 6))
        ac_range = st.slider("AC 값", 0, 10, (0, 10))

        third = st.columns(4)
        maximum_consecutive = third[0].number_input(
            "최대 연속번호쌍", min_value=0, max_value=5, value=5, step=1
        )
        maximum_historical_overlap = third[1].number_input(
            "과거 조합 최대 중복", min_value=0, max_value=6, value=4, step=1
        )
        maximum_result_overlap = third[2].number_input(
            "결과끼리 최대 중복", min_value=0, max_value=6, value=4, step=1
        )
        maximum_attempts = third[3].number_input(
            "최대 시도", min_value=1, max_value=100000, value=10000, step=1000
        )
        submitted = st.form_submit_button("번호 생성", type="primary")

    if submitted:
        try:
            required = parse_number_text(required_text)
            excluded = parse_number_text(excluded_text)
            seed = parse_optional_seed(seed_text)
            strategy = None
            if strategy_label != "균등 무작위":
                recent = int(frequency_recent) if strategy_label == "최근 빈도 가중" else 0
                weight_draws = repository.list_draws(recent=recent)
                if recent and len(weight_draws) < recent:
                    raise ValueError(
                        "최근 빈도 원본 {0}회가 저장 회차 {1}개를 초과합니다.".format(
                            recent, len(weight_draws)
                        )
                    )
                strategy = FrequencyWeightedStrategy(
                    build_frequency_weights(weight_draws), len(weight_draws)
                )
            conditions = GenerationConditions(
                count=int(count),
                required_numbers=required,
                excluded_numbers=excluded,
                odd_minimum=odd_range[0],
                odd_maximum=odd_range[1],
                low_minimum=low_range[0],
                low_maximum=low_range[1],
                sum_minimum=sum_range[0],
                sum_maximum=sum_range[1],
                prime_minimum=prime_range[0],
                prime_maximum=prime_range[1],
                ac_minimum=ac_range[0],
                ac_maximum=ac_range[1],
                maximum_consecutive_pairs=int(maximum_consecutive),
                maximum_historical_overlap=int(maximum_historical_overlap),
                maximum_result_overlap=int(maximum_result_overlap),
                maximum_attempts=int(maximum_attempts),
                seed=seed,
            )
            st.session_state["generation_result"] = GenerationService(
                repository, strategy
            ).generate(conditions)
            st.session_state.pop("generation_error", None)
        except ValueError as exc:
            st.session_state["generation_error"] = str(exc)
            st.session_state.pop("generation_result", None)

    error = st.session_state.get("generation_error")
    if error:
        st.error(error)
    result = st.session_state.get("generation_result")
    if isinstance(result, GenerationResult):
        render_generation_result(result)


def render_generation_result(result: GenerationResult) -> None:
    """Render one completed or partial generation result."""
    metrics = st.columns(4)
    metrics[0].metric("전략", result.strategy)
    metrics[1].metric(
        "생성 결과", "{0}/{1}".format(len(result.combinations), result.requested_count)
    )
    metrics[2].metric("시도 횟수", result.attempts)
    metrics[3].metric("Seed", result.seed if result.seed is not None else "무작위")
    if result.complete:
        st.success("요청한 조합을 모두 생성했습니다.")
    elif result.message:
        st.warning(result.message)

    st.dataframe(generation_rows(result), hide_index=True, width="stretch")
    if result.strategy_details:
        st.caption(
            "전략 정보: {0}".format(
                ", ".join("{0}={1}".format(*item) for item in result.strategy_details)
            )
        )
    if result.rejection_counts:
        st.caption(
            "조건 거절: {0}".format(
                ", ".join("{0}={1}".format(*item) for item in result.rejection_counts)
            )
        )


def parse_number_text(value: str) -> Tuple[int, ...]:
    """Parse an optional comma-separated unique Lotto number list."""
    if not value.strip():
        return ()
    try:
        numbers = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise ValueError("번호는 쉼표로 구분한 정수여야 합니다.") from exc
    if any(not 1 <= number <= 45 for number in numbers):
        raise ValueError("번호는 1부터 45 사이여야 합니다.")
    if len(set(numbers)) != len(numbers):
        raise ValueError("번호를 중복 입력할 수 없습니다.")
    return tuple(sorted(numbers))


def parse_optional_seed(value: str) -> Optional[int]:
    """Parse a blank random seed or one integer seed."""
    if not value.strip():
        return None
    try:
        return int(value.strip())
    except ValueError as exc:
        raise ValueError("Random seed는 정수이거나 빈 값이어야 합니다.") from exc


def generation_rows(result: GenerationResult) -> List[Dict[str, Union[int, str]]]:
    """Convert generated combinations into transparent display rows."""
    return [
        {
            "번호": ", ".join(str(number) for number in item.numbers),
            "홀:짝": "{0}:{1}".format(item.odd_count, item.even_count),
            "저:고": "{0}:{1}".format(item.low_count, item.high_count),
            "합계": item.number_sum,
            "소수": item.prime_count,
            "AC": item.ac_value,
            "연속번호쌍": item.consecutive_pair_count,
            "과거 최대 중복": item.maximum_historical_overlap,
        }
        for item in result.combinations
    ]
