
from pathlib import Path
import json, shutil
import numpy as np
import pandas as pd
from src.performance_engine import run_phase3
from src.rating_engine import build_batter_ratings, build_bowler_ratings

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
REPORTS=ROOT/"reports"

def fmt_label(row):
    return "IPL" if str(row["comp_name"]).upper().startswith("IPL ") else "T20I"

def main():
    meta=pd.read_csv(OUT/"matches_with_competition_metadata.csv")
    deliveries=pd.read_csv(OUT/"pressure_classified_deliveries.csv",low_memory=False)
    is_ipl=meta["comp_name"].astype(str).str.fullmatch(r"IPL\s+\d{4}",case=False,na=False)
    is_t20i=meta["match_format"].astype(str).str.upper().eq("T20I")
    scoped_meta=meta[is_ipl|is_t20i].copy()
    scoped_meta["analysis_format"]=np.where(
        scoped_meta["comp_name"].astype(str).str.fullmatch(r"IPL\s+\d{4}",case=False,na=False),"IPL","T20I")
    valid=set(scoped_meta.match_id)
    scoped=deliveries[deliveries.match_id.isin(valid)].copy()

    bt20=pd.read_csv(OUT/"phase4_3_batter_top20_full.csv")
    wt20=pd.read_csv(OUT/"phase4_3_bowler_top20_full.csv")
    bat_names=set(bt20.striker_name.astype(str))
    bowl_names=set(wt20.bowler_name.astype(str))
    b_rows=[]; w_rows=[]; coverage=[]
    tmp=OUT/"_phase46_runs"
    tmp.mkdir(exist_ok=True)

    for fmt in ["IPL","T20I"]:
        ids=set(scoped_meta.loc[scoped_meta.analysis_format.eq(fmt),"match_id"])
        part=scoped[scoped.match_id.isin(ids)].copy()
        td=tmp/fmt
        td.mkdir(exist_ok=True); (td/"reports").mkdir(exist_ok=True)
        f=td/"deliveries.csv"; part.to_csv(f,index=False)
        run_phase3(f,td,td/"reports")
        bm=pd.read_csv(td/"batting_pressure_vs_normal.csv")
        wm=pd.read_csv(td/"bowling_pressure_vs_normal.csv")
        bs=pd.read_csv(td/"batting_sample_size_report.csv")
        ws=pd.read_csv(td/"bowling_sample_size_report.csv")
        bc=pd.read_csv(td/"batting_match_consistency.csv")
        wc=pd.read_csv(td/"bowling_match_consistency.csv")
        br,_=build_batter_ratings(bm,bs,bc)
        wr,_=build_bowler_ratings(wm,ws,wc)
        br=br[br.striker_name.astype(str).isin(bat_names)].copy()
        wr=wr[wr.bowler_name.astype(str).isin(bowl_names)].copy()
        for _,r in br.iterrows():
            b_rows.append({
                "format":fmt,"player":r.striker_name,"eligible_in_format":bool(r.eligible),
                "pressure_balls":r.get("pressure_balls",np.nan),
                "normal_balls":r.get("normal_balls_faced",np.nan),
                "pressure_matches":r.get("pressure_matches",np.nan),
                "normal_matches":r.get("normal_exposure_matches",np.nan),
                "pressure_sr":r.get("pressure_strike_rate",np.nan),
                "normal_sr":r.get("normal_strike_rate",np.nan),
                "sr_delta":r.get("strike_rate_delta",np.nan),
                "pressure_dot_pct":r.get("pressure_dot_ball_pct",np.nan),
                "normal_dot_pct":r.get("normal_dot_ball_pct",np.nan),
                "dot_pct_delta":r.get("dot_ball_pct_delta",np.nan),
                "pressure_boundary_pct":r.get("pressure_boundary_pct",np.nan),
                "normal_boundary_pct":r.get("normal_boundary_pct",np.nan),
                "boundary_pct_delta":r.get("boundary_pct_delta",np.nan),
                "pressure_dismissal_rate_pct":r.get("pressure_dismissal_rate_pct",np.nan),
                "normal_dismissal_rate_pct":r.get("normal_dismissal_rate_pct",np.nan),
                "dismissal_rate_delta":r.get("dismissal_rate_pct_delta",np.nan),
                "format_rating":r.get("rating_balanced",np.nan),
                "format_reliability_tier":r.get("reliability_tier","not_eligible"),
            })
        for _,r in wr.iterrows():
            w_rows.append({
                "format":fmt,"player":r.bowler_name,"eligible_in_format":bool(r.eligible),
                "pressure_legal_balls":r.get("pressure_legal_balls",np.nan),
                "normal_legal_balls":r.get("normal_legal_balls",np.nan),
                "pressure_matches":r.get("pressure_matches",np.nan),
                "normal_matches":r.get("normal_exposure_matches",np.nan),
                "pressure_economy":r.get("pressure_economy",np.nan),
                "normal_economy":r.get("normal_economy",np.nan),
                "economy_delta":r.get("economy_delta",np.nan),
                "pressure_dot_pct":r.get("pressure_dot_ball_pct",np.nan),
                "normal_dot_pct":r.get("normal_dot_ball_pct",np.nan),
                "dot_pct_delta":r.get("dot_ball_pct_delta",np.nan),
                "pressure_wickets_per_over":r.get("pressure_wickets_per_over",np.nan),
                "normal_wickets_per_over":r.get("normal_wickets_per_over",np.nan),
                "wickets_per_over_delta":r.get("wickets_per_over_delta",np.nan),
                "pressure_boundary_pct":r.get("pressure_boundary_conceded_pct",np.nan),
                "normal_boundary_pct":r.get("normal_boundary_conceded_pct",np.nan),
                "boundary_pct_delta":r.get("boundary_conceded_pct_delta",np.nan),
                "format_rating":r.get("rating_balanced",np.nan),
                "format_reliability_tier":r.get("reliability_tier","not_eligible"),
            })
        shutil.rmtree(td,ignore_errors=True)

    b=pd.DataFrame(b_rows); w=pd.DataFrame(w_rows)
    # Pivot into a candidate-level format evidence view; use actual exposure, not rating averages.
    def summarize(df, role, exposure_col, normal_col):
        records=[]
        for player,g in df.groupby("player"):
            g=g.set_index("format")
            ip=g.loc["IPL"] if "IPL" in g.index else pd.Series(dtype=object)
            ti=g.loc["T20I"] if "T20I" in g.index else pd.Series(dtype=object)
            ipx=float(ip.get(exposure_col,0) or 0); tix=float(ti.get(exposure_col,0) or 0)
            ipn=float(ip.get(normal_col,0) or 0); tin=float(ti.get(normal_col,0) or 0)
            total=ipx+tix
            meaningful=sum([ipx>=30, tix>=30])
            rec={"player":player,"role":role,
                 "ipl_pressure_exposure":ipx,"t20i_pressure_exposure":tix,
                 "ipl_normal_exposure":ipn,"t20i_normal_exposure":tin,
                 "ipl_pressure_share_pct":100*ipx/total if total else np.nan,
                 "t20i_pressure_share_pct":100*tix/total if total else np.nan,
                 "formats_with_30plus_pressure_balls":meaningful,
                 "format_coverage":"both_formats_30plus" if meaningful==2 else ("single_format_30plus" if meaningful==1 else "below_30_in_each_format"),
                 "ipl_format_eligible":bool(ip.get("eligible_in_format",False)),
                 "t20i_format_eligible":bool(ti.get("eligible_in_format",False)),
                 "ipl_format_tier":ip.get("format_reliability_tier","no_exposure"),
                 "t20i_format_tier":ti.get("format_reliability_tier","no_exposure")}
            # Attach the per-format metric deltas for transparent review.
            for c in df.columns:
                if c in ["player","format","eligible_in_format",exposure_col,normal_col]: continue
                rec["ipl_"+c]=ip.get(c,np.nan)
                rec["t20i_"+c]=ti.get(c,np.nan)
            records.append(rec)
        return pd.DataFrame(records)

    bs=summarize(b,"batter","pressure_balls","normal_balls")
    ws=summarize(w,"bowler","pressure_legal_balls","normal_legal_balls")
    # Preserve pooled top-20 order and append format diagnostics.
    bs=bt20[["balanced_rank","striker_name","rating_balanced","reliability_tier","uncertainty_flag"]].merge(
        bs,left_on="striker_name",right_on="player",how="left").drop(columns=["player"])
    ws=wt20[["balanced_rank","bowler_name","rating_balanced","reliability_tier","uncertainty_flag"]].merge(
        ws,left_on="bowler_name",right_on="player",how="left").drop(columns=["player"])
    bs.to_csv(OUT/"phase4_6_batter_format_evidence.csv",index=False)
    ws.to_csv(OUT/"phase4_6_bowler_format_evidence.csv",index=False)
    b.to_csv(OUT/"phase4_6_batter_format_metrics_long.csv",index=False)
    w.to_csv(OUT/"phase4_6_bowler_format_metrics_long.csv",index=False)

    # Diagnostics: do not average independently standardized format ratings.
    def conclusions(df,role):
        both=int((df.formats_with_30plus_pressure_balls==2).sum())
        single=int((df.formats_with_30plus_pressure_balls==1).sum())
        neither=int((df.formats_with_30plus_pressure_balls==0).sum())
        return {"role":role,"top20_candidates":len(df),"both_formats_30plus":both,
                "single_format_30plus":single,"below_30_each_format":neither}
    summary={"method":"pooled score remains primary; format splits are diagnostics only",
             "scope_matches":int(scoped_meta.match_id.nunique()),
             "scope_deliveries":int(len(scoped)),
             "excluded_deliveries":int(len(deliveries)-len(scoped)),
             "batter_top20":conclusions(bs,"batter"),
             "bowler_top20":conclusions(ws,"bowler"),
             "rating_aggregation":"No arithmetic averaging of IPL and T20I ratings; robust z-scores are recalculated within each subset and are not on a common scale.",
             "final_top10_created":False}
    (OUT/"phase4_6_summary.json").write_text(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    print(json.dumps(main(),indent=2))
