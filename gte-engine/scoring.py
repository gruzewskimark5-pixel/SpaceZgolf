import math
from typing import Dict, Any

class GTEEngine:
    def __init__(self):
        # Configuration constants
        self.k1 = 0.4
        self.k2 = 0.5
        self.k3 = 0.3

    def calculate_base_output(self, activity: Dict[str, Any]) -> float:
        """
        Calculates Base Output (BO) based on activity type.
        """
        activity_type = activity.get('type')

        if activity_type in ['running', 'cycling', 'rowing']:
            return activity.get('distance_km', 0.0)
        elif activity_type == 'strength':
            sets = activity.get('sets', [])
            return sum(s.get('reps', 0) * s.get('load', 0.0) for s in sets)
        elif activity_type in ['mobility', 'yoga']:
            return activity.get('duration_min', 0.0) / 10.0
        return 0.0

    def calculate_intensity_multiplier(self, hr_avg: float, hr_baseline: float) -> float:
        """
        Calculates Intensity Multiplier (IM).
        Capped between 0.6 and 1.5.
        """
        if hr_baseline <= 0:
            return 1.0
        im = 1 + ((hr_avg - hr_baseline) / hr_baseline) * self.k1
        return max(0.6, min(1.5, im))

    def calculate_consistency_modifier(self, streak_days: int) -> float:
        """
        Calculates Consistency Modifier (CM).
        """
        return 1 + 0.5 * (1 - math.exp(-streak_days / 30.0))

    def calculate_context_weight(self, context: Dict[str, float]) -> float:
        """
        Calculates Context Weight (CW).
        Factors: terrain, heat, altitude (-0.1 to 0.1 each).
        Total range: 0.8 to 1.3
        """
        terrain = max(-0.1, min(0.1, context.get('terrain_factor', 0.0)))
        heat = max(-0.1, min(0.1, context.get('heat_factor', 0.0)))
        altitude = max(-0.1, min(0.1, context.get('altitude_factor', 0.0)))

        cw = 1 + terrain + heat + altitude
        return max(0.8, min(1.3, cw))

    def calculate_integrity_score(self, anomaly_factors: Dict[str, float], weights: Dict[str, float]) -> float:
        """
        Calculates Integrity Score (IS).
        Composite trust score (0 to 1).
        """
        is_score = 1.0
        for key, factor in anomaly_factors.items():
            weight = weights.get(key, 0.0)
            is_score *= (weight * factor)
        return is_score

    def calculate_adaptive_baseline(self, baselines: Dict[str, float], activity_metrics: Dict[str, float]) -> float:
        """
        Calculates Adaptive Baseline (AB).
        PB = Pace Baseline
        SB = Strength Baseline
        HB = HR Efficiency Baseline
        BB = Behavioral Baseline
        """
        # 6.1 Pace Baseline (PB)
        pb = 1.0
        if activity_metrics.get('pace_today', 0) > 0 and baselines.get('pace_baseline', 0) > 0:
            pb = baselines['pace_baseline'] / activity_metrics['pace_today']
        pb = max(0.7, min(1.6, pb))

        # 6.2 Strength Baseline (SB)
        sb = 1.0
        if activity_metrics.get('volume_expected', 0) > 0:
             sb = activity_metrics.get('volume_today', 0) / activity_metrics['volume_expected']
        sb = max(0.7, min(1.6, sb))

        # 6.3 HR Efficiency Baseline (HB)
        hb = 1.0
        hr_baseline = baselines.get('hr_baseline', 0)
        hr_today = activity_metrics.get('hr_today', 0)
        if hr_baseline > 0:
            hb = 1 + ((hr_baseline - hr_today) / hr_baseline) * self.k2
        hb = max(0.7, min(1.6, hb))

        # 6.4 Behavioral Baseline (BB)
        bb = 1.0
        duration_median = baselines.get('duration_median', 0)
        duration_today = activity_metrics.get('duration_today', 0)
        if duration_median > 0:
             bb = 1 + ((duration_today - duration_median) / duration_median) * self.k3
        bb = max(0.7, min(1.6, bb))

        ab = 0.25 * pb + 0.25 * sb + 0.25 * hb + 0.25 * bb
        return ab

    def calculate_performance_score(self, activity: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates the final Performance Score (PS) and returns all components.
        """
        bo = self.calculate_base_output(activity)

        im = self.calculate_intensity_multiplier(
            activity.get('hr_avg', 0),
            user_profile.get('hr_baseline', 0)
        )

        cm = self.calculate_consistency_modifier(user_profile.get('streak_days', 0))
        cw = self.calculate_context_weight(activity.get('context', {}))

        ab = self.calculate_adaptive_baseline(
            user_profile.get('baselines', {}),
            activity.get('metrics', {})
        )

        # Simple IS logic for now, assumes no anomalies if not provided. In real system, this is a separate engine.
        is_score = 1.0

        ps = (bo * im * cm * cw * ab) * is_score

        return {
            'performance_score': ps,
            'components': {
                'BO': bo,
                'IM': im,
                'CM': cm,
                'CW': cw,
                'AB': ab,
                'IS': is_score
            }
        }
