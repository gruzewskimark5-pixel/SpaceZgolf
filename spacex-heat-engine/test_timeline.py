import requests
import time
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("Setting up game data for timeline...")

# 1. Create a Match
match_data = {"title": "Simulation: Scrubber Data Generator", "phase": "MID"}
res = requests.post(f"{BASE_URL}/matches", json=match_data)
match_id = res.json()["id"]

# 2. Create Players
p1 = requests.post(f"{BASE_URL}/players", json={"name": "Kai Trump", "role": "ANCHOR"}).json()["id"]
p2 = requests.post(f"{BASE_URL}/players", json={"name": "Mia Baker", "role": "CONVERTER"}).json()["id"]

print("Injecting 5 events separated by time...")

for i in range(5):
    # Base novelty increasing over time
    novelty = 0.1 + (i * 0.1)

    event_data = {
        "match_id": match_id,
        "phase_multiplier": 1.0,
        "novelty_bonus": novelty,
        "players": [p1, p2]
    }
    res = requests.post(f"{BASE_URL}/events", json=event_data)
    event_id = res.json()["id"]

    eng_data = {
        "views": random.randint(50000, 150000),
        "retention": random.uniform(0.5, 0.9),
        "interactions": random.randint(5000, 20000),
        "peak_concurrent": random.randint(10000, 50000)
    }
    requests.post(f"{BASE_URL}/events/{event_id}/engagement", json=eng_data)

    res = requests.post(f"{BASE_URL}/events/{event_id}/calculate-heat")
    print(f"Event {i} Heat: {res.json()['heat_index']}")

    time.sleep(1.5)

print("Done generating timeline events.")
