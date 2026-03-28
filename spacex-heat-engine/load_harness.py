import time
import concurrent.futures
from datetime import datetime, timezone
import requests

BASE_URL = "http://localhost:8000/api/v1"

def safe_post(endpoint, payload):
    res = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)
    res.raise_for_status()
    return res.json()

def ingest_event(i, player_id="kai_trump"):
    return safe_post("/digital-twin/ingest", {
        "event_id": f"stress_{player_id}_{i}",
        "player_id": player_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"format": "loadtest", "stakes": "loadtest", "hole": 1, "par": 4, "yardage": 400, "wind": "0"},
        "swing": {"club": "driver", "ball_speed": 150.0, "club_speed": 100, "launch": 10, "spin": 2500, "attack_angle": 1.0, "face_to_path": 0},
        "outcome": {"carry": 250, "total": 260, "fairway": True, "miss_pattern": "straight"}
    })

def run_load_test(events=1000, workers=20):
    print(f"Starting Load Test: {events} events across {workers} workers...")
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(ingest_event, i) for i in range(events)]
        results = []
        for f in concurrent.futures.as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                 print(f"Failed event: {e}")

    duration = time.time() - start
    success = sum(1 for r in results if r.get("event_id"))
    print(f"Events: {events}, Success: {success}, Duration: {duration:.2f}s, EPS: {events/duration:.1f}")

if __name__ == "__main__":
    run_load_test()
