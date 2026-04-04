# orbital_scheduler.py
# Operator-grade Python stubs — Phase C
# TwinState interface + scheduler core. Ready for Phase A testing.

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import numpy as np

@dataclass
class TwinState:
    node_id: str
    timestamp: datetime
    soc_wh: float                     # state-of-charge, Wh
    thermal_c: float                  # current temp, C
    solar_headroom_w: float           # W available next 2h
    next_ground_window_s: int         # seconds to next ground pass
    projected_energy_2h_wh: float     # Twin forecast
    thermal_headroom_c: float         # margin to limit

class OrbitalScheduler:
    def __init__(self, twin_states: Dict[str, TwinState]):
        self.twin_states = twin_states
        self.SOC_RESERVE_WH = 0.15 * 1500  # 15% of 1500 Wh nominal
        self.THERMAL_LIMIT_C = 45.0

    def admit_job(self, job: Dict) -> bool:
        """Job admission control against TwinState forecasts."""
        required_wh = job.get("energy_wh", 0)
        duration_h = job.get("duration_h", 2)

        for node in self.twin_states.values():
            if (node.projected_energy_2h_wh - required_wh * duration_h < self.SOC_RESERVE_WH or
                node.thermal_headroom_c < 5.0):
                return False
        return True

    def place_job(self, job: Dict) -> Optional[str]:
        """Placement: prefer high solar headroom + ground window."""
        candidates = []
        for nid, state in self.twin_states.items():
            score = (state.solar_headroom_w * 0.6 +
                     (3600 - state.next_ground_window_s) * 0.4)
            if (state.soc_wh >= self.SOC_RESERVE_WH and
                state.thermal_headroom_c >= 5.0):
                candidates.append((score, nid))

        if not candidates:
            return None
        return max(candidates, key=lambda x: x[0])[1]

    def mock_telemetry_loop(self, duration_s: int = 3600):
        """Ground-test loop: simulates real sat telemetry → TwinState updates."""
        print(f"[C] Mock telemetry loop started — {duration_s}s")
        for t in range(0, duration_s, 30):
            # In production: replace with real sat packet ingest
            for node_id, state in self.twin_states.items():
                # Kalman-fused SoC + lumped-cap thermal update (Twin already computed)
                state.soc_wh = max(0, state.soc_wh - 50 + np.random.normal(0, 10))
                state.thermal_c += np.random.normal(0, 0.2)
            print(f"[C] TwinState snapshot t={t}s — {len(self.twin_states)} nodes live")
        print("[C] Mock loop complete — ready for live telemetry handoff")

    def enforce_invariants(self, job_placement: Dict) -> bool:
        """Never schedule if SoC < reserve or thermal violation imminent."""
        for nid, state in self.twin_states.items():
            if state.soc_wh < self.SOC_RESERVE_WH or state.thermal_c >= self.THERMAL_LIMIT_C:
                print(f"[C] SAFETY VIOLATION — node {nid} rejected")
                return False
        return True

# Instantiation example (Phase A test)
if __name__ == "__main__":
    # Mock TwinState feed (replace with real B-layer API)
    twin = {
        "node-001": TwinState("node-001", datetime.now(timezone.utc), 1200, 28.5, 850, 120, 1100, 12.0),
        "node-002": TwinState("node-002", datetime.now(timezone.utc), 950, 31.2, 620, 45, 820, 8.5)
    }
    scheduler = OrbitalScheduler(twin)

    test_job = {"energy_wh": 300, "duration_h": 2, "tolerance": "high"}

    if scheduler.admit_job(test_job) and scheduler.enforce_invariants({}):
        placement = scheduler.place_job(test_job)
        print(f"[C] Job placed on → {placement}")
    scheduler.mock_telemetry_loop(180)  # 3-min ground test
