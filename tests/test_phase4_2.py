import pandas as pd
import numpy as np
from src.rating_engine import _confidence_adjusted_delta, build_batter_ratings, build_bowler_ratings


def test_two_sample_reliability_penalizes_small_normal_baseline():
    delta_small, _, _ = _confidence_adjusted_delta(150, 100, 120, 30, 60)
    delta_small = delta_small.iloc[0]
    delta_large, _, _ = _confidence_adjusted_delta(150, 100, 120, 600, 60)
    delta_large = delta_large.iloc[0]
    assert delta_large > delta_small > 0


def test_consistency_merge_keeps_weighted_fields_without_ci():
    bat = pd.DataFrame([{
        "striker_id": 1, "striker_name": "A",
        "pressure_strike_rate": 150, "normal_strike_rate": 110,
        "pressure_dot_ball_pct": 30, "normal_dot_ball_pct": 40,
        "pressure_boundary_pct": 20, "normal_boundary_pct": 15,
        "pressure_dismissal_rate_pct": 3, "normal_dismissal_rate_pct": 5,
        "normal_balls_faced": 150, "normal_exposure_matches": 8,
        "weighted_match_metric_mean": 145.0,
        "weighted_match_metric_std": 22.0, "consistency_exposure_balls": 100,
    }])
    sample = pd.DataFrame([{"striker_id": 1, "pressure_balls": 150, "pressure_matches": 12}])
    consistency = pd.DataFrame([{
        "player_id": 1, "pressure_match_count": 12, "match_metric_mean": 140,
        "match_metric_std": 25, "match_metric_median": 138,
        "weighted_match_metric_mean": 145, "weighted_match_metric_std": 22,
        "consistency_exposure_balls": 150,
    }])
    out, _ = build_batter_ratings(bat, sample, consistency)
    assert out.weighted_match_metric_mean.iloc[0] == 145
    assert out.weighted_match_metric_std.iloc[0] == 22
    assert out.consistency_exposure_balls.iloc[0] == 150
    assert "match_metric_ci_low" not in out.columns
    assert out.reliability_tier.iloc[0] == "stronger"


def test_missing_consistency_does_not_create_fake_confidence_interval():
    bowl = pd.DataFrame([{
        "bowler_id": 2, "bowler_name": "B",
        "pressure_economy": 7, "normal_economy": 9,
        "pressure_dot_ball_pct": 40, "normal_dot_ball_pct": 30,
        "pressure_wickets_per_over": 0.8, "normal_wickets_per_over": 0.4,
        "pressure_boundary_conceded_pct": 10, "normal_boundary_conceded_pct": 20,
        "pressure_charged_extras_per_over": 0.1, "normal_charged_extras_per_over": 0.2,
        "normal_legal_balls": 180, "normal_exposure_matches": 8,
    }])
    sample = pd.DataFrame([{"bowler_id": 2, "pressure_legal_balls": 180, "pressure_matches": 12}])
    consistency = pd.DataFrame(columns=["player_id", "weighted_match_metric_mean", "weighted_match_metric_std"])
    out, _ = build_bowler_ratings(bowl, sample, consistency)
    assert pd.isna(out.weighted_match_metric_mean.iloc[0])
    assert pd.isna(out.weighted_match_metric_std.iloc[0])
    assert out.uncertainty_flag.iloc[0] == "insufficient_match_variance"
