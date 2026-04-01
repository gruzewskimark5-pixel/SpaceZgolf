import unittest
from datetime import datetime, timezone
from pipeline import UnifiedProtocolPipeline
from schema_unified import UnifiedCognitiveEvent

class TestPipeline(unittest.TestCase):
    def test_pipeline_execution(self):
        pipeline = UnifiedProtocolPipeline()

        # Mock Raw Event from Digital Glass
        raw_event = {
            "entity_id": "user_123",
            "timestamp": datetime.now(timezone.utc),
            "state": {
                "biometrics": {"hr_avg": 145},
                "environment": {"terrain_factor": 0.05, "heat_factor": 0.02, "altitude_factor": -0.01}
            },
            "decision": {
                "latency_ms": 250,
                "option_selected": "A",
                "confidence": 0.85
            },
            "causality": {
                "factors": {"fatigue": 0.2, "distraction": 0.1}
            },
            "outcome": {
                "performance_delta": 5.0,
                "accuracy": 0.92,
                "distance_km": 10.5,
                "pace_today": 5.5,
                "duration_today": 60
            },
            "integrity": {
                "factors": {"hr_signature": 0.95, "behavior_outlier": 0.88}
            }
        }

        # Mock User Profile (Baselines)
        user_profile = {
            "hr_baseline": 130,
            "streak_days": 15,
            "baselines": {
                "pace_baseline": 6.0,
                "duration_median": 45
            }
        }

        # Mock History (1 Event)
        history = [
            {
                "outcome": {"accuracy": 0.90},
                "decision": {"latency_ms": 300}
            }
        ]

        # Execute Pipeline
        unified_event = pipeline.process_event(raw_event, user_profile, history)

        # Assertions
        self.assertIsInstance(unified_event, UnifiedCognitiveEvent)
        self.assertEqual(unified_event.entity_id, "user_123")
        self.assertIsNotNone(unified_event.scoring)
        self.assertIsNotNone(unified_event.integrity)
        self.assertIsNotNone(unified_event.leaderboard)

        # Check Computed Deltas in Outcome
        self.assertAlmostEqual(unified_event.outcome.accuracy_delta, 0.02, places=2)
        self.assertEqual(unified_event.outcome.latency_delta, -50)

        # Check Base Output calculation (distance_km was passed into adapter, GTE uses it as BO if activity type matches)
        # Note: In our current adapter, we hardcode activity_type to "derived", which defaults BO to 0.0 in GTEEngine.
        self.assertEqual(unified_event.scoring.components["BO"], 0.0)

if __name__ == '__main__':
    unittest.main()
