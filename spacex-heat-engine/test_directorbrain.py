import requests
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"

def safe_get(endpoint, params=None):
    res = requests.get(f"{BASE_URL}{endpoint}", params=params or {}, timeout=5)
    res.raise_for_status()
    return res.json()

def test_director_returns_enough_matches():
    data = safe_get("/apex/top-force-events", params={"limit": 10})
    assert isinstance(data, list), "Director should return a list"
    assert len(data) >= 5, "Director returning too few matches"
    print("✅ test_director_returns_enough_matches passed")

def test_director_respects_heat_ordering():
    data = safe_get("/apex/top-force-events", params={"limit": 10})
    scores = [m["interaction_score"] for m in data]
    assert scores == sorted(scores, reverse=True), "Matches not sorted by interaction_score desc"
    print("✅ test_director_respects_heat_ordering passed")

def test_director_includes_key_force_events():
    data = safe_get("/apex/top-force-events", params={"limit": 20})
    # Update script to respect the new key names required by the previous step: 'a_id' instead of 'player_a_id'
    pairs = {f"{m['a_id']}|{m['b_id']}" for m in data}

    assert "nelly_korda|alexis_miestowski" in pairs or "alexis_miestowski|nelly_korda" in pairs, \
        "Nelly vs Alexis Force Event missing from Director recommendations"
    print("✅ test_director_includes_key_force_events passed")

if __name__ == "__main__":
    print("Testing Director Brain & Top Force Events...")
    test_director_returns_enough_matches()
    test_director_respects_heat_ordering()
    test_director_includes_key_force_events()
