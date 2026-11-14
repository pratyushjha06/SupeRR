from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"

def test_cutline_challengers_cover_ranks_11_to_20():
    for fn in ["phase4_9_batter_cutline_challengers.csv","phase4_9_bowler_cutline_challengers.csv"]:
        d=pd.read_csv(OUT/fn)
        assert d["omitted_rank"].tolist()==list(range(11,21))

def test_recomputed_bowler_cutline_matches_leakage_corrected_analysis():
    d=pd.read_csv(OUT/"phase4_9_bowler_cutline_challengers.csv")
    row=d.loc[d.omitted_rank.eq(11)].iloc[0]
    assert row["cutoff_candidate"] == "Shardul Thakur"
    assert row["omitted_candidate"] == "Jamie Overton"
    assert row["balanced_rating_gap_vs_cutoff"] > 0.001

def test_recomputed_batter_cutline_matches_leakage_corrected_analysis():
    d=pd.read_csv(OUT/"phase4_9_batter_cutline_challengers.csv")
    row=d.loc[d.omitted_rank.eq(11)].iloc[0]
    assert row["cutoff_candidate"] == "Mark Chapman"
    assert row["omitted_candidate"] == "Ryan Burl"
    assert row["balanced_rating_gap_vs_cutoff"] > 0.001

def test_no_final_top10_created():
    report=(ROOT/"reports"/"phase4_9_final_cutline_challenge.md").read_text(encoding="utf-8")
    assert "No final Unstop Top 10 has been created" in report
