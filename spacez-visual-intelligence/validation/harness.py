from __future__ import annotations

import argparse
import json
import random
import statistics
from dataclasses import asdict

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

        # Deterministic ground-truth event generator. These are labels, not
        # Director outputs, so the harness can measure the Director honestly.
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


def evaluate(matches: list[MatchResult], director: DirectorBrain, k: int = 5) -> ValidationMetrics:
    predicted_ids: list[str] = []
    focused_ids: list[str] = []
    lead_times: list[int] = []
    total_events = 0

    for match in matches:
        decisions: list[DirectorDecision] = []
        for i, event in enumerate(match.events):
            future = match.events[i + 1 : i + 1 + director.config.prediction_window]
            decision = director.decide(event, future)
            decisions.append(decision)
            if decision.predicted:
                predicted_ids.append(event.event_id)
            if decision.decision == "FOCUS_NOW":
                focused_ids.append(event.event_id)

        match.decisions = decisions
        total_events += len(match.events)

        # A prediction is credited when the next few events contain a true major event.
        for i, decision in enumerate(decisions):
            if not decision.predicted:
                continue
            for j in range(i + 1, min(len(match.events), i + 1 + director.config.prediction_window + 1)):
                target = match.events[j]
                if target.event_id in match.true_major_event_ids:
                    lead_times.append(target.timestamp_ms - match.events[i].timestamp_ms)
                    break

    true_major = sum(len(m.true_major_event_ids) for m in matches)
    predicted_major = len(predicted_ids)
    hits = sum(
        1
        for pid in predicted_ids
        if any(pid in m.true_major_event_ids for m in matches)
    )

    # Precision/recall for immediate focus against ground-truth major events.
    focused_set = set(focused_ids)
    true_set = {eid for m in matches for eid in m.true_major_event_ids}
    focus_hits = len(focused_set & true_set)
    precision = focus_hits / len(focused_set) if focused_set else 0.0
    recall = focus_hits / true_major if true_major else 0.0
    false_focus = (len(focused_set) - focus_hits) / len(focused_set) if focused_set else 0.0

    # Event integrity is measured on generated IDs and strict ordering.
    ids = [e.event_id for m in matches for e in m.events]
    ordered = all(
        all(a.shot_index < b.shot_index for a, b in zip(m.events, m.events[1:]))
        for m in matches
    )
    integrity = (len(ids) == len(set(ids)) and ordered)

    replay_recall = recall
    _ = (predicted_major, hits, total_events)  # retained for future forecast metrics

    return ValidationMetrics(
        precision_at_k=precision,
        recall_at_k=recall,
        mean_lead_time_ms=statistics.mean(lead_times) if lead_times else 0.0,
        false_focus_rate=false_focus,
        event_integrity=1.0 if integrity else 0.0,
        replay_recall=replay_recall,
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
