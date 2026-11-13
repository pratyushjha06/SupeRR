from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"

def main():
    bat=pd.read_csv(OUT/"phase4_6_batter_format_evidence.csv")
    bowl=pd.read_csv(OUT/"phase4_6_bowler_format_evidence.csv")
    bt=pd.read_csv(OUT/"phase4_3_batter_top20_full.csv")
    wt=pd.read_csv(OUT/"phase4_3_bowler_top20_full.csv")
    by=pd.read_csv(OUT/"phase4_5_pooled_batter_season_stability.csv")
    wy=pd.read_csv(OUT/"phase4_5_pooled_bowler_season_stability.csv")

    def build(full, fmt, years, name, altcols):
        d=full.copy()
        for c in altcols:
            d[c+"_rank"]=d[c].rank(method="min",ascending=False).astype(int)
        d=d.merge(years[["player","format_year_top10_count","best_year_rank","median_year_rank","appearances"]],
                  left_on=name,right_on="player",how="left").drop(columns="player")
        d=d.merge(fmt[[name,"format_coverage","ipl_pressure_exposure","t20i_pressure_exposure",
                       "ipl_pressure_share_pct","t20i_pressure_share_pct","ipl_format_eligible","t20i_format_eligible"]],
                  on=name,how="left")
        d["alternate_top10_count"]=d[[c+"_rank" for c in altcols]].le(10).sum(axis=1)
        def label(r):
            rank=int(r["balanced_rank"])
            priority=(r["reliability_tier"]=="stronger" and r["uncertainty_flag"]=="standard"
                      and r["alternate_top10_count"]>=2)
            if rank<=10 and priority: return "priority_for_final_review"
            if rank<=10: return "conditional_final_review"
            if r["reliability_tier"]=="stronger" and r["alternate_top10_count"]>=2:
                return "reserve_candidate"
            return "lower_priority_reserve"
        d["review_disposition"]=d.apply(label,axis=1)
        d["format_concentration_flag"]=np.where(
            d[["ipl_pressure_share_pct","t20i_pressure_share_pct"]].max(axis=1)>=80,
            "one_format_over_80pct","no_format_over_80pct")
        d["year_recurrence_flag"]=np.where(d["format_year_top10_count"].fillna(0)>=2,"repeat_format_year_top10",
            np.where(d["format_year_top10_count"].fillna(0)==1,"one_format_year_top10","no_recurrence_row_or_none"))
        return d

    b=build(bt,bat,by,"striker_name",["rating_scoring_impact","rating_survival","rating_equal"])
    w=build(wt,bowl,wy,"bowler_name",["rating_wicket_impact","rating_control","rating_equal"])
    b.to_csv(OUT/"phase4_7_batter_candidate_review.csv",index=False)
    w.to_csv(OUT/"phase4_7_bowler_candidate_review.csv",index=False)
    return {"batters":len(b),"bowlers":len(w),"final_top10_created":False}

if __name__=="__main__":
    print(main())
