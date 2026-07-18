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
