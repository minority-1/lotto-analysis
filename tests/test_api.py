from datetime import date

from fastapi.testclient import TestClient

from lotto_analysis.api.dependencies import get_draw_repository
from lotto_analysis.api.main import create_app
from lotto_analysis.models import LottoDraw
from lotto_analysis.repositories import InMemoryDrawRepository


def _draw(draw_number: int, numbers: tuple) -> LottoDraw:
    return LottoDraw(
        draw_number=draw_number,
        draw_date=date(2026, 7, draw_number),
        numbers=numbers,  # type: ignore[arg-type]
        bonus_number=45,
        first_prize_winners=1,
        first_prize_amount=100,
        total_sales_amount=1000,
        collected_at=None,
    )


def _client() -> TestClient:
    draws = (
        _draw(1, (1, 2, 3, 4, 5, 6)),
        _draw(2, (7, 8, 9, 10, 11, 12)),
    )
    application = create_app()
    application.dependency_overrides[get_draw_repository] = lambda: InMemoryDrawRepository(
        draws
    )
    return TestClient(application)


def _backtest_client() -> TestClient:
    draws = (
        _draw(1, (1, 2, 3, 4, 5, 6)),
        _draw(2, (7, 8, 9, 10, 11, 12)),
        _draw(3, (13, 14, 15, 16, 17, 18)),
        _draw(4, (19, 20, 21, 22, 23, 24)),
        _draw(5, (25, 26, 27, 28, 29, 30)),
    )
    application = create_app()
    application.dependency_overrides[get_draw_repository] = lambda: InMemoryDrawRepository(
        draws
    )
    return TestClient(application)


def test_health_and_openapi_are_available() -> None:
    client = _client()

    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/openapi.json").status_code == 200


def test_draws_and_dashboard_return_explicit_json_contracts() -> None:
    client = _client()

    draws = client.get("/api/draws", params={"recent": 1})
    dashboard = client.get("/api/dashboard")

    assert draws.status_code == 200
    assert draws.json()[0]["draw_number"] == 2
    assert draws.json()[0]["numbers"] == [7, 8, 9, 10, 11, 12]
    assert dashboard.status_code == 200
    assert dashboard.json()["total_draws"] == 2
    assert dashboard.json()["latest_draw"]["draw_number"] == 2
    assert dashboard.json()["missing_draw_numbers"] == []


def test_basic_analysis_uses_service_and_rejects_shortened_recent_range() -> None:
    client = _client()

    response = client.get("/api/analysis/basic", params={"recent": 2})
    too_many = client.get("/api/analysis/basic", params={"recent": 3})

    assert response.status_code == 200
    assert response.json()["total_draws"] == 2
    assert len(response.json()["number_statistics"]) == 45
    assert too_many.status_code == 422
    assert too_many.json()["detail"] == "recent 3 exceeds available draw count 2"


def test_query_validation_rejects_negative_recent() -> None:
    response = _client().get("/api/draws", params={"recent": -1})

    assert response.status_code == 422


