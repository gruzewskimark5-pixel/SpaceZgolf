import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from simulator import generate_random_event, generate_feedback, run_simulator

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

@patch('simulator.nats.connect', new_callable=AsyncMock)
@patch('simulator.asyncio.sleep', new_callable=AsyncMock)
def test_run_simulator(mock_sleep, mock_connect):
    # Setup mock returns for NATS and JetStream
    mock_nc = AsyncMock()
    mock_connect.return_value = mock_nc
    mock_js = AsyncMock()

    # .jetstream() is a synchronous method returning the context
    mock_nc.jetstream = MagicMock(return_value=mock_js)

    # By the time the first sleep happens, one event is published.
    # We break the infinite loop by raising an exception in sleep.
    mock_sleep.side_effect = Exception("Stop loop")

    # Run the simulator loop synchronously for testing.
    # We expect the simulator error to be caught by the generic except block inside run_simulator,
    # so we just let it run.
    asyncio.run(run_simulator())

    # Assertions to ensure expected flow occurred
    assert mock_connect.called
    assert mock_js.add_stream.call_count == 2

    # We expect 1 publish call before the first sleep happens
    assert mock_js.publish.call_count == 1

    # Let's verify that the subject was EVENT_SUBJECT
    args, kwargs = mock_js.publish.call_args
    assert args[0] == "spacez.events.detected"

    # Ensure cleanup is called
    assert mock_nc.close.called
