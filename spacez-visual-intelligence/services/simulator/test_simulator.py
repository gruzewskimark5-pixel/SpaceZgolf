from simulator import generate_random_event, generate_feedback

def test_generate_event():
    event = generate_random_event(1)
    assert event.event_id == "evt_000001"
    assert event.event_type in ["kill", "knockdown", "zone_close", "celebration", "revive", "third_party", "champion_eliminated"]
    assert 0 <= event.salience.narrative <= 1.0

def test_generate_feedback():
    event = generate_random_event(1)
    feedback = generate_feedback(event)
    assert feedback.event_id == "evt_000001"
    assert 0 <= feedback.engagement_score <= 1.0
    assert -1.0 <= feedback.retention_delta <= 1.0
    assert feedback.latency_ms > 0
