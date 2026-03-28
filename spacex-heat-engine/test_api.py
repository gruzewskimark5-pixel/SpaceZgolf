import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_response(label, res):
    print(f"\n--- {label} ---")
    print(f"Status: {res.status_code}")
    if res.status_code < 300:
        print(json.dumps(res.json(), indent=2))
    else:
        print(res.text)

print("Wait for server to start...")
time.sleep(2)

# 1. Create a Match
match_data = {"title": "The Creators Cup - Final Round", "phase": "LATE"}
res = requests.post(f"{BASE_URL}/matches", json=match_data)
print_response("Create Match", res)
match_id = res.json()["id"]

# 2. Create Players
p1 = requests.post(f"{BASE_URL}/players", json={"name": "Kai Trump", "role": "ANCHOR"}).json()["id"]
p2 = requests.post(f"{BASE_URL}/players", json={"name": "Mia Baker", "role": "CONVERTER"}).json()["id"]

# 3. Create an Event (Moment)
event_data = {
    "match_id": match_id,
    "phase_multiplier": 1.5, # LATE phase multiplier
    "novelty_bonus": 0.2, # Good shot out of rough
    "players": [p1, p2]
}
res = requests.post(f"{BASE_URL}/events", json=event_data)
print_response("Create Event", res)
event_id = res.json()["id"]

# 4. Add Engagement
eng_data = {
    "views": 150000,
    "retention": 0.85,
    "interactions": 12000,
    "peak_concurrent": 45000
}
res = requests.post(f"{BASE_URL}/events/{event_id}/engagement", json=eng_data)
print_response("Add Engagement", res)

# 5. Calculate Heat Index
res = requests.post(f"{BASE_URL}/events/{event_id}/calculate-heat")
print_response("Calculate Heat", res)

# 6. Add Revenue (Sponsor interaction during moment)
res = requests.post(f"{BASE_URL}/events/{event_id}/revenue", json={"revenue": 5000.0, "source": "TaylorMade App Install"})
print_response("Add Revenue", res)

# 7. Calculate CES
res = requests.post(f"{BASE_URL}/events/{event_id}/calculate-ces")
print_response("Calculate CES", res)
