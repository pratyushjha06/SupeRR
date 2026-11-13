from pathlib import Path
import json
import shutil
import pandas as pd
from src.performance_engine import run_phase3
from src.rating_engine import build_batter_ratings, build_bowler_ratings

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

def main():
    meta = pd.read_csv(OUT / "matches_with_competition_metadata.csv")
    deliveries = pd.read_csv(OUT / "pressure_classified_deliveries.csv", low_memory=False)

    ipl = meta["comp_name"].astype(str).str.fullmatch(r"IPL\s+\d{4}", case=False, na=False)
    t20i = meta["match_format"].astype(str).str.upper().eq("T20I")
    scoped_meta = meta[ipl | t20i].copy()
    scoped_meta["analysis_format"] = "T20I"
    scoped_meta.loc[ipl.loc[scoped_meta.index], "analysis_format"] = "IPL"
    scoped_meta["analysis_year"] = pd.to_datetime(
        scoped_meta["match_date"], errors="coerce"
    ).dt.year.astype("Int64").astype(str)
    scoped_meta.loc[scoped_meta["analysis_format"].eq("IPL"), "analysis_year"] = (
        scoped_meta.loc[scoped_meta["analysis_format"].eq("IPL"), "comp_name"]
        .str.extract(r"(\d{4})", expand=False)
    )

    valid_ids = set(scoped_meta["match_id"])
    scoped = deliveries[deliveries["match_id"].isin(valid_ids)].copy()

    summary_rows, batter_rows, bowler_rows = [], [], []
    temp_root = OUT / "_phase45_runs"
    temp_root.mkdir(exist_ok=True)

    for (fmt, year), group in scoped_meta.groupby(["analysis_format", "analysis_year"]):
        ids = set(group["match_id"])
        part = scoped[scoped["match_id"].isin(ids)].copy()
        temp = temp_root / f"{fmt}_{year}"
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

        br = br[br["eligible"].fillna(False)].sort_values("rating_balanced", ascending=False).copy()
        wr = wr[wr["eligible"].fillna(False)].sort_values("rating_balanced", ascending=False).copy()
        br["rank"] = range(1, len(br) + 1)
        wr["rank"] = range(1, len(wr) + 1)

        summary_rows.append({
            "format": fmt, "calendar_year": year, "matches": len(ids),
            "deliveries": len(part), "eligible_batters": len(br),
            "eligible_bowlers": len(wr),
            "batter_top10_complete": len(br) >= 10,
            "bowler_top10_complete": len(wr) >= 10,
        })
        for _, row in br.iterrows():
            batter_rows.append({
                "format": fmt, "calendar_year": year, "rank": int(row["rank"]),
                "player": row["striker_name"], "rating": row["rating_balanced"],
                "reliability_tier": row["reliability_tier"],
                "pressure_balls": row["pressure_balls"],
                "normal_balls": row["normal_balls_faced"],
                "pressure_matches": row["pressure_matches"],
            })
        for _, row in wr.iterrows():
            bowler_rows.append({
                "format": fmt, "calendar_year": year, "rank": int(row["rank"]),
                "player": row["bowler_name"], "rating": row["rating_balanced"],
                "reliability_tier": row["reliability_tier"],
                "pressure_balls": row["pressure_legal_balls"],
                "normal_balls": row["normal_legal_balls"],
                "pressure_matches": row["pressure_matches"],
            })
        shutil.rmtree(temp, ignore_errors=True)

    summary_df = pd.DataFrame(summary_rows)
    bat_df = pd.DataFrame(batter_rows)
    bowl_df = pd.DataFrame(bowler_rows)
    summary_df.to_csv(OUT / "phase4_5_format_year_summary.csv", index=False)
    bat_df[bat_df["rank"] <= 10].to_csv(OUT / "phase4_5_batter_year_top10.csv", index=False)
    bowl_df[bowl_df["rank"] <= 10].to_csv(OUT / "phase4_5_bowler_year_top10.csv", index=False)
    bat_df.to_csv(OUT / "phase4_5_all_batter_year_ranks.csv", index=False)
    bowl_df.to_csv(OUT / "phase4_5_all_bowler_year_ranks.csv", index=False)

    pooled_bat = pd.read_csv(OUT / "phase4_4_batter_balanced_top10.csv")
    pooled_bowl = pd.read_csv(OUT / "phase4_4_bowler_balanced_top10.csv")

    def stability(pooled, name, yearly):
        rows = []
        for _, p in pooled.sort_values("rank").iterrows():
            sub = yearly[yearly["player"] == p[name]]
            rows.append({
                "pooled_rank": int(p["rank"]), "player": p[name],
                "pooled_tier": p["reliability_tier"],
                "format_year_buckets_eligible": int((yearly["player"] == p[name]).sum()),
                "format_year_top10_count": int((sub["rank"] <= 10).sum()),
                "best_year_rank": int(sub["rank"].min()) if len(sub) else None,
                "median_year_rank": float(sub["rank"].median()) if len(sub) else None,
                "appearances": "; ".join(
                    f"{r.format} {r.calendar_year}: #{int(r.rank)}"
                    for r in sub[sub["rank"] <= 10].itertuples(index=False)
                ) or "No format-year Top 10 appearance",
            })
        return pd.DataFrame(rows)

    bs = stability(pooled_bat, "striker_name", bat_df)
    ws = stability(pooled_bowl, "bowler_name", bowl_df)
    bs.to_csv(OUT / "phase4_5_pooled_batter_season_stability.csv", index=False)
    ws.to_csv(OUT / "phase4_5_pooled_bowler_season_stability.csv", index=False)

    result = {
        "phase": "4.5",
        "status": "format_season_robustness_analysis_only",
        "final_unstop_top10_created": False,
        "season_grouping": "IPL competition year; T20I calendar year",
        "format_year_groups": len(summary_df),
        "t20i_years_without_full_batter_top10": summary_df[
            (summary_df["format"] == "T20I") & (~summary_df["batter_top10_complete"])
        ]["calendar_year"].tolist(),
        "pooled_batter_top10_recurrence": bs[["player", "format_year_top10_count"]].to_dict("records"),
        "pooled_bowler_top10_recurrence": ws[["player", "format_year_top10_count"]].to_dict("records"),
        "warning": "Year/format scores are re-standardized within each subset and are not directly comparable across subsets."
    }
    (OUT / "phase4_5_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    shutil.rmtree(temp_root, ignore_errors=True)

if __name__ == "__main__":
    main()
