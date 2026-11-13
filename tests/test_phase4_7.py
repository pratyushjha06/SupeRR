from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"

def test_candidate_review_has_full_top20_pools():
    b=pd.read_csv(OUT/"phase4_7_batter_candidate_review.csv")
    w=pd.read_csv(OUT/"phase4_7_bowler_candidate_review.csv")
    assert len(b)==20 and len(w)==20
    assert b["review_disposition"].notna().all()
    assert w["review_disposition"].notna().all()

def test_disposition_labels_are_from_documented_rubric():
    allowed={"priority_for_final_review","conditional_final_review","reserve_candidate","lower_priority_reserve"}
    for fn in ["phase4_7_batter_candidate_review.csv","phase4_7_bowler_candidate_review.csv"]:
        df=pd.read_csv(OUT/fn)
        assert set(df["review_disposition"]).issubset(allowed)

def test_no_final_top10_claimed():
    report=(ROOT/"reports"/"phase4_7_candidate_by_candidate_review.md").read_text(encoding="utf-8")
    assert "No final Unstop Top 10 has been created" in report
