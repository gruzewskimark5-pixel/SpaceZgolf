import uuid
import hashlib
from typing import Dict, Any

class EventNormalizer:
    def __init__(self):
        self.required_fields = ["event_id", "timestamp", "athlete_id"]

    def _hash_id(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(value, max_val))

    def normalize(self, raw_event: Dict[str, Any], role: str) -> Dict[str, Any]:
        """
        Normalizes a raw event from the DI pipeline into a strict Digital Glass event.
        Enforces schema, normalizes units, applies privacy rules.
        """

        # 1. Enforce Required Fields
        for field in self.required_fields:
            if field not in raw_event:
                raise ValueError(f"Missing required field: {field}")

        # 2. Assign Privacy Mode based on role
        if role == "internal":
            privacy_mode = "internal"
        elif role in ["coach", "investor"]:
            privacy_mode = "pii_redacted"
        else:
            privacy_mode = "public"

        # 3. Build Context
        context = raw_event.get("context", {})
        normalized_context = {
            "hole_id": context.get("hole_id", "unknown"),
            "weather": {
                "wind_speed": self._clamp(context.get("weather", {}).get("wind_speed", 0), 0, 100),
                "wind_direction": self._clamp(context.get("weather", {}).get("wind_direction", 0), 0, 360),
                "temperature": self._clamp(context.get("weather", {}).get("temperature", 70), -50, 130)
            },
            "lie": context.get("lie", "unknown"),
            "distance_to_pin": self._clamp(context.get("distance_to_pin", 0), 0, 800)
        }

        # 4. Build Telemetry (Normalize units/ranges)
        telemetry = raw_event.get("telemetry", {})
        normalized_telemetry = {
            "hrv": self._clamp(telemetry.get("hrv", 60), 30, 200),
            "focus_index": self._clamp(telemetry.get("focus_index", 50), 0, 100),
            "stress_index": self._clamp(telemetry.get("stress_index", 50), 0, 100),
            "swing_speed": self._clamp(telemetry.get("swing_speed", 100), 0, 160),
            "club_face_angle": self._clamp(telemetry.get("club_face_angle", 0), -45, 45)
        }

        # 5. Build Decision
        decision = raw_event.get("decision", {})
        normalized_decision = {
            "decision_id": decision.get("decision_id", str(uuid.uuid4())),
            "club_selected": decision.get("club_selected", "unknown"),
            "target_line": self._clamp(decision.get("target_line", 0), -180, 180),
            "confidence_score": self._clamp(decision.get("confidence_score", 0), 0, 100),
            "execution_complexity": self._clamp(decision.get("execution_complexity", 0), 0, 100)
        }

        # 6. Build Trace
        trace = raw_event.get("trace", [])
        normalized_trace = []
        for t in trace:
             normalized_trace.append({
                 "input_variable": t.get("input_variable", "unknown"),
                 "threshold": float(t.get("threshold", 0.0)),
                 "actual": float(t.get("actual", 0.0)),
                 "passed": bool(t.get("passed", False))
             })

        # 7. Build Outcome
        outcome = raw_event.get("outcome", {})
        normalized_outcome = {
            "carry_distance": self._clamp(outcome.get("carry_distance", 0), 0, 400),
            "fairway_hit": bool(outcome.get("fairway_hit", False)),
            "proximity_to_hole": self._clamp(outcome.get("proximity_to_hole", 0), 0, 1000),
            "strokes_gained": float(outcome.get("strokes_gained", 0.0))
        }

        # 8. Assemble Normalized Event
        glass_event = {
            "event_id": str(raw_event["event_id"]),
            "timestamp": str(raw_event["timestamp"]),
            "privacy_mode": privacy_mode,
            "athlete_id": str(raw_event["athlete_id"]),
            "context": normalized_context,
            "telemetry": normalized_telemetry,
            "decision": normalized_decision,
            "trace": normalized_trace,
            "outcome": normalized_outcome
        }

        # 9. Apply Privacy Rules
        if privacy_mode == "pii_redacted":
            glass_event["athlete_id"] = self._hash_id(glass_event["athlete_id"])
            # Redact highly sensitive bio-data if needed for certain tiers
            glass_event["telemetry"]["hrv"] = -1 # Redacted

        return glass_event
