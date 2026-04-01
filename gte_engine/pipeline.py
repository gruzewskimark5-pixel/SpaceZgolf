from typing import Dict, Any, List
from gte_engine.models import UnifiedCognitiveEvent, EventOutcome, EventScoring, EventIntegrity, EventState, EventDecision, EventCausality, EventLeaderboard
from gte_engine.outcome_engine import OutcomeEngine
from gte_engine.scoring_adapter import ScoringAdapter

class UnifiedProtocolPipeline:
    def __init__(self):
        self.outcome_engine = OutcomeEngine()
        self.scoring_adapter = ScoringAdapter()
        # Assume a mock GTE Scoring Service and mock Integrity Engine for now

    def _run_integrity_checks(self, event: Dict[str, Any]) -> EventIntegrity:
        # Mocking integrity calculation
        return EventIntegrity(
            score=0.95,
            flags=["gps_noise_low"],
            factors={
                "hr_signature": 0.92,
                "behavior_outlier": 0.85
            }
        )

    def _score_event_with_gte(self, activity: Dict[str, Any]) -> EventScoring:
        # Mocking GTE scoring via the activity adapter
        perf = activity.get("raw", {}).get("performance", 0.0)
        return EventScoring(
            performance_score=85.0 + (perf * 10),
            integrity_score=0.95,
            components={"execution": 40.0, "decision": 45.0}
        )

    def process_event(self, raw_telemetry: Dict[str, Any], history: List[Dict[str, Any]]) -> UnifiedCognitiveEvent:
        """
        Fuses Telemetry -> Decision -> Outcome -> Score -> Rank
        """

        # 1. Base Event
        event_dict = {
            "entity_id": raw_telemetry.get("athlete_id", "unknown_user"),
            "timestamp": raw_telemetry.get("timestamp"),
            "state": EventState(
                biometrics=raw_telemetry.get("telemetry", {}),
                context=raw_telemetry.get("context", {})
            ),
            "decision": EventDecision(
                latency_ms=raw_telemetry.get("decision", {}).get("latency_ms", 500.0),
                choice=raw_telemetry.get("decision", {}).get("club_selected", "driver"),
                confidence=raw_telemetry.get("decision", {}).get("confidence_score"),
                complexity=raw_telemetry.get("decision", {}).get("execution_complexity")
            ),
            "causality": EventCausality(
                factors=raw_telemetry.get("trace", [])
            )
        }

        # Setup event inputs for the outcome engine
        outcome_input = {
            "accuracy": raw_telemetry.get("outcome", {}).get("accuracy", 0.0),
            "latency": event_dict["decision"].latency_ms
        }

        # 2. Compute Outcomes dynamically based on history
        computed_outcome = self.outcome_engine.compute(outcome_input, history)

        event_dict["outcome"] = EventOutcome(
            performance_delta=computed_outcome["accuracy_delta"],
            accuracy=outcome_input["accuracy"],
            latency=outcome_input["latency"],
            raw_metrics=raw_telemetry.get("outcome", {})
        )

        # 3. Integrity checks (Integrity MUST feed back into Digital Glass causality/outcome)
        event_dict["integrity"] = self._run_integrity_checks(event_dict)

        # 4. Score through Adapter
        activity_payload = self.scoring_adapter.to_activity(event_dict)
        event_dict["scoring"] = self._score_event_with_gte(activity_payload)

        # 5. Leaderboard Update (Mock for now, normally an external service query)
        event_dict["leaderboard"] = EventLeaderboard(
            delta_rank=+3,
            current_rank=42
        )

        return UnifiedCognitiveEvent(**event_dict)
