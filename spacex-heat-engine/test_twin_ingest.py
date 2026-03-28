import requests
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Ingest into Mark OS Node
print("1. Ingesting into Mark OS Node...")
node_event = {
    "node_id": "driver_panther_national",
    "owner": "kai_trump",
    "timestamp": datetime.utcnow().isoformat(),
    "context": {"session_id": "sim_001", "course": "panther", "wind": "5L"},
    "swing": {"club": "driver", "ball_speed": 165.2, "club_speed": 105.1, "launch": 12.1, "spin": 2500, "attack_angle": 3.8, "face_to_path": 0.4},
    "outcome": {"carry": 272, "total": 288, "target_line_offset": 5, "result": "fairway"}
}
res = requests.post(f"{BASE_URL}/markos/ingest-node-event", json=node_event)
print(res.json())

# Ingest into Digital Twin
print("\n2. Ingesting into Digital Twin...")
twin_event = {
    "event_id": "kt_1",
    "player_id": "kai_trump",
    "timestamp": datetime.utcnow().isoformat(),
    "context": {"format": "stroke", "stakes": "league", "hole": 1, "par": 4, "yardage": 410, "wind": "10L"},
    "swing": {"club": "driver", "ball_speed": 168.5, "club_speed": 108.2, "launch": 11.5, "spin": 2300, "attack_angle": 4.1, "face_to_path": -0.5},
    "outcome": {"carry": 285, "total": 301, "fairway": True, "miss_pattern": "draw"}
}
res = requests.post(f"{BASE_URL}/digital-twin/ingest", json=twin_event)
print(res.json())

print("\n3. Fetching Player Twin State...")
res = requests.get(f"{BASE_URL}/digital-twin/player/kai_trump")
data = res.json()
print(f"Heat: {data['state']['current_heat']} | Avg Ball Speed: {data['state']['avg_ball_speed']} | Fairway %: {data['state']['fairway_percentage']}")
