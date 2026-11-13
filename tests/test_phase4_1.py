import numpy as np
import pandas as pd

from src.rating_engine import build_batter_ratings, build_bowler_ratings, _rank


def test_batter_requires_normal_baseline_exposure():
    bat = pd.DataFrame([{
        "striker_id": 1, "striker_name": "Batter",
        "pressure_strike_rate": 140, "normal_strike_rate": 110,
        "pressure_dot_ball_pct": 30, "normal_dot_ball_pct": 40,
        "pressure_boundary_pct": 20, "normal_boundary_pct": 15,
        "pressure_dismissal_rate_pct": 3, "normal_dismissal_rate_pct": 5,
        "normal_balls_faced": 12, "normal_exposure_matches": 2,
    }])
    sample = pd.DataFrame([{"striker_id": 1, "pressure_balls": 80, "pressure_matches": 8}])
    consistency = pd.DataFrame([{
        "player_id": 1, "pressure_match_count": 8, "match_metric_mean": 140,
        "match_metric_std": 15, "match_metric_median": 138,
        "weighted_match_metric_mean": 140, "weighted_match_metric_std": 12,
        "consistency_exposure_balls": 80,
    }])
    result, _ = build_batter_ratings(bat, sample, consistency)
    assert not bool(result.loc[0, "eligible"])
    assert result.loc[0, "reliability_tier"] == "not_eligible"


def test_bowler_requires_normal_baseline_exposure():
    bowl = pd.DataFrame([{
        "bowler_id": 2, "bowler_name": "Bowler",
        "pressure_economy": 7, "normal_economy": 9,
        "pressure_dot_ball_pct": 40, "normal_dot_ball_pct": 30,
        "pressure_wickets_per_over": 0.8, "normal_wickets_per_over": 0.4,
        "pressure_boundary_conceded_pct": 10, "normal_boundary_conceded_pct": 20,
        "pressure_charged_extras_per_over": 0.1, "normal_charged_extras_per_over": 0.2,
        "normal_legal_balls": 10, "normal_exposure_matches": 1,
    }])
    sample = pd.DataFrame([{"bowler_id": 2, "pressure_legal_balls": 100, "pressure_matches": 8}])
    consistency = pd.DataFrame([{
        "player_id": 2, "pressure_match_count": 8, "match_metric_mean": 7,
        "match_metric_std": 1, "match_metric_median": 7,
        "weighted_match_metric_mean": 7, "weighted_match_metric_std": 1,
        "consistency_exposure_balls": 100,
    }])
    result, _ = build_bowler_ratings(bowl, sample, consistency)
    assert not bool(result.loc[0, "eligible"])


def test_rank_excludes_non_finite_scores():
    frame = pd.DataFrame({
        "player_id": [1, 2], "player_name": ["A", "B"],
        "eligible": [True, True], "rating": [1.0, np.nan],
        "pressure_balls": [50, 60], "pressure_matches": [5, 6],
        "uncertainty_flag": ["standard", "standard"],
    })
    ranked = _rank(frame, "player_id", "player_name", "rating")
    assert ranked.player_id.tolist() == [1]
