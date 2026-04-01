from typing import Dict, Any, List

class OutcomeEngine:
    def _compute_baseline(self, history: List[Dict[str, Any]], key: str, default: float = 0.0) -> float:
        if not history:
            return default
        values = [event.get(key, default) for event in history]
        return sum(values) / len(values)

    def compute(self, current_event: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes outcomes dynamically based on historical baselines.
        Currently implements a simple moving average baseline.
        """
        # Consider only the last 10 events for the baseline
        recent_history = history[-10:] if history else []

        # Current event values
        current_accuracy = current_event.get("accuracy", 0.0)
        current_latency = current_event.get("latency", 0.0)

        # Baselines
        baseline_accuracy = self._compute_baseline(recent_history, "accuracy", default=current_accuracy)
        baseline_latency = self._compute_baseline(recent_history, "latency", default=current_latency)

        # Compute deltas
        accuracy_delta = current_accuracy - baseline_accuracy
        latency_delta = current_latency - baseline_latency

        return {
            "accuracy_delta": accuracy_delta,
            "latency_delta": latency_delta,
            "baseline_accuracy": baseline_accuracy,
            "baseline_latency": baseline_latency
        }
