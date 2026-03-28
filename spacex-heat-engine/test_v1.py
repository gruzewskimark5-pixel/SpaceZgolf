import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("🔥 Testing Heat Engine v1 API 🔥\n")

print("1. Fetching Top Force Events...")
res = requests.get(f"{BASE_URL}/apex/top-force-events?limit=3")
if res.status_code == 200:
    for ev in res.json():
        print(f"[{ev['cluster_pair']}] {ev['pairing']}")
        print(f"   -> Score: {ev['interaction_score']} | Spike Prob: {ev['spike_probability']} | Top Force: {ev.get('top_force_event')}")
else:
    print(f"Error: {res.text}")

print("\n2. Testing Specific Pairing (Nelly vs Alexis)...")
res = requests.post(f"{BASE_URL}/apex/predict-pairing?player_a_id=nelly_korda&player_b_id=alexis_miestowski")
if res.status_code == 200:
    data = res.json()
    print(f"[{data['cluster_pair']}] {data['pairing']}")
    print(f"   -> Score: {data['interaction_score']} | Multiplier: {data.get('multiplier')} | Validated: {data.get('validated_top_force')}")
else:
    print(f"Error: {res.text}")
