from __future__ import annotations

import argparse
import json
import random
import statistics

from .director import DirectorBrain
from .models import DirectorDecision, MatchResult, ShotEvent, ValidationMetrics

MAJOR_KINDS = {"heat_spike", "momentum_shift", "lead_change", "clutch", "meltdown"}


def generate_match(seed: int, match_id: str, shots: int = 72) -> MatchResult:
    rng = random.Random(seed)
    result = MatchResult(match_id=match_id)
    heat = rng.uniform(25, 55)
    momentum = rng.uniform(-20, 20)
    win_probability = 0.5

    for i in range(shots):
        hole = min(18, i // 4 + 1)
        shock = rng.random()
        kind = "routine"
        impact = rng.uniform(0.05, 0.35)

        if shock > 0.985:
            kind = "clutch"
            heat = min(100, heat + rng.uniform(25, 40))
            momentum += rng.uniform(20, 35)
            impact = rng.uniform(0.80, 1.00)
        elif shock > 0.96:
            kind = "lead_change"
            heat = min(100, heat + rng.uniform(12, 25))
            momentum += rng.uniform(-35, 35)
            impact = rng.uniform(0.75, 0.95)
        elif shock > 0.925:
            kind = "momentum_shift"
            momentum += rng.choice([-1, 1]) * rng.uniform(20, 35)
            heat = min(100, heat + rng.uniform(8, 20))
            impact = rng.uniform(0.65, 0.90)
        elif shock > 0.90:
            kind = "meltdown"
            heat = min(100, heat + rng.uniform(15, 30))
            momentum -= rng.uniform(20, 35)
            impact = rng.uniform(0.70, 0.95)
        else:
            heat = max(0, min(100, heat + rng.uniform(-4, 5)))
            momentum = max(-100, min(100, momentum + rng.uniform(-8, 8)))

        win_probability = max(
            0.01,
            min(0.99, win_probability + momentum / 2000.0 + rng.uniform(-0.015, 0.015)),
        )

        event = ShotEvent(
            event_id=f"{match_id}:shot:{i:04d}",
            match_id=match_id,
            shot_index=i,
            player_id="p1" if i % 2 == 0 else "p2",
            hole=hole,
            score_diff=round((win_probability - 0.5) * 4, 3),
            heat=round(heat, 3),
            momentum=round(momentum, 3),
            win_probability=round(win_probability, 5),
            kind=kind,
            impact=round(impact, 3),
            timestamp_ms=i * 4500,
        )
        result.events.append(event)
        if kind in MAJOR_KINDS:
            result.true_major_event_ids.add(event.event_id)

    return result


def evaluate(matches: list[MatchResult], director: DirectorBrain) -> ValidationMetrics:
    focused_ids: set[str] = set()
    prediction_hits: set[str] = set()
    prediction_attempts = 0
    lead_times: list[int] = []

    for match in matches:
        decisions: list[DirectorDecision] = []
        for i, event in enumerate(match.events):
            future = match.events[i + 1 : i + 1 + director.config.prediction_window]
            decision = director.decide(event, future)
            decisions.append(decision)
            if decision.decision == "FOCUS_NOW":
                focused_ids.add(event.event_id)
            if decision.predicted:
                prediction_attempts += 1
                target = next((e for e in future if e.event_id in match.true_major_event_ids), None)
                if target is not None:
                    prediction_hits.add(target.event_id)
                    lead_times.append(target.timestamp_ms - event.timestamp_ms)
        match.decisions = decisions

    true_set = {eid for m in matches for eid in m.true_major_event_ids}
    focus_hits = len(focused_ids & true_set)
    focus_precision = focus_hits / len(focused_ids) if focused_ids else 0.0
    focus_recall = focus_hits / len(true_set) if true_set else 0.0
    false_focus = 1.0 - focus_precision if focused_ids else 0.0

    predictive_precision = len(prediction_hits) / prediction_attempts if prediction_attempts else 0.0
    predictive_recall = len(prediction_hits) / len(true_set) if true_set else 0.0

    all_ids = [e.event_id for m in matches for e in m.events]
    ordered = all(
        all(a.shot_index < b.shot_index for a, b in zip(m.events, m.events[1:]))
        for m in matches
    )
    integrity = 1.0 if len(all_ids) == len(set(all_ids)) and ordered else 0.0

    return ValidationMetrics(
        precision_at_k=focus_precision,
        recall_at_k=focus_recall,
        predictive_precision=predictive_precision,
        predictive_recall=predictive_recall,
        mean_lead_time_ms=statistics.mean(lead_times) if lead_times else 0.0,
        false_focus_rate=false_focus,
        event_integrity=integrity,
        replay_recall=focus_recall,
    )


def run(seed: int, matches: int, shots: int) -> dict:
    scenarios = [generate_match(seed + i, f"sim-{i:05d}", shots) for i in range(matches)]
    metrics = evaluate(scenarios, DirectorBrain())
    return {
        "seed": seed,
        "matches": matches,
        "shots_per_match": shots,
        "events": matches * shots,
        "metrics": metrics.as_dict(),
        "major_events": sum(len(m.true_major_event_ids) for m in scenarios),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SpaceZ Director Brain validation harness")
    parser.add_argument("--seed", type=int, default=20260814)
    parser.add_argument("--matches", type=int, default=1000)
    parser.add_argument("--shots", type=int, default=72)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.matches, args.shots), indent=2))
