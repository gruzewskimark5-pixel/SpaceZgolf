from typing import Dict, Any
from .schemas import RawTelemetryEvent, Outcome, NormalizedMetrics, BaselineContext

class OutcomeEngine:
    def __init__(self):
        # In a real system, this would hold state or connect to a DB for historical baseline context
        pass

    def calculate_baseline(self, entity_id: str, context_filter: Dict[str, str]) -> float:
        """
        Simulate calculating a baseline weighted average over past events.
        """
        # A mock baseline accuracy
        return 0.80

    def normalize_metrics(self, raw_metrics: Dict[str, float], context_filter: Dict[str, str]) -> NormalizedMetrics:
        """
        Normalize metrics based on fatigue, environment, etc.
        """
        raw_accuracy = raw_metrics.get("accuracy", 0.85)
        raw_latency = raw_metrics.get("latency_ms", 250)

        # Simple dummy normalization
        fatigue_factor = 1.05 if context_filter.get("environment") == "wind_high" else 0.95

        normalized_acc = raw_accuracy / fatigue_factor

        # Lower latency is better efficiency
        efficiency_score = (1 / raw_latency) * 1000 * normalized_acc

        return NormalizedMetrics(
            accuracy=round(normalized_acc, 3),
            efficiency_score=round(efficiency_score, 3)
        )

    def process_event(self, event: RawTelemetryEvent) -> Outcome:
        context_filter = {
            "activity": event.activity,
            "environment": event.environment
        }

        baseline_acc = self.calculate_baseline(event.entity_id, context_filter)
        normalized = self.normalize_metrics(event.raw_metrics, context_filter)

        raw_acc = event.raw_metrics.get("accuracy", 0.0)
        raw_lat = event.raw_metrics.get("latency_ms", 0.0)

        # Fake historical deltas
        delta = {
            "accuracy": round(raw_acc - baseline_acc, 3),
            "latency_ms": round(raw_lat - 250, 2)
        }

        return Outcome(
            delta=delta,
            normalized=normalized,
            confidence=0.92, # Placeholder
            baseline=BaselineContext(
                window="weighted_50",
                context="matched_conditions"
            )
        )
