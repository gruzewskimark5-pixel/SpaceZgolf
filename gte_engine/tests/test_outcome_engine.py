import pytest
from gte_engine.outcome_engine import OutcomeEngine

@pytest.fixture
def engine():
    return OutcomeEngine()

def test_compute_baseline_empty_history(engine):
    assert engine._compute_baseline([], "accuracy") == 0.0
    assert engine._compute_baseline([], "accuracy", default=5.0) == 5.0

def test_compute_baseline_single_item(engine):
    history = [{"accuracy": 0.8}]
    assert engine._compute_baseline(history, "accuracy") == 0.8

def test_compute_baseline_multiple_items(engine):
    history = [{"accuracy": 0.8}, {"accuracy": 0.6}, {"accuracy": 1.0}]
    assert engine._compute_baseline(history, "accuracy") == pytest.approx(0.8)

def test_compute_baseline_missing_key(engine):
    history = [{"other_key": 0.5}, {"other_key": 0.6}]
    assert engine._compute_baseline(history, "accuracy") == 0.0
    assert engine._compute_baseline(history, "accuracy", default=1.0) == 1.0

def test_compute_baseline_mixed_keys(engine):
    history = [{"accuracy": 0.8}, {"other_key": 0.5}, {"accuracy": 1.0}]
    # 0.8 + 0.0 (default) + 1.0 = 1.8 / 3 = 0.6
    assert engine._compute_baseline(history, "accuracy") == pytest.approx(0.6)
    # 0.8 + 2.0 (default) + 1.0 = 3.8 / 3 = 1.2666...
    assert engine._compute_baseline(history, "accuracy", default=2.0) == pytest.approx(1.2666666666666666)

def test_compute_method(engine):
    current_event = {"accuracy": 0.9, "latency": 100.0}
    history = [
        {"accuracy": 0.8, "latency": 150.0},
        {"accuracy": 0.6, "latency": 200.0},
        {"accuracy": 1.0, "latency": 100.0}
    ]

    result = engine.compute(current_event, history)

    # baseline_accuracy = (0.8 + 0.6 + 1.0) / 3 = 0.8
    # baseline_latency = (150.0 + 200.0 + 100.0) / 3 = 150.0

    assert result["baseline_accuracy"] == pytest.approx(0.8)
    assert result["baseline_latency"] == pytest.approx(150.0)

    # accuracy_delta = 0.9 - 0.8 = 0.1
    # latency_delta = 100.0 - 150.0 = -50.0
    assert result["accuracy_delta"] == pytest.approx(0.1)
    assert result["latency_delta"] == pytest.approx(-50.0)
