from .schemas import Outcome

class ScoringAdapter:
    def __init__(self):
        pass

    def calculate_gte_score(self, outcome: Outcome) -> float:
        """
        Translates raw normalized outcomes into a canonical GTE Score.
        """
        base_score = 50.0
        acc_bonus = outcome.normalized.accuracy * 20.0
        eff_bonus = outcome.normalized.efficiency_score * 5.0

        # Combine normalized components and confidence
        score = base_score + (acc_bonus + eff_bonus) * outcome.confidence

        return round(score, 2)
