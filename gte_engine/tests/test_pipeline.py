import pytest
from gte_engine.pipeline import UnifiedProtocolPipeline
from gte_engine.models import EventIntegrity

@pytest.fixture
def pipeline():
    return UnifiedProtocolPipeline()

def test_run_integrity_checks(pipeline):
    # Setup test event data
    test_event = {
        "entity_id": "test_user_1",
        "decision": {
            "latency_ms": 150.0
        }
    }

    # Execute the method under test
    integrity = pipeline._run_integrity_checks(test_event)

    # Validate return type
    assert isinstance(integrity, EventIntegrity)

    # Validate output values match the expected mocked output
    assert integrity.score == 0.95
    assert "gps_noise_low" in integrity.flags
    assert len(integrity.flags) == 1

    assert "hr_signature" in integrity.factors
    assert integrity.factors["hr_signature"] == 0.92

    assert "behavior_outlier" in integrity.factors
    assert integrity.factors["behavior_outlier"] == 0.85
    assert len(integrity.factors) == 2

def test_run_integrity_checks_empty_event(pipeline):
    # Execute the method with empty event dictionary to ensure it handles missing keys safely
    integrity = pipeline._run_integrity_checks({})

    # Validate return type
    assert isinstance(integrity, EventIntegrity)

    # Validate output values
    assert integrity.score == 0.95
    assert "gps_noise_low" in integrity.flags
    assert integrity.factors["hr_signature"] == 0.92
    assert integrity.factors["behavior_outlier"] == 0.85
