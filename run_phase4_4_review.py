from pathlib import Path
import json
import shutil
import pandas as pd
from src.performance_engine import run_phase3
from src.rating_engine import build_batter_ratings, build_bowler_ratings

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

def top10(df, name, fmt, role):
    x = df[df["eligible"].fillna(False)].sort_values("rating_balanced", ascending=False).head(10).copy()
    x.insert(0, "rank", range(1, len(x) + 1))
    x.insert(0, "format", fmt)
    x.insert(2, "player", x[name])
    return x[["format", "rank", "player", "rating_balanced", "reliability_tier", "uncertainty_flag"]]

def main():
    meta = pd.read_csv(OUT / "matches_with_competition_metadata.csv",
                       usecols=["match_id", "comp_name", "match_format"])
    raw = pd.read_csv(OUT / "pressure_classified_deliveries.csv", low_memory=False)
    ipl_mask = meta["comp_name"].astype(str).str.fullmatch(r"IPL\s+\d{4}", case=False, na=False)
    t20i_mask = meta["match_format"].astype(str).str.upper().eq("T20I")
    scope_ids = set(meta.loc[ipl_mask | t20i_mask, "match_id"])
    raw = raw[raw["match_id"].isin(scope_ids)].copy()

    batter_tables, bowler_tables, summaries = [], [], {}
    for fmt, mask in [("IPL", ipl_mask), ("T20I", t20i_mask)]:
        ids = set(meta.loc[mask, "match_id"])
        part = raw[raw["match_id"].isin(ids)].copy()
        temp = ROOT / "outputs" / f"_phase44_{fmt.lower()}"
        temp.mkdir(parents=True, exist_ok=True)
        report_temp = temp / "reports"
        report_temp.mkdir(exist_ok=True)
        source = temp / "deliveries.csv"
        part.to_csv(source, index=False)
        run_phase3(source, temp, report_temp)

        bm = pd.read_csv(temp / "batting_pressure_vs_normal.csv")
        wm = pd.read_csv(temp / "bowling_pressure_vs_normal.csv")
        bs = pd.read_csv(temp / "batting_sample_size_report.csv")
        ws = pd.read_csv(temp / "bowling_sample_size_report.csv")
        bc = pd.read_csv(temp / "batting_match_consistency.csv")
        wc = pd.read_csv(temp / "bowling_match_consistency.csv")
        br, _ = build_batter_ratings(bm, bs, bc)
        wr, _ = build_bowler_ratings(wm, ws, wc)
        batter_tables.append(top10(br, "striker_name", fmt, "batter"))
        bowler_tables.append(top10(wr, "bowler_name", fmt, "bowler"))
        summaries[fmt] = {
            "deliveries": int(len(part)),
            "matches": int(len(ids)),
            "eligible_batters": int(br["eligible"].sum()),
            "eligible_bowlers": int(wr["eligible"].sum()),
        }
        shutil.rmtree(temp, ignore_errors=True)

    bat = pd.concat(batter_tables, ignore_index=True)
    bowl = pd.concat(bowler_tables, ignore_index=True)
    bat.to_csv(OUT / "phase4_4_format_batter_top10.csv", index=False)
    bowl.to_csv(OUT / "phase4_4_format_bowler_top10.csv", index=False)
    summary = {
        "phase": "4.4",
        "status": "exploratory_format_split_audit_only",
        "final_unstop_top10_created": False,
        "formats": summaries,
        "ipl_t20i_top10_overlap_batters": int(
            len(set(bat.loc[bat["format"] == "IPL", "player"]) &
                set(bat.loc[bat["format"] == "T20I", "player"]))),
        "ipl_t20i_top10_overlap_bowlers": int(
            len(set(bowl.loc[bowl["format"] == "IPL", "player"]) &
                set(bowl.loc[bowl["format"] == "T20I", "player"]))),
        "warning": "Format-specific robust z-scores are recalculated within each format; scores are not directly comparable across formats."
    }
    (OUT / "phase4_4_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
