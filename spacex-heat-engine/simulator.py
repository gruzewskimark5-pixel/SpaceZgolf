import requests
import time
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("🔥 Initializing SpaceZ Golf Simulation Harness 🔥")

def create_match():
    res = requests.post(f"{BASE_URL}/matches", json={"title": "SpaceZ Masters - Final Group", "phase": "MID"})
    match_id = res.json()["id"]
    print(f"Match created: {match_id}")
    return match_id

def create_players():
    players = [
        {"name": "Kai Trump", "role": "ANCHOR"},
        {"name": "Sabrina Andolpho", "role": "ANCHOR"},
        {"name": "Alyssa Lamoureux", "role": "DISRUPTOR"},
        {"name": "Mia Baker", "role": "CONVERTER"},
        {"name": "Nelly Korda", "role": "PRESTIGE"},
        {"name": "Claire Hogle", "role": "AMPLIFIER"}
    ]
    p_ids = {}
    for p in players:
        res = requests.post(f"{BASE_URL}/players", json=p)
        p_ids[p["name"]] = res.json()["id"]
    print("Players initialized")
    return p_ids

match_id = create_match()
p_ids = create_players()

def generate_event(novelty_bonus=0.0, players=[], is_chaos=False, is_revenue=False):
    # Determine base engagement levels based on who is playing
    base_views = 30000
    base_retention = 0.5

    if "Kai Trump" in players or "Sabrina Andolpho" in players:
        base_views += 50000
        base_retention += 0.2

    if "Nelly Korda" in players:
        base_views += 70000

    if is_chaos:
        # Chaos brings a huge spike in views but erratic retention
        base_views += 100000
        base_retention -= 0.15
        novelty_bonus += 0.5

    # Introduce random noise
    views = int(base_views * random.uniform(0.8, 1.2))
    retention = min(base_retention * random.uniform(0.9, 1.1), 1.0)
    interactions = int(views * random.uniform(0.05, 0.2))
    peak_concurrent = int(views * random.uniform(0.3, 0.6))

    # 1. Create Event
    p_uuid_list = [p_ids[name] for name in players]
    event_data = {
        "match_id": match_id,
        "phase_multiplier": 1.2,
        "novelty_bonus": novelty_bonus,
        "players": p_uuid_list
    }
    res = requests.post(f"{BASE_URL}/events", json=event_data)
    event_id = res.json()["id"]

    # 2. Add Engagement
    eng_data = {
        "views": views,
        "retention": retention,
        "interactions": interactions,
        "peak_concurrent": peak_concurrent
    }
    requests.post(f"{BASE_URL}/events/{event_id}/engagement", json=eng_data)

    # 3. Calculate Heat & trigger broadcast + Director rules
    res = requests.post(f"{BASE_URL}/events/{event_id}/calculate-heat")
    heat_data = res.json()

    print(f"\n[{players}] Heat: {heat_data.get('heat_index')} | Projected: {heat_data.get('projected_heat_30s')}")
    if heat_data.get("director_decisions"):
        for dec in heat_data["director_decisions"]:
            print(f"  ⚡ {dec['policy']} Triggered")

    # 4. Optional: Revenue Event
    if is_revenue or "Mia Baker" in players:
        revenue = random.randint(1000, 10000)
        if "Mia Baker" in players: revenue *= 2
        requests.post(f"{BASE_URL}/events/{event_id}/revenue", json={"revenue": revenue, "source": "Affiliate Link Click"})
        requests.post(f"{BASE_URL}/events/{event_id}/calculate-ces")

# -- RUN THE SIMULATION SCENARIO --
print("\n▶️ Starting Match Simulation (Press Ctrl+C to stop)")

scenarios = [
    # Warmup
    {"players": ["Claire Hogle", "Alyssa Lamoureux"], "novelty": 0.1},
    {"players": ["Claire Hogle", "Alyssa Lamoureux"], "novelty": 0.1},
    # Anchor step up
    {"players": ["Kai Trump"], "novelty": 0.2},
    {"players": ["Kai Trump"], "novelty": 0.3},
    # Rivalry interaction (heat spike)
    {"players": ["Kai Trump", "Sabrina Andolpho"], "novelty": 0.4},
    {"players": ["Kai Trump", "Sabrina Andolpho"], "novelty": 0.5},
    # Chaos / Unexpected Drop
    {"players": ["Alyssa Lamoureux"], "novelty": 0.1, "chaos": True},
    # Fatigue Drop
    {"players": ["Alyssa Lamoureux"], "novelty": 0.0},
    {"players": ["Alyssa Lamoureux"], "novelty": 0.0},
    # Converter moment
    {"players": ["Mia Baker"], "novelty": 0.2, "revenue": True},
    # Prestige Gatekeep test
    {"players": ["Claire Hogle"], "novelty": 0.0},
]

try:
    for step, s in enumerate(scenarios):
        time.sleep(2.5) # Time between events
        generate_event(
            players=s.get("players"),
            novelty_bonus=s.get("novelty", 0.0),
            is_chaos=s.get("chaos", False),
            is_revenue=s.get("revenue", False)
        )

    print("\n✅ Simulation Complete.")

except KeyboardInterrupt:
    print("\n🛑 Simulation Stopped.")
