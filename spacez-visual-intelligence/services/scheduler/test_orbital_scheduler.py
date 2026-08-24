import sys
from unittest.mock import MagicMock

# Mock numpy before importing orbital_scheduler
mock_np = MagicMock()
sys.modules["numpy"] = mock_np

from datetime import datetime, timezone
from orbital_scheduler import OrbitalScheduler, TwinState

def test_admit_job_boundary_energy():
    # SOC_RESERVE_WH = 0.15 * 1500 = 225.0
    soc_reserve = 0.15 * 1500

    # Exactly at reserve after job
    # projected_energy_2h_wh - required_wh * duration_h == SOC_RESERVE_WH
    # 325 - 50 * 2 = 225
    twin = {
        "node-001": TwinState("node-001", datetime.now(timezone.utc), 1200, 28.5, 850, 120, 325.0, 10.0)
    }
    scheduler = OrbitalScheduler(twin)
    job = {"energy_wh": 50, "duration_h": 2}
    assert scheduler.admit_job(job) is True

    # Slightly below reserve after job
    # 324.9 - 50 * 2 = 224.9 < 225
    twin["node-001"].projected_energy_2h_wh = 324.9
    assert scheduler.admit_job(job) is False

def test_admit_job_boundary_thermal():
    # thermal_headroom_c < 5.0 fails

    # Exactly at 5.0
    twin = {
        "node-001": TwinState("node-001", datetime.now(timezone.utc), 1200, 28.5, 850, 120, 1000.0, 5.0)
    }
    scheduler = OrbitalScheduler(twin)
    job = {"energy_wh": 50, "duration_h": 2}
    assert scheduler.admit_job(job) is True

    # Slightly below 5.0
    twin["node-001"].thermal_headroom_c = 4.9
    assert scheduler.admit_job(job) is False

def test_admit_job_defaults():
    # energy_wh defaults to 0, duration_h defaults to 2
    # projected_energy_2h_wh - 0 * 2 = 1000 > 225
    twin = {
        "node-001": TwinState("node-001", datetime.now(timezone.utc), 1200, 28.5, 850, 120, 1000.0, 10.0)
    }
    scheduler = OrbitalScheduler(twin)
    job = {}
    assert scheduler.admit_job(job) is True

    # Test only one missing
    job = {"energy_wh": 100} # duration defaults to 2. 1000 - 100*2 = 800 > 225. True.
    assert scheduler.admit_job(job) is True

def test_admit_job_multiple_nodes():
    # One node fails
    twin = {
        "node-001": TwinState("node-001", datetime.now(timezone.utc), 1200, 28.5, 850, 120, 1000.0, 10.0),
        "node-002": TwinState("node-002", datetime.now(timezone.utc), 1200, 28.5, 850, 120, 200.0, 10.0) # 200 < 225
    }
    scheduler = OrbitalScheduler(twin)
    job = {"energy_wh": 0, "duration_h": 2}
    assert scheduler.admit_job(job) is False

    # All nodes pass
    twin["node-002"].projected_energy_2h_wh = 1000.0
    assert scheduler.admit_job(job) is True
