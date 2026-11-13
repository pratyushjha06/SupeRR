from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"

def test_cutline_challengers_cover_ranks_11_to_20():
    for fn in ["phase4_9_batter_cutline_challengers.csv","phase4_9_bowler_cutline_challengers.csv"]:
        d=pd.read_csv(OUT/fn)
        assert d["omitted_rank"].tolist()==list(range(11,21))

def test_bowler_cutline_is_near_tie():
    d=pd.read_csv(OUT/"phase4_9_bowler_cutline_challengers.csv")
    sai=d.loc[d.omitted_candidate.eq("Sai Kishore")].iloc[0]
    assert abs(sai["balanced_rating_gap_vs_cutoff"])<0.001

def test_batter_cutline_is_close():
    d=pd.read_csv(OUT/"phase4_9_batter_cutline_challengers.csv")
    dasun=d.loc[d.omitted_candidate.eq("Dasun Shanaka")].iloc[0]
    assert dasun["balanced_rating_gap_vs_cutoff"]<0.02

def test_no_final_top10_created():
    report=(ROOT/"reports"/"phase4_9_final_cutline_challenge.md").read_text(encoding="utf-8")
    assert "No final Unstop Top 10 has been created" in report
