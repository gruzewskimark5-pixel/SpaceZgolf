from typing import Dict, Any
from gte_engine.models import UnifiedCognitiveEvent

class ScoringAdapter:
    def to_activity(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a Digital Glass Event (Dictionary currently representing UnifiedCognitiveEvent) into the GTE scoring format.
        """
        outcome = event.get("outcome")
        state = event.get("state")
        decision = event.get("decision")

        # Determine performance delta based on whether `outcome` is an object or dictionary
        if hasattr(outcome, 'performance_delta'):
            performance = outcome.performance_delta
        elif isinstance(outcome, dict):
            performance = outcome.get("performance_delta", 0.0)
        else:
            performance = 0.0

        if hasattr(state, 'biometrics'):
            biometrics = state.biometrics
        elif isinstance(state, dict):
            biometrics = state.get("biometrics", {})
        else:
            biometrics = {}

        if hasattr(decision, 'latency_ms'):
            decision_latency = decision.latency_ms
        elif isinstance(decision, dict):
            decision_latency = decision.get("latency_ms", 0.0)
        else:
            decision_latency = 0.0

        return {
            "user_id": event.get("entity_id"),
            "activity_type": "derived",
            "timestamp": event.get("timestamp"),
            "raw": {
                "performance": performance,
                "biometrics": biometrics,
                "decision_latency": decision_latency
            }
        }
