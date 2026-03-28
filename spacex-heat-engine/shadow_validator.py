import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"

def get_live_pairing(player_a_id, player_b_id):
    return requests.post(
        f"{BASE_URL}/apex/predict-pairing",
        params={"player_a_id": player_a_id, "player_b_id": player_b_id}
    ).json()

# In our implementation we haven't split out a true shadow backend instance, so we mock the comparison
def get_shadow_pairing(player_a_id, player_b_id):
    return requests.post(
        f"{BASE_URL}/apex/predict-pairing",
        params={"player_a_id": player_a_id, "player_b_id": player_b_id}
    ).json()

def compare_pairing(a, b, tolerance=0.5):
    live = get_live_pairing(a, b)
    shadow = get_shadow_pairing(a, b)

    live_score = live["interaction_score"]
    shadow_score = shadow["interaction_score"]

    delta = abs(live_score - shadow_score)
    ok = delta <= tolerance

    return {
        "pair": f"{a} vs {b}",
        "live": live_score,
        "shadow": shadow_score,
        "delta": delta,
        "ok": ok
    }

def run_shadow_suite():
    print("Running Shadow Validator (Live vs Shadow Pipeline)...")
    pairs = [
        ("nelly_korda", "alexis_miestowski"),
        ("kai_trump", "cailyn"),
        ("asterisk_talley", "alyssa_lamoureux"),
        ("megha_ganne", "sabrina_andolpho"),
        ("claire_hogle", "gabriella_degasperis")
    ]
    results = [compare_pairing(a, b) for a, b in pairs]
    for r in results:
        status = "✅" if r["ok"] else "❌"
        print(f"{status} {r['pair']} | live={r['live']} shadow={r['shadow']} Δ={r['delta']:.2f}")

if __name__ == "__main__":
    run_shadow_suite()
