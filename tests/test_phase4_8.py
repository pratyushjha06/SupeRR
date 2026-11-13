from pathlib import Path
import pandas as pd, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs"

def test_phase48_has_top15_candidates_each_role():
    assert len(pd.read_csv(OUT/"phase4_8_batter_match_level_validation.csv"))==15
    assert len(pd.read_csv(OUT/"phase4_8_bowler_match_level_validation.csv"))==15

def test_match_level_records_include_both_groups():
    for fn in ["phase4_8_batter_match_records.csv","phase4_8_bowler_match_records.csv"]:
        d=pd.read_csv(OUT/fn)
        assert set(d["pressure_group"])=={"pressure","normal"}

def test_no_final_top10_created():
    s=json.loads((OUT/"phase4_8_summary.json").read_text())
    assert s["final_top10_created"] is False