def test_period_comparison_returns_normalized_rates_and_ranges() -> None:
    response = _client().get(
        "/api/analysis/compare", params={"recent": 1, "against_all": False}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["baseline_start_draw"] == 1
    assert body["comparison_end_draw"] == 2
    assert body["baseline_total_draws"] == 1
    assert body["comparison_total_draws"] == 1
    assert len(body["numbers"]) == 45
    assert body["numbers"][0]["baseline_rate"] == 1.0
    assert body["numbers"][0]["comparison_rate"] == 0.0


def test_gap_analysis_returns_all_numbers_and_rejects_too_large_range() -> None:
    client = _client()

    response = client.get("/api/analysis/gaps", params={"recent": 2})
    too_many = client.get("/api/analysis/gaps", params={"recent": 3})

    assert response.status_code == 200
    assert response.json()["start_draw"] == 1
    assert response.json()["end_draw"] == 2
    assert len(response.json()["numbers"]) == 45
    assert response.json()["numbers"][0]["appearance_draws"] == [1]
    assert too_many.status_code == 422


def test_relationship_and_pattern_endpoints_return_nested_contracts() -> None:
    client = _client()

    relationships = client.get(
        "/api/analysis/relationships", params={"recent": 2, "number": 1}
    )
    patterns = client.get("/api/analysis/patterns", params={"recent": 2})

    assert relationships.status_code == 200
    assert relationships.json()["total_draws"] == 2
    assert relationships.json()["anchor_number"] == 1
    assert relationships.json()["pairs"][0]["numbers"] == [1, 2]
    assert len(relationships.json()["lag_overlaps"]) == 3
    assert patterns.status_code == 200
    assert patterns.json()["total_draws"] == 2
    assert len(patterns.json()["draws"]) == 2
    assert sum(item["count"] for item in patterns.json()["ac_distribution"]) == 2


def test_matrix_and_similarity_endpoints_preserve_invariants() -> None:
    client = _client()

    matrix = client.get("/api/analysis/matrix", params={"recent": 2})
    comparison = client.get(
        "/api/analysis/matrix/compare", params={"recent": 1}
    )
    similarity = client.get("/api/analysis/similarity", params={"recent": 2})

    assert matrix.status_code == 200
    assert len(matrix.json()["cells"]) == 49
    assert sum(matrix.json()["row_totals"]) == 12
    assert comparison.status_code == 200
    assert len(comparison.json()["cells"]) == 49
    assert comparison.json()["baseline_start_draw"] == 1
    assert comparison.json()["comparison_end_draw"] == 2
    assert similarity.status_code == 200
    assert similarity.json()["pair_comparisons"] == 1
    assert sum(similarity.json()["overlap_distribution"]) == 1


def test_generation_endpoint_is_reproducible_and_returns_characteristics() -> None:
    client = _client()
    payload = {
        "strategy": "uniform",
        "count": 2,
        "required_numbers": [20],
        "excluded_numbers": [21],
        "seed": 42,
    }

    first = client.post("/api/combinations/generate", json=payload)
    second = client.post("/api/combinations/generate", json=payload)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()["complete"] is True
    assert len(first.json()["combinations"]) == 2
    assert all(20 in item["numbers"] for item in first.json()["combinations"])
    assert all(21 not in item["numbers"] for item in first.json()["combinations"])
    assert "ac_value" in first.json()["combinations"][0]


def test_frequency_generation_and_domain_validation_errors() -> None:
    client = _client()
    frequency = client.post(
        "/api/combinations/generate",
        json={"strategy": "frequency", "weight_recent": 2, "count": 1, "seed": 7},
    )
    overlap = client.post(
        "/api/combinations/generate",
        json={"required_numbers": [1], "excluded_numbers": [1]},
    )
    invalid_weight = client.post(
        "/api/combinations/generate",
        json={"strategy": "uniform", "weight_recent": 10},
    )

    assert frequency.status_code == 200
    assert frequency.json()["strategy"] == "frequency_weighted"
    assert frequency.json()["strategy_details"][0] == ["source_draws", "2"]
    assert overlap.status_code == 422
    assert "must not overlap" in overlap.json()["detail"]
    assert invalid_weight.status_code == 422
    assert "requires the frequency strategy" in invalid_weight.json()["detail"]


def test_detailed_backtest_api_preserves_training_boundary_and_distributions() -> None:
    response = _backtest_client().post(
        "/api/backtests/run",
        json={
            "strategy": "uniform",
            "target_count": 2,
            "combinations_per_target": 3,
            "base_seed": 100,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["complete_targets"] == 2
    assert body["total_generated_combinations"] == 6
    assert sum(body["main_match_distribution"]) == 6
    assert sum(body["best_match_distribution"]) == 2
    assert body["targets"][0]["target_draw_number"] == 4
    assert body["targets"][0]["training_end_draw"] == 3
    assert body["targets"][1]["target_draw_number"] == 5
    assert body["targets"][1]["training_end_draw"] == 4


def test_backtest_experiment_api_builds_comparable_summary_grid() -> None:
    response = _backtest_client().post(
        "/api/backtests/experiment",
        json={
            "target_count": 2,
            "combination_counts": [1, 2],
            "seeds": [10, 20],
            "frequency_recent": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["summaries"]) == 6
    assert body["seeds"] == [10, 20]
    assert body["combination_counts"] == [1, 2]
    for summary in body["summaries"]:
        assert summary["complete_runs"] == 2
        assert summary["run_count"] == 2
        assert sum(summary["best_match_distribution"]) == 4


def test_backtest_api_rejects_future_leakage_prone_target_range() -> None:
    response = _backtest_client().post(
        "/api/backtests/run",
        json={"target_count": 5, "combinations_per_target": 1},
    )

    assert response.status_code == 422
    assert "requires more than 5 available draws" in response.json()["detail"]
