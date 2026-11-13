
import pandas as pd
from src.rating_engine import _robust_z, _shrink_rate, build_batter_ratings, build_bowler_ratings

def test_robust_z_direction():
    x=pd.Series([1.,2.,3.])
    assert _robust_z(x,True).iloc[2] > _robust_z(x,True).iloc[0]
    assert _robust_z(x,False).iloc[2] < _robust_z(x,False).iloc[0]

def test_shrinkage_moves_small_sample_toward_normal():
    shrunk,w=_shrink_rate(200.,100.,10.,60.)
    assert 100 < shrunk < 200
    assert 0 < w < 1

def test_batter_minimum_exposure_eligibility():
    bat=pd.DataFrame([dict(striker_id=1,striker_name="A",pressure_strike_rate=150,normal_strike_rate=120,
        pressure_dot_ball_pct=30,normal_dot_ball_pct=40,pressure_boundary_pct=20,normal_boundary_pct=15,
        pressure_dismissal_rate_pct=3,normal_dismissal_rate_pct=5)])
    sample=pd.DataFrame([dict(striker_id=1,pressure_balls=20,pressure_matches=6)])
    consistency=pd.DataFrame([dict(player_id=1,pressure_match_count=6,match_metric_mean=150,match_metric_std=20,match_metric_median=145)])
    out,_=build_batter_ratings(bat,sample,consistency)
    assert not bool(out.eligible.iloc[0])

def test_bowler_directional_components():
    bowl=pd.DataFrame([dict(bowler_id=2,bowler_name="B",pressure_economy=7,normal_economy=9,
        pressure_dot_ball_pct=40,normal_dot_ball_pct=30,pressure_wickets_per_over=0.8,normal_wickets_per_over=0.4,
        pressure_boundary_conceded_pct=10,normal_boundary_conceded_pct=20,
        pressure_charged_extras_per_over=0.1,normal_charged_extras_per_over=0.2,
        normal_legal_balls=100,normal_exposure_matches=5)])
    sample=pd.DataFrame([dict(bowler_id=2,pressure_legal_balls=100,pressure_matches=8)])
    consistency=pd.DataFrame([dict(player_id=2,pressure_match_count=8,match_metric_mean=7,match_metric_std=1,match_metric_median=7)])
    out,_=build_bowler_ratings(bowl,sample,consistency)
    assert out.economy_component.iloc[0] > 0
    assert out.dot_component.iloc[0] > 0
    assert out.wicket_component.iloc[0] > 0
