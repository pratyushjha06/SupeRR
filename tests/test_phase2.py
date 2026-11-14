
import pandas as pd
from src.pressure_engine import build_match_state, classify_pressure

def synthetic():
    ball = pd.DataFrame([
        # First innings: legal, wide, legal, Overstep
        {"match_id":1,"innings":1,"innings_ball_num":1,"overid":1,"over_ball_num":1,"runs":1,"extras1_runs":0,"extras_2_runs":0,"is_wicket":False,"extras_type":None},
        {"match_id":1,"innings":1,"innings_ball_num":2,"overid":1,"over_ball_num":2,"runs":0,"extras1_runs":1,"extras_2_runs":0,"is_wicket":False,"extras_type":"wide"},
        {"match_id":1,"innings":1,"innings_ball_num":3,"overid":1,"over_ball_num":3,"runs":4,"extras1_runs":0,"extras_2_runs":0,"is_wicket":True,"extras_type":None},
        {"match_id":1,"innings":1,"innings_ball_num":4,"overid":1,"over_ball_num":4,"runs":0,"extras1_runs":1,"extras_2_runs":0,"is_wicket":False,"extras_type":"Overstep"},
        {"match_id":1,"innings":1,"innings_ball_num":5,"overid":1,"over_ball_num":5,"runs":2,"extras1_runs":0,"extras_2_runs":0,"is_wicket":False,"extras_type":None},
        # Chase
        {"match_id":1,"innings":2,"innings_ball_num":1,"overid":1,"over_ball_num":1,"runs":0,"extras1_runs":0,"extras_2_runs":0,"is_wicket":False,"extras_type":None},
        {"match_id":1,"innings":2,"innings_ball_num":2,"overid":1,"over_ball_num":2,"runs":1,"extras1_runs":0,"extras_2_runs":0,"is_wicket":False,"extras_type":None},
    ])
    matches = pd.DataFrame([{"match_id":1,"comp_id":10,"first_inn_revised_overs":None,"second_inn_revised_overs":None,"revised_target":None}])
    comps = pd.DataFrame([{"comp_id":10,"comp_name":"Synthetic T20","match_format":"T20","season":"2025"}])
    return ball,matches,comps

def test_illegal_deliveries_do_not_consume_legal_balls():
    b,m,c = synthetic()
    s = build_match_state(b,m,c)
    first = s[s.innings.eq(1)].reset_index(drop=True)
    assert first.loc[0,"legal_balls_before"] == 0
    assert first.loc[1,"legal_balls_before"] == 1
    assert first.loc[2,"legal_balls_before"] == 1
    assert first.loc[3,"legal_balls_before"] == 2
    assert first.loc[4,"legal_balls_before"] == 2
    assert first.loc[4,"runs_before"] == 7

def test_team_runs_include_batter_runs_and_extras():
    b,m,c = synthetic()
    s = build_match_state(b,m,c)
    first = s[s.innings.eq(1)]
    assert first["team_runs_this_delivery"].sum() == 9

def test_super_over_is_excluded():
    b,m,c = synthetic()
    extra = b.iloc[[0]].copy()
    extra["innings"] = 3
    extra["match_id"] = 2
    m2 = pd.concat([m, pd.DataFrame([{"match_id":2,"comp_id":10,"first_inn_revised_overs":None,"second_inn_revised_overs":None,"revised_target":None}])], ignore_index=True)
    s = build_match_state(pd.concat([b,extra],ignore_index=True),m2,c)
    out = classify_pressure(s)
    assert out.loc[out.match_id.eq(2),"is_super_over"].all()
    assert not out.loc[out.match_id.eq(2),"pressure_eligible"].any()

def test_chase_has_target_and_pressure_score():
    b,m,c = synthetic()
    out = classify_pressure(build_match_state(b,m,c))
    chase = out[out.innings.eq(2)]
    assert chase["target"].notna().all()
    assert chase["pressure_score"].notna().all()
    assert chase["pressure_score"].between(0,100).all()

def test_first_innings_par_rate_uses_only_prior_match_dates():
    from src.pressure_engine import classify_pressure
    # Build four prior matches plus one later match in the same competition-season.
    balls=[]; matches=[]
    final_runs=[120, 132, 144, 156, 300]
    dates=['2025-01-01','2025-01-02','2025-01-03','2025-01-04','2025-01-05']
    for mid,(runs,date) in enumerate(zip(final_runs,dates),start=1):
        matches.append({'match_id':mid,'comp_id':10,'match_date':date,
                        'first_inn_revised_overs':None,'second_inn_revised_overs':None,
                        'revised_target':None})
        # Twenty legal balls; distribute total across 20 deliveries.
        q,r=divmod(runs,20)
        for ball_no in range(1,21):
            balls.append({'match_id':mid,'innings':1,'innings_ball_num':ball_no,
                          'overid':(ball_no-1)//6+1,'over_ball_num':(ball_no-1)%6+1,
                          'runs':q+(1 if ball_no<=r else 0),'extras1_runs':0,
                          'extras_2_runs':0,'is_wicket':False,'extras_type':None})
    comps=pd.DataFrame([{'comp_id':10,'comp_name':'Synthetic T20','match_format':'T20','season':'2025'}])
    state=build_match_state(pd.DataFrame(balls),pd.DataFrame(matches),comps)
    classified=classify_pressure(state)
    # Match 5 must use median of matches 1-4 (41.4), not its own 90.0 or any future data.
    m5=classified[classified.match_id.eq(5)]
    assert m5.par_run_rate.nunique()==1
    assert abs(float(m5.par_run_rate.iloc[0])-41.4)<1e-9


def test_same_date_matches_do_not_leak_into_each_others_par_reference():
    balls=[]; matches=[]
    for mid,(runs,date) in enumerate([(120,'2025-01-01'),(132,'2025-01-02'),
                                      (144,'2025-01-03'),(156,'2025-01-04'),
                                      (300,'2025-01-05'),(60,'2025-01-05')],start=1):
        matches.append({'match_id':mid,'comp_id':10,'match_date':date,
                        'first_inn_revised_overs':None,'second_inn_revised_overs':None,
                        'revised_target':None})
        q,r=divmod(runs,20)
        for ball_no in range(1,21):
            balls.append({'match_id':mid,'innings':1,'innings_ball_num':ball_no,
                          'overid':(ball_no-1)//6+1,'over_ball_num':(ball_no-1)%6+1,
                          'runs':q+(1 if ball_no<=r else 0),'extras1_runs':0,
                          'extras_2_runs':0,'is_wicket':False,'extras_type':None})
    comps=pd.DataFrame([{'comp_id':10,'comp_name':'Synthetic T20','match_format':'T20','season':'2025'}])
    out=classify_pressure(build_match_state(pd.DataFrame(balls),pd.DataFrame(matches),comps))
    values=out.loc[out.match_id.isin([5,6]),['match_id','par_run_rate']].drop_duplicates()
    assert values.par_run_rate.nunique()==1
