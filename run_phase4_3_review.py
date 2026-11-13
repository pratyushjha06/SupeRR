from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"

def main():
    bat = pd.read_csv(OUT / "batter_ratings_all.csv")
    bowl = pd.read_csv(OUT / "bowler_ratings_all.csv")
    sens = pd.read_csv(OUT / "ranking_sensitivity.csv")
    summary = json.loads((OUT / "phase4_summary.json").read_text(encoding="utf-8"))

    def eligible(df):
        return df[df["eligible"].fillna(False)].copy()

    def rank(df, score):
        return df.sort_values(score, ascending=False).reset_index(drop=True)

    def make_top(df, score, name, filename):
        result = rank(eligible(df), score).head(20).copy()
        result.insert(0, "balanced_rank", range(1, len(result) + 1))
        result.to_csv(OUT / filename, index=False)
        return result

    make_top(bat, "rating_balanced", "striker_name", "phase4_3_batter_top20_full.csv")
    make_top(bowl, "rating_balanced", "bowler_name", "phase4_3_bowler_top20_full.csv")
    for df, role, score, filename in [
        (bat, "batter", "rating_balanced", "phase4_3_batter_stronger_only.csv"),
        (bowl, "bowler", "rating_balanced", "phase4_3_bowler_stronger_only.csv"),
    ]:
        shortlist = rank(eligible(df).query("reliability_tier == 'stronger'"), score).head(20)
        shortlist.to_csv(OUT / filename, index=False)

    result = {
        "phase": "4.3",
        "status": "provisional_review_only",
        "final_unstop_top10_created": False,
        "scope": summary.get("competition_scope"),
        "eligible_batters": int(eligible(bat).shape[0]),
        "eligible_bowlers": int(eligible(bowl).shape[0]),
        "stronger_batters": int((eligible(bat)["reliability_tier"] == "stronger").sum()),
        "stronger_bowlers": int((eligible(bowl)["reliability_tier"] == "stronger").sum()),
        "sensitivity_rows": int(sens.shape[0]),
    }
    (OUT / "phase4_3_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
