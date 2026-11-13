from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"

def main():
    bt=pd.read_csv(OUT/"phase4_3_batter_top20_full.csv")
    wt=pd.read_csv(OUT/"phase4_3_bowler_top20_full.csv")
    ba=pd.read_csv(OUT/"phase4_8_batter_match_level_validation.csv")
    wa=pd.read_csv(OUT/"phase4_8_bowler_match_level_validation.csv")
    bat=bt.merge(ba[["striker_id","match_median_favourable_components","match_level_sample_flag",
        "match_median_sr_delta","match_median_dot_pct_delta","match_median_boundary_pct_delta",
        "match_median_dismissal_rate_delta","pressure_matches","normal_matches"]],
        on="striker_id",how="left",suffixes=("","_match"))
    bowl=wt.merge(wa[["bowler_id","match_median_favourable_components","match_level_sample_flag",
        "match_median_economy_delta","match_median_dot_pct_delta","match_median_wickets_per_over_delta",
        "match_median_boundary_pct_delta","pressure_matches","normal_matches"]],
        on="bowler_id",how="left",suffixes=("","_match"))
    def cutoff(df,name,role,alts):
        cut=df.loc[df.balanced_rank.eq(10)].iloc[0]
        rows=[]
        for _,r in df[df.balanced_rank.ge(11)].iterrows():
            x={"role":role,"omitted_rank":int(r.balanced_rank),"omitted_candidate":r[name],
               "cutoff_candidate":cut[name],"balanced_rating_gap_vs_cutoff":float(cut.rating_balanced-r.rating_balanced),
               "omitted_reliability":r.reliability_tier,"cutoff_reliability":cut.reliability_tier,
               "omitted_uncertainty":r.uncertainty_flag,"cutoff_uncertainty":cut.uncertainty_flag,
               "omitted_match_favourable":r.match_median_favourable_components,
               "cutoff_match_favourable":cut.match_median_favourable_components,
               "omitted_pressure_matches":int(r.pressure_matches_match),
               "omitted_normal_matches":int(r.normal_matches)}
            for a in alts: x[f"{a}_gap_vs_cutoff"]=float(cut[a]-r[a])
            rows.append(x)
        return pd.DataFrame(rows).sort_values("balanced_rating_gap_vs_cutoff")
    b=cutoff(bat,"striker_name","batter",["rating_scoring_impact","rating_survival","rating_equal"])
    w=cutoff(bowl,"bowler_name","bowler",["rating_wicket_impact","rating_control","rating_equal"])
    b.to_csv(OUT/"phase4_9_batter_cutline_challengers.csv",index=False)
    w.to_csv(OUT/"phase4_9_bowler_cutline_challengers.csv",index=False)
    return {"batter_challengers":len(b),"bowler_challengers":len(w),
            "batter_cutoff_gap":float(b.iloc[0].balanced_rating_gap_vs_cutoff),
            "bowler_cutoff_gap":float(w.iloc[0].balanced_rating_gap_vs_cutoff),
            "final_top10_created":False}
if __name__=="__main__":
    print(main())
