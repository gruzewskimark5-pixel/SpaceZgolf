from .schemas import RawTelemetryEvent, UnifiedCognitiveEvent
from .outcome_engine import OutcomeEngine
from .scoring_adapter import ScoringAdapter
from .integrity_engine import IntegrityEngine
import uuid

class UnifiedProtocolPipeline:
    def __init__(self):
        self.outcome_engine = OutcomeEngine()
        self.scoring_adapter = ScoringAdapter()
        self.integrity_engine = IntegrityEngine()

    def process_telemetry(self, raw_event: RawTelemetryEvent) -> UnifiedCognitiveEvent:
        """
        Main pipeline orchestrating the processing of a raw telemetry event into a canonical UnifiedCognitiveEvent.
        """
        # 1. Calculate outcomes and normalization
        outcome = self.outcome_engine.process_event(raw_event)

        # 2. Derive GTE Score from the normalized outcomes
        gte_score = self.scoring_adapter.calculate_gte_score(outcome)

        # 3. Calculate Integrity Score via ML Ensemble mock
        integrity_score = self.integrity_engine.calculate_integrity(raw_event)

        # 4. Construct canonical event
        canonical_event = UnifiedCognitiveEvent(
            event_id=raw_event.event_id,
            entity_id=raw_event.entity_id,
            ts=raw_event.ts,
            raw_payload=raw_event,
            outcome=outcome,
            integrity_score=integrity_score,
            gte_score=gte_score
        )

        return canonical_event
