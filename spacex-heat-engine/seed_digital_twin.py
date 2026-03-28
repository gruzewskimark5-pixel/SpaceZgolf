import requests
import time
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

def seed_claire_twin():
    now = datetime.now(timezone.utc)

    swings = [
        {
            "event_id": "claire_seed_1",
            "timestamp": (now - timedelta(days=3)).isoformat(),
            "context": {"format": "match", "stakes": "league", "hole": 1, "par": 4, "yardage": 400, "wind": "0L"},
            "swing": {"club": "driver", "ball_speed": 158.0, "club_speed": 108.0, "launch": 12.0, "spin": 2500, "attack_angle": 3.0, "face_to_path": 0.0},
            "outcome": {"carry": 255, "total": 270, "fairway": True, "miss_pattern": "straight"}
        },
        {
            "event_id": "claire_seed_2",
            "timestamp": (now - timedelta(days=2)).isoformat(),
            "context": {"format": "match", "stakes": "league", "hole": 9, "par": 3, "yardage": 160, "wind": "5R"},
            "swing": {"club": "7i", "ball_speed": 112.0, "club_speed": 85.0, "launch": 18.0, "spin": 6000, "attack_angle": -4.0, "face_to_path": 1.0},
            "outcome": {"carry": 148, "total": 150, "fairway": True, "miss_pattern": "slight fade"}
        },
        {
            "event_id": "claire_seed_3",
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "context": {"format": "content_day", "stakes": "practice", "hole": 18, "par": 5, "yardage": 520, "wind": "10L"},
            "swing": {"club": "driver", "ball_speed": 161.0, "club_speed": 110.0, "launch": 11.5, "spin": 2300, "attack_angle": 4.0, "face_to_path": -2.0},
            "outcome": {"carry": 262, "total": 280, "fairway": False, "miss_pattern": "pull"}
        }
    ]

    print("Seeding Claire Hogle Digital Twin...")

    for s in swings:
        payload = {
            "event_id": s["event_id"],
            "player_id": "claire_hogle",
            "timestamp": s["timestamp"],
            "context": s["context"],
            "swing": s["swing"],
            "outcome": s["outcome"]
        }
        res = requests.post(f"{BASE_URL}/digital-twin/ingest", json=payload)
        if res.status_code == 200:
            print(f"✅ Ingested {s['event_id']}")
        else:
            print(f"❌ Failed {s['event_id']}: {res.text}")

    print("Done seeding.")

if __name__ == "__main__":
    seed_claire_twin()
