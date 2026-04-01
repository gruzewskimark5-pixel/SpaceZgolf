from typing import Dict, Any, List
from scoring import GTEEngine
from adapter import ScoringAdapter
from outcome import OutcomeEngine
from schema_unified import UnifiedCognitiveEvent, ScoringDetails, IntegrityDetails, LeaderboardDetails

class UnifiedProtocolPipeline:
    """
    The closed-loop, fraud-resistant, explainable performance protocol.
    Coordinates the Outcome Engine, Scoring Adapter, and GTE Engine to produce Unified Events.
    """
    def __init__(self):
        self.gte_engine = GTEEngine()
        self.scoring_adapter = ScoringAdapter()
        self.outcome_engine = OutcomeEngine()

    def process_event(self, raw_event: Dict[str, Any], user_profile: Dict[str, Any], history: List[Dict[str, Any]]) -> UnifiedCognitiveEvent:
        """
        Takes raw inputs, calculates outcomes, runs anti-cheat/integrity, computes score, and returns the canonical event.
        """
        # 1. Outcome Engine computes deltas (Accuracy, Latency)
        outcome_deltas = self.outcome_engine.compute(raw_event, history)

        # Inject computed deltas into raw event's outcome block
        raw_event["outcome"]["accuracy_delta"] = outcome_deltas.get("accuracy_delta", 0.0)
        raw_event["outcome"]["latency_delta"] = outcome_deltas.get("latency_delta", 0.0)

        # 2. Scoring Adapter maps Unified Digital Glass Event -> GTE payload
        gte_payload = self.scoring_adapter.to_activity(raw_event)

        # 3. GTE Engine calculates Performance Score (PS) + components
        score_result = self.gte_engine.calculate_performance_score(gte_payload, user_profile)

        # 4. Anti-cheat/Integrity evaluation (Mocked for pipeline completeness)
        # In a real system, this is a separate machine learning model analyzing HR signature, GPS, etc.
        integrity_score = self.gte_engine.calculate_integrity_score(
             raw_event.get("integrity", {}).get("factors", {}),
             {"hr_signature": 0.5, "behavior_outlier": 0.5} # Mock weights
        )

        # 5. Build Unified Canonical Event
        event_model = UnifiedCognitiveEvent(
             entity_id=raw_event["entity_id"],
             state=raw_event["state"],
             decision=raw_event["decision"],
             causality=raw_event["causality"],
             outcome=raw_event["outcome"]
        )

        # Hydrate Scoring + Integrity
        event_model.integrity = IntegrityDetails(
             score=integrity_score,
             flags=["verified"], # Mock flag
             factors=raw_event.get("integrity", {}).get("factors", {})
        )

        event_model.scoring = ScoringDetails(
             performance_score=score_result["performance_score"],
             integrity_score=integrity_score,
             components=score_result["components"]
        )

        # Mocking Leaderboard projection calculation
        # This occurs down-stream via Redis, but the rank deltas can be captured in the final event ledger
        event_model.leaderboard = LeaderboardDetails(
            delta_rank=1, # Mock
            current_rank=100 # Mock
        )

        return event_model
