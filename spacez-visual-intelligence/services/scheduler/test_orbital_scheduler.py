import sys
from unittest.mock import MagicMock

# Mock numpy to avoid missing dependency in restricted environments
mock_numpy = MagicMock()
mock_numpy.random.normal.return_value = 0.0
sys.modules['numpy'] = mock_numpy

import pytest
from datetime import datetime, timezone
from orbital_scheduler import OrbitalScheduler, TwinState

@pytest.fixture
def mock_twin_states():
    now = datetime.now(timezone.utc)
    return {
        "node-001": TwinState(
            node_id="node-001",
            timestamp=now,
            soc_wh=1200.0,
            thermal_c=28.5,
            solar_headroom_w=850.0,
            next_ground_window_s=120,
            projected_energy_2h_wh=1100.0,
            thermal_headroom_c=12.0
        ),
        "node-002": TwinState(
            node_id="node-002",
            timestamp=now,
            soc_wh=950.0,
            thermal_c=31.2,
            solar_headroom_w=620.0,
            next_ground_window_s=45,
            projected_energy_2h_wh=820.0,
            thermal_headroom_c=8.5
        )
    }

@pytest.fixture
def scheduler(mock_twin_states):
    return OrbitalScheduler(mock_twin_states)

def test_admit_job_success(scheduler):
    # Requirements well within limits
    job = {"energy_wh": 100, "duration_h": 2}
    assert scheduler.admit_job(job) is True

def test_admit_job_insufficient_energy(scheduler, mock_twin_states):
    # Requires 500 Wh * 2 h = 1000 Wh.
    # node-002 projected energy is 820.
    # 820 - 1000 = -180 < 225 (reserve) => Should be rejected.
    job = {"energy_wh": 500, "duration_h": 2}
    assert scheduler.admit_job(job) is False

def test_admit_job_insufficient_thermal_headroom(scheduler, mock_twin_states):
    job = {"energy_wh": 100, "duration_h": 2}
    # Reduce thermal headroom of node-001 to 4.0 (< 5.0 required)
    mock_twin_states["node-001"].thermal_headroom_c = 4.0
    assert scheduler.admit_job(job) is False

def test_place_job_success(scheduler):
    # Score for node-001: 850 * 0.6 + (3600 - 120) * 0.4 = 510 + 1392 = 1902
    # Score for node-002: 620 * 0.6 + (3600 - 45) * 0.4 = 372 + 1422 = 1794
    # Therefore node-001 is best
    job = {"energy_wh": 100, "duration_h": 2}
    placed_node = scheduler.place_job(job)
    assert placed_node == "node-001"

def test_place_job_no_candidates(scheduler, mock_twin_states):
    job = {"energy_wh": 100, "duration_h": 2}

    # Violate reserve SOC and thermal headroom for both nodes
    mock_twin_states["node-001"].soc_wh = 100.0  # < 225
    mock_twin_states["node-002"].thermal_headroom_c = 4.0  # < 5.0

    placed_node = scheduler.place_job(job)
    assert placed_node is None

def test_enforce_invariants_success(scheduler):
    assert scheduler.enforce_invariants({}) is True

def test_enforce_invariants_soc_violation(scheduler, mock_twin_states):
    mock_twin_states["node-001"].soc_wh = 100.0  # < reserve (225.0)
    assert scheduler.enforce_invariants({}) is False

def test_enforce_invariants_thermal_violation(scheduler, mock_twin_states):
    mock_twin_states["node-002"].thermal_c = 50.0  # > limit (45.0)
    assert scheduler.enforce_invariants({}) is False

def test_mock_telemetry_loop(scheduler):
    # Test that the telemetry loop executes without raising exceptions
    try:
        scheduler.mock_telemetry_loop(duration_s=60)
    except Exception as e:
        pytest.fail(f"mock_telemetry_loop raised an exception: {e}")
