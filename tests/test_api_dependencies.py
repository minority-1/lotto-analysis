from types import SimpleNamespace

from lotto_analysis.api import dependencies


def test_dispose_engine_closes_and_clears_cached_pool(monkeypatch) -> None:
    class FakeEngine:
        disposed = False

        def dispose(self) -> None:
            self.disposed = True

    engine = FakeEngine()
    cleared = {"value": False}

    def cached_engine() -> FakeEngine:
        return engine

    cached_engine.cache_info = lambda: SimpleNamespace(currsize=1)  # type: ignore[attr-defined]
    cached_engine.cache_clear = lambda: cleared.update(value=True)  # type: ignore[attr-defined]
    monkeypatch.setattr(dependencies, "get_engine", cached_engine)

    dependencies.dispose_engine()

    assert engine.disposed is True
    assert cleared["value"] is True
