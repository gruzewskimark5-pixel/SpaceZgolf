from __future__ import annotations

from dataclasses import dataclass

from .models import DirectorDecision, ShotEvent


@dataclass(frozen=True)
class DirectorConfig:
    heat_weight: float = 0.25
    momentum_weight: float = 0.14
    impact_weight: float = 0.28
    comeback_weight: float = 0.10
    trajectory_weight: float = 0.13
    transition_weight: float = 0.10
    major_threshold: float = 0.72
    prediction_threshold: float = 0.70
    prediction_margin: float = 0.02
    prediction_window: int = 5


class DirectorBrain:
    """Deterministic, temporal Director policy for offline validation."""

    def __init__(self, config: DirectorConfig | None = None) -> None:
        self.config = config or DirectorConfig()

    @staticmethod
    def _normalized_momentum(event: ShotEvent) -> float:
        return min(1.0, abs(event.momentum) / 100.0)

    def priority(
        self,
        event: ShotEvent,
        previous_events: list[ShotEvent] | None = None,
    ) -> float:
        previous_events = previous_events or []
        recent = previous_events[-3:]
        previous_momentum = recent[-1].momentum if recent else event.momentum
        previous_heat = recent[-1].heat if recent else event.heat

        momentum_accel = max(-1.0, min(1.0, (event.momentum - previous_momentum) / 50.0))
        heat_accel = max(-1.0, min(1.0, (event.heat - previous_heat) / 25.0))
        trajectory = max(0.0, 0.6 * momentum_accel + 0.4 * heat_accel)

        transition = min(1.0, abs(event.score_diff) / 2.0)
        comeback = min(1.0, abs(event.win_probability - 0.5) * 2.0)

        score = (
            event.heat / 100.0 * self.config.heat_weight
            + self._normalized_momentum(event) * self.config.momentum_weight
            + event.impact * self.config.impact_weight
            + comeback * self.config.comeback_weight
            + trajectory * self.config.trajectory_weight
            + transition * self.config.transition_weight
        )
        return max(0.0, min(1.0, score))

    def decide(
        self,
        event: ShotEvent,
        previous_events: list[ShotEvent] | None = None,
        future_events: list[ShotEvent] | None = None,
    ) -> DirectorDecision:
        previous_events = previous_events or []
        future_events = future_events or []
        current = self.priority(event, previous_events)
        future_best = max(
            (self.priority(e, previous_events + [event]) for e in future_events),
            default=0.0,
        )
        predicted = future_best >= self.config.prediction_threshold and future_best > current + self.config.prediction_margin

        if predicted:
            decision = "PREPARE_FOCUS"
            reason = "trajectory_priority_spike"
        elif current >= self.config.major_threshold:
            decision = "FOCUS_NOW"
            reason = "trajectory_aware_threshold"
        else:
            decision = "MONITOR"
            reason = "below_trajectory_threshold"

        return DirectorDecision(
            event_id=event.event_id,
            match_id=event.match_id,
            priority=current,
            predicted=predicted,
            decision=decision,
            reason=reason,
        )
