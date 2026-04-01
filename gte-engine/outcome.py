from typing import List, Dict, Any

class OutcomeEngine:
    """
    Computes real-time outcomes (deltas) against historical baselines.
    This replaces static outcomes with dynamic, contextual intelligence.
    """

    def compute(self, current_event: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates performance deltas by comparing current event to past N events.
        """
        if not history:
            return {
                "accuracy_delta": 0.0,
                "latency_delta": 0
            }

        # Take last N events for baseline (e.g., 10)
        recent_history = history[-10:]

        # Calculate averages for baselines
        avg_accuracy = sum(event.get("outcome", {}).get("accuracy", 0.0) for event in recent_history) / len(recent_history)
        avg_latency = sum(event.get("decision", {}).get("latency_ms", 0) for event in recent_history) / len(recent_history)

        current_accuracy = current_event.get("outcome", {}).get("accuracy", 0.0)
        current_latency = current_event.get("decision", {}).get("latency_ms", 0)

        return {
            "accuracy_delta": current_accuracy - avg_accuracy,
            "latency_delta": current_latency - avg_latency
        }
