from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from .data_loader import load_dataset

def run_exploration(data_dir="data/raw", output_dir="outputs"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    d = load_dataset(data_dir)
    balls, matches, comps = d["ball_by_ball"], d["matches"], d["competitions"]

    # Competition metadata joined to match records; validate relationship.
    match_meta = matches.merge(
        comps[["comp_id", "comp_name", "match_format", "season"]],
        on="comp_id", how="left", validate="many_to_one"
    )
    match_meta.to_csv(out / "matches_with_competition_metadata.csv", index=False)

    # Competition inclusion is explicit and configurable. Preserve all formats
    # in the Phase 1 audit; do not silently discard domestic T20 competitions.
    comp_profile = comps.groupby(["match_format", "season"], dropna=False).agg(
        competition_count=("comp_id", "nunique"),
        competition_names=("comp_name", lambda x: " | ".join(sorted(set(map(str, x)))))
    ).reset_index()
    comp_profile.to_csv(out / "competition_profile.csv", index=False)

    # Descriptive participation tables use delivery-row counts only. They are
    # intentionally NOT called balls faced/overs until extras semantics are audited.
    batter_rows = balls.groupby(["striker_id", "striker_name"], dropna=False).agg(
        delivery_rows=("match_id", "size"),
        matches=("match_id", "nunique"),
        recorded_runs_sum=("runs", "sum"),
        fours_flagged=("is_four", "sum"),
        sixes_flagged=("is_six", "sum"),
        dismissal_events_as_striker=("is_wicket", "sum"),
    ).reset_index().sort_values(["delivery_rows", "recorded_runs_sum"], ascending=False)
    bowler_rows = balls.groupby(["bowler_id", "bowler_name"], dropna=False).agg(
        delivery_rows=("match_id", "size"),
        matches=("match_id", "nunique"),
        recorded_runs_field_sum=("runs", "sum"),
        wicket_events_on_delivery=("is_wicket", "sum"),
    ).reset_index().sort_values(["delivery_rows", "matches"], ascending=False)
    batter_rows.to_csv(out / "batter_participation_eda.csv", index=False)
    bowler_rows.to_csv(out / "bowler_participation_eda.csv", index=False)

    innings = balls.groupby("innings").agg(
        delivery_rows=("match_id", "size"),
        matches=("match_id", "nunique"),
        mean_recorded_runs=("runs", "mean"),
        wicket_flag_rows=("is_wicket", "sum")
    ).reset_index()
    innings.to_csv(out / "innings_profile.csv", index=False)

    extras = balls["extras_type"].fillna("<no extras label>").value_counts().rename_axis("extras_type").reset_index(name="delivery_rows")
    extras.to_csv(out / "extras_type_profile.csv", index=False)

    # Small, readable figures for the report; matplotlib defaults intentionally retained.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    comps["match_format"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Competition records by match format")
    ax.set_xlabel("Match format")
    ax.set_ylabel("Number of competition records")
    fig.tight_layout()
    fig.savefig(out / "competition_formats.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    comps["season"].astype(str).value_counts().sort_index().plot(kind="bar", ax=ax)
    ax.set_title("Competition records by season")
    ax.set_xlabel("Season")
    ax.set_ylabel("Number of competition records")
    fig.tight_layout()
    fig.savefig(out / "competition_seasons.png", dpi=160)
    plt.close(fig)

    return {
        "unique_batters_in_delivery_data": int(balls.striker_id.nunique()),
        "unique_bowlers_in_delivery_data": int(balls.bowler_id.nunique()),
        "unique_players_in_playing_eleven": int(d["playing_eleven"].player_id.nunique()),
        "unique_players_in_competition_mapping": int(d["competition_team_player_mapping"].player_id.nunique()),
        "top_batter_delivery_rows": batter_rows.head(10).to_dict("records"),
        "top_bowler_delivery_rows": bowler_rows.head(10).to_dict("records"),
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_exploration(), indent=2, default=str))
