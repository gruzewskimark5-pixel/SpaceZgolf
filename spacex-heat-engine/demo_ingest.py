import requests
import time
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000/api/v1"

swings = [
    {"carry": 260, "total": 275, "fairway": True, "miss": "straight", "speed": 162.0},
    {"carry": 265, "total": 280, "fairway": True, "miss": "straight", "speed": 163.5},
    {"carry": 210, "total": 220, "fairway": False, "miss": "hook", "speed": 160.1},
    {"carry": 285, "total": 305, "fairway": True, "miss": "slight draw", "speed": 168.9},
]

print("Starting Mark OS -> Digital Twin Demo Ingestion...\n")

for i, s in enumerate(swings):
    print(f"[{i+1}/4] Kai Trump hits a {s['speed']}mph drive. Carry: {s['carry']} yards. Fairway: {s['fairway']}")

    twin_event = {
        "event_id": f"demo_kt_{i}",
        "player_id": "kai_trump",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"format": "stroke", "stakes": "practice", "hole": i+1, "par": 4, "yardage": 400, "wind": "5L"},
        "swing": {"club": "driver", "ball_speed": s["speed"], "club_speed": round(s["speed"]/1.45, 1), "launch": 11.0, "spin": 2400, "attack_angle": 3.0, "face_to_path": 0.0},
        "outcome": {"carry": s["carry"], "total": s["total"], "fairway": s["fairway"], "miss_pattern": s["miss"]}
    }

    try:
        res = requests.post(f"{BASE_URL}/digital-twin/ingest", json=twin_event)
        res.raise_for_status()
        state = requests.get(f"{BASE_URL}/digital-twin/player/kai_trump").json()
        print(f"  -> Momentum: {state['state']['momentum']} | Trend: {state['state']['trend_direction']}")
    except Exception as e:
        print(f"  -> Error: {e}")

    time.sleep(2)

print("\nIngestion Complete.")
