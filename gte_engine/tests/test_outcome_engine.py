import pytest
from gte_engine.outcome_engine import OutcomeEngine

def test_compute_empty_history():
    engine = OutcomeEngine()
    current_event = {"accuracy": 0.8, "latency": 100.0}
    result = engine.compute(current_event, [])

    assert result["baseline_accuracy"] == 0.8
    assert result["baseline_latency"] == 100.0
    assert result["accuracy_delta"] == 0.0
    assert result["latency_delta"] == 0.0

def test_compute_with_history():
    engine = OutcomeEngine()
    current_event = {"accuracy": 0.9, "latency": 120.0}
    history = [
        {"accuracy": 0.8, "latency": 100.0},
        {"accuracy": 0.7, "latency": 110.0}
    ]
    result = engine.compute(current_event, history)

    assert result["baseline_accuracy"] == 0.75
    assert result["baseline_latency"] == 105.0
    assert result["accuracy_delta"] == pytest.approx(0.15)
    assert result["latency_delta"] == 15.0

def test_compute_history_truncation():
    engine = OutcomeEngine()
    current_event = {"accuracy": 0.9, "latency": 100.0}
    # Create 15 history events
    # The first 5 are 0.0, the last 10 are 0.5
    history = [
        {"accuracy": 0.0, "latency": 0.0} for _ in range(5)
    ] + [
        {"accuracy": 0.5, "latency": 50.0} for _ in range(10)
    ]
    result = engine.compute(current_event, history)

    # Baseline should only consider the last 10 events (0.5 and 50.0)
    assert result["baseline_accuracy"] == 0.5
    assert result["baseline_latency"] == 50.0
    assert result["accuracy_delta"] == pytest.approx(0.4)
    assert result["latency_delta"] == 50.0

def test_compute_missing_keys():
    engine = OutcomeEngine()
    current_event = {}  # missing accuracy and latency
    history = [
        {"other_key": "value"} # missing accuracy and latency
    ]
    result = engine.compute(current_event, history)

    assert result["baseline_accuracy"] == 0.0
    assert result["baseline_latency"] == 0.0
    assert result["accuracy_delta"] == 0.0
    assert result["latency_delta"] == 0.0
