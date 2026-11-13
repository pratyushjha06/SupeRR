from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"

def summarize_match(df, idcol, namecol, metrics, exposure):
    rows=[]
    for pid,g in df.groupby(idcol):
        rec={"player_id":pid,"player":g[namecol].iloc[0]}
        for group in ["pressure","normal"]:
            x=g[g.pressure_group.eq(group)]
            rec[f"{group}_matches"]=int(x.match_id.nunique())
            rec[f"{group}_exposure"]=int(x[exposure].sum())
            for metric in metrics:
                vals=x[metric].dropna()
                for stat,func in [("median",lambda z:z.median()),("mean",lambda z:z.mean()),
                                  ("sd",lambda z:z.std(ddof=1)),("p25",lambda z:z.quantile(.25)),
                                  ("p75",lambda z:z.quantile(.75))]:
                    rec[f"{group}_{metric}_match_{stat}"]=func(vals) if len(vals) else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)

def main():
    d=pd.read_csv(OUT/"pressure_classified_deliveries.csv",low_memory=False)
    m=pd.read_csv(OUT/"matches_with_competition_metadata.csv")
    is_ipl=m.comp_name.astype(str).str.fullmatch(r"IPL\s+\d{4}",case=False,na=False)
    is_t20i=m.match_format.astype(str).str.upper().eq("T20I")
    d=d[d.match_id.isin(set(m.loc[is_ipl|is_t20i,"match_id"]))].copy()
    d=d[d.pressure_eligible.fillna(False)&d.is_regulation_innings.fillna(False)].copy()
    d["pressure_group"]=np.where(d.pressure_level.isin(["high","very_high"]),"pressure",
                           np.where(d.pressure_level.isin(["low","moderate"]),"normal",None))
    d=d[d.pressure_group.notna()].copy()
    d["is_wide"]=d.extras_type_norm.eq("wide")
    d["is_overstep"]=d.extras_type_norm.eq("overstep")
    d["bat_balls_faced"]=(~d.is_wide).astype(int)
    d["bat_dot"]=(d.batter_runs.eq(0)&~d.is_wide).astype(int)
    d["bat_runs"]=d.batter_runs.fillna(0)
    d["bat_boundary"]=(d.is_four.fillna(False)|d.is_six.fillna(False)).astype(int)
    bat=d.groupby(["striker_id","striker_name","match_id","pressure_group"]).agg(
        balls=("bat_balls_faced","sum"),runs=("bat_runs","sum"),dots=("bat_dot","sum"),
        boundaries=("bat_boundary","sum")).reset_index()
    dis=d[d.is_wicket.fillna(False)&d.dismissed_player_id.notna()].groupby(
        ["dismissed_player_id","match_id","pressure_group"]).size().rename("dismissals").reset_index()
    bat=bat.merge(dis,left_on=["striker_id","match_id","pressure_group"],
                  right_on=["dismissed_player_id","match_id","pressure_group"],how="left").drop(columns="dismissed_player_id")
    bat["dismissals"]=bat.dismissals.fillna(0)
    bat["sr"]=100*bat.runs/bat.balls.replace(0,np.nan)
    bat["dot_pct"]=100*bat.dots/bat.balls.replace(0,np.nan)
    bat["boundary_pct"]=100*bat.boundaries/bat.balls.replace(0,np.nan)
    bat["dismissal_rate"]=100*bat.dismissals/bat.balls.replace(0,np.nan)

    d["bowl_legal"]=(~d.is_wide&~d.is_overstep).astype(int)
    d["bowl_runs"]=d.batter_runs.fillna(0)+np.where(d.is_wide|d.is_overstep,d.extra_runs.fillna(0),0)
    d["bowl_dot"]=(d.bowl_runs.eq(0)&d.bowl_legal.eq(1)).astype(int)
    d["bowl_boundary"]=(d.is_four.fillna(False)|d.is_six.fillna(False)).astype(int)
    d["bowl_wicket"]=(d.is_wicket.fillna(False)&d.dismissal_type.astype(str).str.lower().isin(
        {"caught","bowled","lbw","stump","hit wicket"})).astype(int)
    bowl=d.groupby(["bowler_id","bowler_name","match_id","pressure_group"]).agg(
        legal_balls=("bowl_legal","sum"),runs_conceded=("bowl_runs","sum"),dots=("bowl_dot","sum"),
        wickets=("bowl_wicket","sum"),boundaries=("bowl_boundary","sum")).reset_index()
    bowl["economy"]=6*bowl.runs_conceded/bowl.legal_balls.replace(0,np.nan)
    bowl["dot_pct"]=100*bowl.dots/bowl.legal_balls.replace(0,np.nan)
    bowl["wickets_per_over"]=6*bowl.wickets/bowl.legal_balls.replace(0,np.nan)
    bowl["boundary_pct"]=100*bowl.boundaries/bowl.legal_balls.replace(0,np.nan)

    bt=pd.read_csv(OUT/"phase4_3_batter_top20_full.csv").head(15)
    wt=pd.read_csv(OUT/"phase4_3_bowler_top20_full.csv").head(15)
    bs=summarize_match(bat,"striker_id","striker_name",["sr","dot_pct","boundary_pct","dismissal_rate"],"balls")
    ws=summarize_match(bowl,"bowler_id","bowler_name",["economy","dot_pct","wickets_per_over","boundary_pct"],"legal_balls")
    ba=bt[["balanced_rank","striker_id","striker_name","reliability_tier","uncertainty_flag","rating_balanced"]].merge(
        bs,left_on="striker_id",right_on="player_id",how="left")
    wa=wt[["balanced_rank","bowler_id","bowler_name","reliability_tier","uncertainty_flag","rating_balanced"]].merge(
        ws,left_on="bowler_id",right_on="player_id",how="left")
    for col,expr in {
        "match_median_sr_delta":"pressure_sr_match_median-normal_sr_match_median",
        "match_median_dot_pct_delta":"pressure_dot_pct_match_median-normal_dot_pct_match_median",
        "match_median_boundary_pct_delta":"pressure_boundary_pct_match_median-normal_boundary_pct_match_median",
        "match_median_dismissal_rate_delta":"pressure_dismissal_rate_match_median-normal_dismissal_rate_match_median"}.items():
        ba[col]=ba.eval(expr)
    for col,expr in {
        "match_median_economy_delta":"pressure_economy_match_median-normal_economy_match_median",
        "match_median_dot_pct_delta":"pressure_dot_pct_match_median-normal_dot_pct_match_median",
        "match_median_wickets_per_over_delta":"pressure_wickets_per_over_match_median-normal_wickets_per_over_match_median",
        "match_median_boundary_pct_delta":"pressure_boundary_pct_match_median-normal_boundary_pct_match_median"}.items():
        wa[col]=wa.eval(expr)
    def fav_b(r):
        v=[r.match_median_sr_delta,-r.match_median_dot_pct_delta,r.match_median_boundary_pct_delta,-r.match_median_dismissal_rate_delta]
        v=[x for x in v if pd.notna(x)]
        return f"{sum(x>0 for x in v)}/{len(v)}"
    def fav_w(r):
        v=[-r.match_median_economy_delta,r.match_median_dot_pct_delta,r.match_median_wickets_per_over_delta,-r.match_median_boundary_pct_delta]
        v=[x for x in v if pd.notna(x)]
        return f"{sum(x>0 for x in v)}/{len(v)}"
    ba["match_median_favourable_components"]=ba.apply(fav_b,axis=1)
    wa["match_median_favourable_components"]=wa.apply(fav_w,axis=1)
    for df in [ba,wa]:
        df["match_level_sample_flag"]=np.where(df.pressure_matches<5,"under_5_pressure_matches",
            np.where(df.normal_matches<3,"under_3_normal_matches","meets_match_count_marker"))
    bd=bat[bat.striker_id.isin(set(bt.striker_id))].merge(
        bt[["balanced_rank","striker_id","reliability_tier","uncertainty_flag","rating_balanced"]],on="striker_id",how="left")
    wd=bowl[bowl.bowler_id.isin(set(wt.bowler_id))].merge(
        wt[["balanced_rank","bowler_id","reliability_tier","uncertainty_flag","rating_balanced"]],on="bowler_id",how="left")
    ba.to_csv(OUT/"phase4_8_batter_match_level_validation.csv",index=False)
    wa.to_csv(OUT/"phase4_8_bowler_match_level_validation.csv",index=False)
    bd.to_csv(OUT/"phase4_8_batter_match_records.csv",index=False)
    wd.to_csv(OUT/"phase4_8_bowler_match_records.csv",index=False)
    summary={"in_scope_pressure_or_normal_regulation_deliveries":int(len(d)),
             "batter_candidates":len(ba),"bowler_candidates":len(wa),
             "batter_match_group_records":len(bd),"bowler_match_group_records":len(wd),
             "final_top10_created":False}
    (OUT/"phase4_8_summary.json").write_text(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    print(main())
