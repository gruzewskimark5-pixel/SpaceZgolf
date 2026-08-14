from __future__ import annotations

from dataclasses import dataclass

from .models import DirectorDecision, ShotEvent


@dataclass(frozen=True)
class DirectorConfig:
    """Deterministic Director policy used by the validation harness.

    The validation loop deliberately keeps policy separate from event generation
    so the same corpus can be replayed while thresholds/weights are tuned.
    """

    heat_weight: float = 0.34
    momentum_weight: float = 0.18
    impact_weight: float = 0.34
    comeback_weight: float = 0.14
    major_threshold: float = 0.84
    prediction_threshold: float = 0.80
    prediction_margin: float = 0.04
    prediction_window: int = 4


class DirectorBrain:
    """Pure deterministic decision function for offline validation."""

    def __init__(self, config: DirectorConfig | None = None) -> None:
        self.config = config or DirectorConfig()

    def priority(self, event: ShotEvent) -> float:
        # Distance from a neutral win state measures competitive tension without
        # rewarding a merely large absolute win probability.
        comeback = min(1.0, abs(event.win_probability - 0.5) * 2.0)
        score = (
            event.heat / 100.0 * self.config.heat_weight
            + abs(event.momentum) / 100.0 * self.config.momentum_weight
            + event.impact * self.config.impact_weight
            + comeback * self.config.comeback_weight
        )
        return max(0.0, min(1.0, score))

    def decide(
        self,
        event: ShotEvent,
        future_events: list[ShotEvent] | None = None,
    ) -> DirectorDecision:
        future_events = future_events or []
        current = self.priority(event)
        future_best = max((self.priority(e) for e in future_events), default=0.0)

        predicted = (
            future_best >= self.config.prediction_threshold
            and future_best > current + self.config.prediction_margin
        )

        if predicted:
            decision = "PREPARE_FOCUS"
            reason = "future_priority_spike"
        elif current >= self.config.major_threshold:
            decision = "FOCUS_NOW"
            reason = "current_priority_threshold"
        else:
            decision = "MONITOR"
            reason = "below_focus_threshold"

        return DirectorDecision(
            event_id=event.event_id,
            match_id=event.match_id,
            priority=current,
            predicted=predicted,
            decision=decision,
            reason=reason,
        )
