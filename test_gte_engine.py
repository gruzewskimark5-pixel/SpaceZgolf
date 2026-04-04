import uuid
from datetime import datetime, timezone
from gte_engine.models import UnifiedCognitiveEvent
from gte_engine.pipeline import UnifiedProtocolPipeline

def test_unified_cognitive_event():
    # Constructing a sample payload simulating what Digital Glass produces
    sample_raw_event = {
        "event_id": str(uuid.uuid4()),
        "athlete_id": "athlete_123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "hole_id": "miakka_7"
        },
        "telemetry": {
            "hrv": 65,
            "focus_index": 82
        },
        "decision": {
            "latency_ms": 110.0,
            "club_selected": "7_iron",
            "confidence_score": 90.0,
            "execution_complexity": 65.0
        },
        "trace": [],
        "outcome": {
            "accuracy": 85.0,
            "latency": 110.0
        }
    }

    # Simulate history for Outcome Engine
    history = [
        {"accuracy": 80.0, "latency": 120.0},
        {"accuracy": 78.0, "latency": 125.0},
        {"accuracy": 82.0, "latency": 115.0}
    ] # avg accuracy: 80.0, avg latency: 120.0

    pipeline = UnifiedProtocolPipeline()
    unified_event = pipeline.process_event(sample_raw_event, history)

    # Asserting Schema constraints
    assert isinstance(unified_event, UnifiedCognitiveEvent)

    # Asserting Outcome Engine computations
    assert unified_event.outcome.accuracy == 85.0
    assert unified_event.outcome.performance_delta == 5.0  # 85 - 80
    assert unified_event.outcome.latency == 110.0

    # Asserting adapter translation to GTE
    assert unified_event.scoring.integrity_score == 0.95
    assert unified_event.scoring.performance_score == 135.0  # 85 + (5.0 * 10)

if __name__ == "__main__":
    test_unified_cognitive_event()
    print("Tests passed.")
