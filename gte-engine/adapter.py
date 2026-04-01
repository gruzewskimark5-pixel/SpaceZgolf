from typing import Dict, Any

class ScoringAdapter:
    """
    Translates cognitive events (Digital Glass) into GTE input payloads.
    Ensures that GTE and Digital Glass remain decoupled, maintaining a single source of truth.
    """

    def to_activity(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps the nested unified event structure to the flat activity payload expected by GTE.
        """
        return {
            "user_id": event.get("entity_id"),
            "activity_type": "derived",
            "timestamp": event.get("timestamp"),
            "raw": {
                "performance": event.get("outcome", {}).get("performance_delta", 0.0),
                "biometrics": event.get("state", {}).get("biometrics", {}),
                "decision_latency": event.get("decision", {}).get("latency_ms", 0)
            },
            # Map parameters for GTE's calculating functions:
            "hr_avg": event.get("state", {}).get("biometrics", {}).get("hr_avg", 0),
            "distance_km": event.get("outcome", {}).get("distance_km", 0.0), # Example mapping for Base Output
            "metrics": {
                 "pace_today": event.get("outcome", {}).get("pace_today", 0.0),
                 "hr_today": event.get("state", {}).get("biometrics", {}).get("hr_avg", 0),
                 "duration_today": event.get("outcome", {}).get("duration_today", 0.0)
            },
            "context": event.get("state", {}).get("environment", {})
        }
