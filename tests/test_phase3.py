
import pandas as pd
from src.performance_engine import prepare_performance_events, _aggregate_batting, _aggregate_bowling

def sample():
    rows = [
        # Batter 10, normal, legal dot
        dict(match_id=1,innings=1,striker_id=10,striker_name="A",bowler_id=20,bowler_name="X",
             runs=0,extras1_runs=0,extras_2_runs=0,extras_type=None,is_wicket=False,
             dismissal_type=None,dismissed_player_id=None,is_four=False,is_six=False,
             pressure_level="low",pressure_eligible=True,is_regulation_innings=True,is_super_over=False),
        # Wide: no batter ball, legal ball or bowler dot; one conceded
        dict(match_id=1,innings=1,striker_id=10,striker_name="A",bowler_id=20,bowler_name="X",
             runs=0,extras1_runs=1,extras_2_runs=0,extras_type="wide",is_wicket=False,
             dismissal_type=None,dismissed_player_id=None,is_four=False,is_six=False,
             pressure_level="high",pressure_eligible=True,is_regulation_innings=True,is_super_over=False),
        # No-ball/Overstep: batter faced, not legal bowler ball; 1 batter run + 1 extra
        dict(match_id=1,innings=1,striker_id=10,striker_name="A",bowler_id=20,bowler_name="X",
             runs=1,extras1_runs=1,extras_2_runs=0,extras_type="Overstep",is_wicket=False,
             dismissal_type=None,dismissed_player_id=None,is_four=False,is_six=False,
             pressure_level="high",pressure_eligible=True,is_regulation_innings=True,is_super_over=False),
        # Runout of non-striker id 11: batter A faced ball, dismissal belongs to player 11, not bowler
        dict(match_id=1,innings=1,striker_id=10,striker_name="A",bowler_id=20,bowler_name="X",
             runs=1,extras1_runs=0,extras_2_runs=0,extras_type=None,is_wicket=True,
             dismissal_type="RunOut",dismissed_player_id=11,is_four=False,is_six=False,
             pressure_level="high",pressure_eligible=True,is_regulation_innings=True,is_super_over=False),
        # Bowled wicket, pressure
        dict(match_id=2,innings=1,striker_id=12,striker_name="B",bowler_id=20,bowler_name="X",
             runs=0,extras1_runs=0,extras_2_runs=0,extras_type=None,is_wicket=True,
             dismissal_type="Bowled",dismissed_player_id=12,is_four=False,is_six=False,
             pressure_level="very_high",pressure_eligible=True,is_regulation_innings=True,is_super_over=False),
        # Legbye: not charged to bowler
        dict(match_id=2,innings=1,striker_id=12,striker_name="B",bowler_id=20,bowler_name="X",
             runs=0,extras1_runs=1,extras_2_runs=0,extras_type="legbyes",is_wicket=False,
             dismissal_type=None,dismissed_player_id=None,is_four=False,is_six=False,
             pressure_level="low",pressure_eligible=True,is_regulation_innings=True,is_super_over=False),
    ]
    for row in rows:
        row["non_striker_id"] = 11
        row["non_striker_name"] = "NonStriker"
    return pd.DataFrame(rows)

def test_batter_ball_count_excludes_wide_but_includes_overstep():
    e=prepare_performance_events(sample())
    a=_aggregate_batting(e)
    row=a[(a.striker_id==10)&(a.pressure_group=="pressure")].iloc[0]
    assert row.balls_faced==2  # Overstep + normal legal runout ball; wide excluded

def test_batter_dismissal_credited_to_dismissed_player_not_striker():
    e=prepare_performance_events(sample())
    a=_aggregate_batting(e)
    player11=a[a.striker_id==11]
    # Player 11's run-out is counted only if they have a striker aggregation row;
    # the synthetic sample intentionally has none, so no false attribution to batter 10.
    row=a[(a.striker_id==10)&(a.pressure_group=="pressure")].iloc[0]
    assert row.dismissals==0
    non_striker=a[(a.striker_id==11)&(a.pressure_group=="pressure")].iloc[0]
    assert non_striker.dismissals==1

def test_runout_not_credited_to_bowler_but_bowled_is():
    e=prepare_performance_events(sample())
    assert int(e.loc[e.dismissal_type.eq("RunOut"),"bowler_credit_wicket"].sum())==0
    assert int(e.loc[e.dismissal_type.eq("Bowled"),"bowler_credit_wicket"].sum())==1

def test_bowler_legal_balls_and_conceded_runs():
    e=prepare_performance_events(sample())
    a=_aggregate_bowling(e)
    pressure=a[a.pressure_group.eq("pressure")].iloc[0]
    # wide and Overstep are not legal; only runout legal ball and bowled legal ball count
    assert pressure.legal_balls==2
    # Wide 1 + no-ball batter run 1 + no-ball extra 1 + runout batter run 1 + bowled 0 = 4
    assert pressure.runs_conceded==4

def test_byes_legbyes_excluded_from_bowler_conceded_runs():
    e=prepare_performance_events(sample())
    leg=e[e.extras_type_norm.eq("legbyes")].iloc[0]
    assert leg.bowler_runs_conceded==0

def test_super_over_or_ineligible_rows_not_analysed():
    x=sample()
    x.loc[0,"is_super_over"]=True
    e=prepare_performance_events(x)
    assert not e.loc[0,"analysis_eligible"]


def test_legbye_label_prevents_bowler_charge_when_runs_field_conflicts():
    x=sample()
    x.loc[5,"runs"]=1
    x.loc[5,"extras1_runs"]=0
    e=prepare_performance_events(x)
    row=e[e.extras_type_norm.eq("legbyes")].iloc[0]
    assert row.scoring_semantics_anomaly
    assert row.bowler_runs_conceded==0
