import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"

def test_phase46_summary_is_diagnostic_only():
    s=json.loads((OUT/"phase4_6_summary.json").read_text())
    assert s["final_top10_created"] is False
    assert s["scope_matches"] == 853
    assert s["scope_deliveries"] == 194014

def test_top20_format_evidence_has_twenty_candidates_each():
    b=pd.read_csv(OUT/"phase4_6_batter_format_evidence.csv")
    w=pd.read_csv(OUT/"phase4_6_bowler_format_evidence.csv")
    assert len(b)==20 and len(w)==20
    assert b["format_coverage"].notna().all()
    assert w["format_coverage"].notna().all()

def test_format_shares_sum_to_100():
    for filename in ["phase4_6_batter_format_evidence.csv","phase4_6_bowler_format_evidence.csv"]:
        df=pd.read_csv(OUT/filename)
        total=df["ipl_pressure_share_pct"]+df["t20i_pressure_share_pct"]
        assert ((total-100).abs()<1e-6).all()
