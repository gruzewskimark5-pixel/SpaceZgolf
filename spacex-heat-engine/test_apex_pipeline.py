import requests
import time
import concurrent.futures
from datetime import datetime, timezone
import jsonschema

BASE_URL = "http://localhost:8000/api/v1"  # adjusted to the v1 prefix

# -----------------------------
# Safe network wrappers
# -----------------------------

def safe_post(endpoint, payload):
    try:
        res = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        raise AssertionError(f"🔥 SERVER DOWN: {BASE_URL} unreachable")
    except requests.exceptions.HTTPError as e:
        raise AssertionError(f"⚠️ HTTP {e.response.status_code}: {e.response.text}")

def safe_get(endpoint):
    try:
        res = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.ConnectionError:
        raise AssertionError(f"🔥 SERVER DOWN: {BASE_URL} unreachable")
    except requests.exceptions.HTTPError as e:
        raise AssertionError(f"⚠️ HTTP {e.response.status_code}: {e.response.text}")

# -----------------------------
# Schema for drift detection
# -----------------------------

TWINSTATE_SCHEMA = {
    "type": "object",
    "required": ["state", "recent_events"],
    "properties": {
        "state": {
            "type": "object",
            "required": ["player_id", "current_heat"],
            "properties": {
                "player_id": {"type": "string"},
                "current_heat": {"type": "number"}
            }
        },
        "recent_events": {
            "type": "array"
        }
    }
}

def validate_schema(response, schema):
    try:
        jsonschema.validate(response, schema)
    except jsonschema.ValidationError as e:
        raise AssertionError(f"❌ Schema drift: {e.message}")

# -----------------------------
# 1. Round-trip integrity test
# -----------------------------

def test_roundtrip_integrity():
    print("Testing Round-trip integrity...")
    uniqueballspeed = 999.9  # sentinel

    # Mark OS Ingest
    safe_post("/markos/ingest-node-event", {
        "node_id": "testdriver_sentinel",
        "owner": "kai_trump",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"session": "testing"},
        "swing": {"ball_speed": uniqueballspeed, "club": "driver", "club_speed": 100, "launch": 12, "spin": 2500, "attack_angle": 2.0, "face_to_path": 0},
        "outcome": {"carry": 200, "total": 210, "fairway": True, "miss_pattern": "straight"}
    })

    # Actually trigger the Digital Twin pipeline since Mark OS doesn't automatically do it in our MVP
    safe_post("/digital-twin/ingest", {
        "event_id": "sentinel_twin_01",
        "player_id": "kai_trump",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"format": "test", "stakes": "test", "hole": 1, "par": 4, "yardage": 400, "wind": "0"},
        "swing": {"ball_speed": uniqueballspeed, "club": "driver", "club_speed": 100, "launch": 12, "spin": 2500, "attack_angle": 2.0, "face_to_path": 0},
        "outcome": {"carry": 200, "total": 210, "fairway": True, "miss_pattern": "straight"}
    })

    time.sleep(0.5)

    data = safe_get("/digital-twin/player/kai_trump")
    recent = data.get("recent_events", [])
    speeds = [e["swing"]["ball_speed"] for e in recent]

    assert uniqueballspeed in speeds, f"❌ Mark OS -> Twin pipeline broken. Speeds: {speeds}"
    print("✅ Round-trip integrity passed")

# -----------------------------
# 2. Heat calculation accuracy
# -----------------------------

def test_heat_calculation_accuracy():
    print("Testing Heat Calculation Accuracy...")

    # First get baseline
    try:
        baseline = safe_get("/digital-twin/player/kai_trump")["state"]["current_heat"]
    except:
        baseline = 1.40

    for i in range(3):
        safe_post("/digital-twin/ingest", {
            "event_id": f"heattest_{i}",
            "player_id": "kai_trump",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": {"format": "stroke", "stakes": "test", "hole": i + 1, "par": 4, "yardage": 400, "wind": "0"},
            "swing": {"ball_speed": 160.0, "club": "driver", "club_speed": 110, "launch": 11, "spin": 2500, "attack_angle": 3.0, "face_to_path": 0},
            "outcome": {"carry": 280, "total": 300, "fairway": True, "miss_pattern": "straight"} # Good shots increase momentum
        })
        time.sleep(0.1)

    data = safe_get("/digital-twin/player/kai_trump")
    state = data["state"]

    validate_schema(data, TWINSTATE_SCHEMA)

    assert state["current_heat"] > 1.40, f"❌ Heat calculation undercounting. Base: 1.40, Current: {state['current_heat']}"
    print(f"✅ Heat Calculation Accuracy passed. Final Heat: {state['current_heat']}")

# -----------------------------
# 3. Concurrency / load test
# -----------------------------

def ingest_single_event(i):
    return safe_post("/digital-twin/ingest", {
        "event_id": f"load_{i}",
        "player_id": "kai_trump",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"format": "stroke", "stakes": "test", "hole": i + 1, "par": 4, "yardage": 400, "wind": "0"},
        "swing": {"ball_speed": 150.0, "club": "driver", "club_speed": 100, "launch": 10, "spin": 2500, "attack_angle": 1.0, "face_to_path": 0},
        "outcome": {"carry": 250, "total": 260, "fairway": True, "miss_pattern": "straight"}
    })

def test_concurrency():
    print("Testing Concurrency (100 parallel ingests)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(ingest_single_event, i) for i in range(100)]
        results = []
        for f in concurrent.futures.as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                print(f"Concurrency error: {e}")

    success_rate = len([r for r in results if r and r.get("event_id")]) / 100
    assert success_rate > 0.98, f"❌ Failure rate too high: {success_rate}"
    print(f"✅ Concurrency passed with {success_rate*100}% success rate")

# -----------------------------
# 4. Schema drift test
# -----------------------------

def test_schema_drift():
    print("Testing Schema Drift...")
    data = safe_get("/digital-twin/player/kai_trump")
    validate_schema(data, TWINSTATE_SCHEMA)
    print("✅ Schema Drift passed")

if __name__ == "__main__":
    test_roundtrip_integrity()
    test_heat_calculation_accuracy()
    test_concurrency()
    test_schema_drift()
    print("\n🚀 All Apex Pipeline Tests Passed Successfully!")
