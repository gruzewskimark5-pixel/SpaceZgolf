import pytest
from app.schemas import RawTelemetryEvent, UnifiedCognitiveEvent
from app.pipeline import UnifiedProtocolPipeline
import uuid
import time
from datetime import datetime, timezone

@pytest.fixture
def pipeline():
    return UnifiedProtocolPipeline()

@pytest.fixture
def valid_telemetry():
    return RawTelemetryEvent(
        event_id=str(uuid.uuid4()),
        entity_id="player_99",
        ts=int(datetime.now(timezone.utc).timestamp() * 1000),
        activity="swing",
        environment="wind_high",
        raw_metrics={
            "accuracy": 0.82,
            "latency_ms": 110.0
        }
    )

def test_pipeline_valid_event(pipeline, valid_telemetry):
    canonical_event = pipeline.process_telemetry(valid_telemetry)

    # 1. Check Schema validation
    assert isinstance(canonical_event, UnifiedCognitiveEvent)
    assert canonical_event.event_id == valid_telemetry.event_id
    assert canonical_event.entity_id == "player_99"

    # 2. Check Outcome Generation
    assert canonical_event.outcome.confidence == 0.92

    # 3. Check Integrity Engine scoring (mocked models)
    # The pace model is 0.85 since latency > 10, total should be around 0.895
    assert canonical_event.integrity_score > 0.8

    # 4. Check that GTE Score was generated
    assert canonical_event.gte_score > 50.0

def test_pipeline_fraudulent_event(pipeline, valid_telemetry):
    # Simulate an impossibly fast superhuman reaction time
    valid_telemetry.raw_metrics["latency_ms"] = 5.0

    canonical_event = pipeline.process_telemetry(valid_telemetry)

    # Integrity score should drop due to the rule in the pace model
    assert canonical_event.integrity_score < 0.8
