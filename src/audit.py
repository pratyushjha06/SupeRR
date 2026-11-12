from pathlib import Path
import json
import pandas as pd
from .data_loader import load_dataset, FILES

KEYS = {
    "competitions": ["comp_id"],
    "matches": ["match_id"],
    "ball_by_ball": None,
    "teams": ["comp_id", "team_id"],
    "competition_team_player_mapping": ["comp_id", "team_id", "player_id"],
    "playing_eleven": ["match_id", "team_id", "player_id"],
}

def _json_safe(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value

def run_audit(data_dir="data/raw", output_dir="outputs"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = load_dataset(data_dir)
    tables = {}
    for name, df in data.items():
        key_cols = KEYS.get(name)
        tables[name] = {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
            "dtypes": {c: str(t) for c, t in df.dtypes.items()},
            "missing": {
                c: {"count": int(n), "percent": round(float(n / len(df) * 100), 3) if len(df) else 0}
                for c, n in df.isna().sum().items() if n > 0
            },
            "exact_duplicate_rows": int(df.duplicated().sum()),
            "key_columns_checked": key_cols,
            "duplicate_key_rows": (
                int(df.duplicated(key_cols).sum()) if key_cols and all(c in df for c in key_cols) else None
            ),
        }
        pd.DataFrame({
            "column": df.columns,
            "dtype": [str(x) for x in df.dtypes],
            "missing_count": [int(x) for x in df.isna().sum()],
            "missing_percent": [round(float(x / len(df) * 100), 3) if len(df) else 0 for x in df.isna().sum()],
            "unique_values": [int(df[c].nunique(dropna=True)) for c in df.columns],
        }).to_csv(out / f"{name}_column_profile.csv", index=False)

    matches = data["matches"]
    balls = data["ball_by_ball"]
    comps = data["competitions"]
    playing = data["playing_eleven"]
    mapping = data["competition_team_player_mapping"]

    match_ids = set(matches["match_id"].dropna())
    ball_match_ids = set(balls["match_id"].dropna())
    comp_ids = set(comps["comp_id"].dropna())
    match_comp_ids = set(matches["comp_id"].dropna())

    coverage = {
        "matches_in_matches_file": int(matches["match_id"].nunique()),
        "matches_with_ball_by_ball": int(balls["match_id"].nunique()),
        "matches_without_ball_by_ball": int(len(match_ids - ball_match_ids)),
        "ball_by_ball_match_ids_not_in_matches": int(len(ball_match_ids - match_ids)),
        "match_competition_ids_missing_from_competitions": int(len(match_comp_ids - comp_ids)),
        "playing_eleven_match_ids_not_in_matches": int(len(set(playing.match_id) - match_ids)),
        "mapping_competition_ids_not_in_competitions": int(len(set(mapping.comp_id) - comp_ids)),
    }

    comp_join = matches.merge(
        comps[["comp_id", "comp_name", "match_format", "season"]],
        on="comp_id", how="left", validate="many_to_one"
    )
    format_counts = comps["match_format"].value_counts(dropna=False).to_dict()
    season_counts = comps["season"].astype(str).value_counts(dropna=False).sort_index().to_dict()
    match_format_counts = comp_join["match_format"].value_counts(dropna=False).to_dict()

    summary = {
        "dataset_name": "SupeRR Selector Season 2 supplied data pack",
        "tables": tables,
        "coverage_checks": coverage,
        "competition_format_counts_competition_rows": {str(k): int(v) for k, v in format_counts.items()},
        "competition_season_counts_competition_rows": {str(k): int(v) for k, v in season_counts.items()},
        "match_counts_by_format": {str(k): int(v) for k, v in match_format_counts.items()},
        "date_range": {
            "min": str(matches["match_date"].min()),
            "max": str(matches["match_date"].max())
        },
        "ball_by_ball": {
            "unique_matches": int(balls.match_id.nunique()),
            "innings_values": {str(k): int(v) for k, v in balls.innings.value_counts(dropna=False).sort_index().items()},
            "extras_type_counts": {str(k): int(v) for k, v in balls.extras_type.fillna("<NA>").value_counts().items()},
            "dismissal_type_counts": {str(k): int(v) for k, v in balls.dismissal_type.fillna("<NA>").value_counts().items()},
            "runs_field_min": _json_safe(balls.runs.min()),
            "runs_field_max": _json_safe(balls.runs.max()),
        },
        "notes": [
            "Missing values are profiled, not automatically treated as errors; several fields are optional by design.",
            "No player rankings or pressure labels are generated in Phase 1.",
            "Delivery-row counts are not yet treated as legal balls or balls faced.",
            "Run and extras fields require semantic validation before deriving batting/bowling rates."
        ]
    }
    with open(out / "dataset_audit.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    comp_join.groupby(["match_format", "season"], dropna=False).agg(
        competition_count=("comp_id", "nunique"),
        match_count=("match_id", "nunique")
    ).reset_index().to_csv(out / "matches_by_format_season.csv", index=False)
    return summary

if __name__ == "__main__":
    result = run_audit()
    print(json.dumps({
        "tables": {k: {"rows": v["rows"], "columns": v["columns"]} for k,v in result["tables"].items()},
        "coverage_checks": result["coverage_checks"],
        "date_range": result["date_range"]
    }, indent=2))
