
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ILLEGAL_EXTRA_TYPES = {"wide", "overstep"}
SUPER_OVER_INNINGS = {3, 4}

def _clean_extra_type(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.lower()

def inspect_scoring_semantics(ball: pd.DataFrame) -> dict:
    """Summarize observed scoring fields; no undocumented field assumptions are hidden."""
    extras = ball.assign(extras_type_norm=_clean_extra_type(ball["extras_type"]))
    extra_profile = (
        extras.groupby("extras_type_norm", dropna=False)
        .agg(
            deliveries=("match_id", "size"),
            batter_runs=("runs", "sum"),
            extras1_runs=("extras1_runs", "sum"),
            extras2_runs=("extras_2_runs", "sum"),
            wicket_rows=("is_wicket", "sum"),
        ).reset_index()
    )
    wicket_types = (
        ball.loc[ball["is_wicket"].astype(bool), "dismissal_type"]
        .fillna("MISSING").value_counts().to_dict()
    )
    return {
        "runs_field_observation": "Observed values are 0–6 and can coexist with extras; treated as batter runs for this model.",
        "extras1_observation": "Observed as a primary extra component; added to runs when reconstructing team total.",
        "extras2_observation": "Observed as a second extra component, including some Overstep/other rows; added to extras1 and runs for team total.",
        "illegal_delivery_types_observed": ["wide", "Overstep"],
        "illegal_delivery_rule": "wide and Overstep do not consume a legal ball; this is an explicit modelling interpretation of observed extras_type values.",
        "wicket_flag_observation": "is_wicket is the recorded dismissal flag. Wicket losses are counted from this flag; dismissal types are retained for later bowler-credit analysis.",
        "innings_observed": sorted(int(x) for x in ball["innings"].dropna().unique()),
        "super_over_rule": "Innings 3 and 4 are excluded from regulation-innings pressure classification and retained with is_super_over=True.",
        "wicket_types": {str(k): int(v) for k, v in wicket_types.items()},
        "extras_profile": extra_profile.to_dict(orient="records"),
        "caveat": "These are dataset-observed field patterns, not a substitute for the provider's formal data dictionary. Validate edge cases against match scorecards before final player ratings."
    }

def _max_overs_for_innings(row: pd.Series, fmt: str, innings: int) -> float:
    field = "first_inn_revised_overs" if innings == 1 else "second_inn_revised_overs"
    revised = row.get(field, np.nan)
    if pd.notna(revised) and float(revised) > 0:
        return float(revised)
    # Dataset formats show T20/T20I only. The default is 20 overs.
    return 20.0 if fmt in {"T20", "T20I"} else 20.0

def _clamp01(x):
    return np.clip(x, 0.0, 1.0)

def build_match_state(ball: pd.DataFrame, matches: pd.DataFrame, competitions: pd.DataFrame) -> pd.DataFrame:
    required_ball = {"match_id","innings","innings_ball_num","runs","extras1_runs","extras_2_runs","is_wicket","extras_type"}
    missing = required_ball - set(ball.columns)
    if missing:
        raise ValueError(f"ball_by_ball missing required columns: {sorted(missing)}")
    b = ball.copy()
    m = matches.copy()
    c = competitions.copy()
    b["extras_type_norm"] = _clean_extra_type(b["extras_type"])
    b["is_super_over"] = b["innings"].isin(SUPER_OVER_INNINGS)
    b["batter_runs"] = pd.to_numeric(b["runs"], errors="coerce").fillna(0)
    b["extra_runs"] = (
        pd.to_numeric(b["extras1_runs"], errors="coerce").fillna(0)
        + pd.to_numeric(b["extras_2_runs"], errors="coerce").fillna(0)
    )
    b["team_runs_this_delivery"] = b["batter_runs"] + b["extra_runs"]
    b["is_legal_delivery"] = ~b["extras_type_norm"].isin(ILLEGAL_EXTRA_TYPES)
    b["wicket_event"] = b["is_wicket"].fillna(False).astype(bool)

    # Sort using supplied sequence field; over/ball are deterministic tie-breakers.
    sort_cols = ["match_id","innings","innings_ball_num"]
    for col in ["overid","over_ball_num"]:
        if col in b.columns:
            sort_cols.append(col)
    b = b.sort_values(sort_cols, kind="stable").reset_index(drop=True)

    # Merge match and competition context.
    mcols = [x for x in ["match_id","comp_id","match_date","first_inn_revised_overs","second_inn_revised_overs","revised_target","result"] if x in m.columns]
    b = b.merge(m[mcols], on="match_id", how="left", validate="many_to_one")
    b = b.merge(c[["comp_id","comp_name","match_format","season"]], on="comp_id", how="left", validate="many_to_one")
    b["match_format"] = b["match_format"].fillna("UNKNOWN")
    b["season"] = b["season"].astype("string")

    group = b.groupby(["match_id","innings"], sort=False, dropna=False)
    b["runs_before"] = group["team_runs_this_delivery"].cumsum() - b["team_runs_this_delivery"]
    b["wickets_before"] = group["wicket_event"].cumsum().astype(int) - b["wicket_event"].astype(int)
    b["legal_balls_before"] = group["is_legal_delivery"].cumsum().astype(int) - b["is_legal_delivery"].astype(int)
    b["legal_balls_after"] = b["legal_balls_before"] + b["is_legal_delivery"].astype(int)
    b["wickets_after"] = b["wickets_before"] + b["wicket_event"].astype(int)
    b["wickets_remaining"] = (10 - b["wickets_before"]).clip(lower=0)
    b["innings_max_overs"] = b.apply(lambda r: _max_overs_for_innings(r, r["match_format"], int(r["innings"])), axis=1)
    b["innings_max_legal_balls"] = (b["innings_max_overs"] * 6).astype(int)
    b["balls_remaining"] = (b["innings_max_legal_balls"] - b["legal_balls_before"]).clip(lower=0)
    b["overs_elapsed"] = b["legal_balls_before"] / 6.0
    b["current_run_rate"] = np.where(b["legal_balls_before"] > 0, b["runs_before"] * 6 / b["legal_balls_before"], 0.0)

    # Innings totals are computed from all deliveries in that innings.
    totals = b.groupby(["match_id","innings"], as_index=False).agg(
        innings_total=("team_runs_this_delivery","sum"),
        innings_wickets=("wicket_event","sum"),
        innings_legal_balls=("is_legal_delivery","sum")
    )
    first = totals[totals.innings.eq(1)][["match_id","innings_total"]].rename(columns={"innings_total":"first_innings_total"})
    b = b.merge(first, on="match_id", how="left", validate="many_to_one")
    b["target"] = np.where(
        pd.to_numeric(b["revised_target"], errors="coerce").notna(),
        pd.to_numeric(b["revised_target"], errors="coerce"),
        b["first_innings_total"] + 1
    )
    b["runs_required"] = b["target"] - b["runs_before"]
    b["required_run_rate"] = np.where(
        (b["innings"].eq(2)) & (b["balls_remaining"] > 0) & b["runs_required"].gt(0),
        b["runs_required"] * 6 / b["balls_remaining"],
        np.nan
    )
    b["rrr_minus_crr"] = b["required_run_rate"] - b["current_run_rate"]
    b["is_chase"] = b["innings"].eq(2)
    b["is_regulation_innings"] = b["innings"].isin([1,2])
    return b

def classify_pressure(state: pd.DataFrame) -> pd.DataFrame:
    """Add transparent 0-100 pressure scores for first innings and chases."""
    d = state.copy()
    d["pressure_score"] = np.nan
    d["pressure_level"] = "excluded"
    d["pressure_context"] = np.select(
        [d["is_super_over"], d["innings"].eq(1), d["innings"].eq(2)],
        ["super_over", "first_innings", "chase"],
        default="unsupported_innings"
    )

    # First innings: wickets lost, innings progress, and scoring below competition-season par.
    first_mask = d["innings"].eq(1) & ~d["is_super_over"]
    # Estimate par from median first-innings final run rate within competition and season.
    innings_totals = d.loc[first_mask].groupby(["match_id","comp_id","season"], as_index=False).agg(
        final_runs=("team_runs_this_delivery","sum"),
        legal_balls=("is_legal_delivery","sum"),
        max_balls=("innings_max_legal_balls","max")
    )
    innings_totals["final_rr"] = innings_totals["final_runs"] * 6 / innings_totals["legal_balls"].replace(0,np.nan)
    par = innings_totals.groupby(["comp_id","season"])["final_rr"].median().rename("par_run_rate").reset_index()
    d = d.merge(par, on=["comp_id","season"], how="left", validate="many_to_one")
    fallback = innings_totals["final_rr"].median()
    d["par_run_rate"] = d["par_run_rate"].fillna(fallback if pd.notna(fallback) else 8.0)

    progress = _clamp01(d["legal_balls_before"] / d["innings_max_legal_balls"].replace(0,np.nan)).fillna(0)
    wicket_pressure = _clamp01(d["wickets_before"] / 9.0)
    run_rate_deficit = _clamp01((d["par_run_rate"] - d["current_run_rate"]) / d["par_run_rate"].replace(0,np.nan)).fillna(0)
    first_score = 100 * (0.35*wicket_pressure + 0.35*progress + 0.30*run_rate_deficit)
    d.loc[first_mask,"pressure_score"] = first_score.loc[first_mask]

    # Chases: RRR intensity, wicket scarcity, time scarcity, and gap between required/current rate.
    chase_mask = d["innings"].eq(2) & ~d["is_super_over"] & d["required_run_rate"].notna()
    rrr_intensity = _clamp01((d["required_run_rate"] - 6.0) / 12.0)
    wicket_scarcity = _clamp01(d["wickets_before"] / 9.0)
    time_scarcity = _clamp01(1 - d["balls_remaining"] / d["innings_max_legal_balls"].replace(0,np.nan)).fillna(0)
    gap_intensity = _clamp01((d["rrr_minus_crr"].fillna(0) + 2.0) / 12.0)
    chase_score = 100 * (0.35*rrr_intensity + 0.25*wicket_scarcity + 0.20*time_scarcity + 0.20*gap_intensity)
    d.loc[chase_mask,"pressure_score"] = chase_score.loc[chase_mask]

    d["pressure_score"] = d["pressure_score"].clip(0,100)
    d["pressure_level"] = pd.cut(
        d["pressure_score"], bins=[-0.001,25,50,75,100.001],
        labels=["low","moderate","high","very_high"], include_lowest=True
    ).astype("string").fillna("unclassified")
    # Only regulation innings with a computable score are eligible.
    d["pressure_eligible"] = d["is_regulation_innings"] & d["pressure_score"].notna()
    return d

def run_phase2(data_dir: Path, output_dir: Path, report_dir: Path) -> dict:
    data_dir, output_dir, report_dir = Path(data_dir), Path(output_dir), Path(report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    ball = pd.read_csv(data_dir/"ball_by_ball.csv", low_memory=False)
    matches = pd.read_csv(data_dir/"matches.csv", low_memory=False)
    comps = pd.read_csv(data_dir/"competitions.csv", low_memory=False)
    semantics = inspect_scoring_semantics(ball)
    state = build_match_state(ball, matches, comps)
    classified = classify_pressure(state)

    # Keep complete file for reproducibility; also emit compact summary outputs.
    classified.to_csv(output_dir/"pressure_classified_deliveries.csv", index=False)
    classified.loc[classified["pressure_eligible"]].groupby(
        ["match_format","season","innings","pressure_level"], dropna=False
    ).agg(deliveries=("match_id","size"), matches=("match_id","nunique"),
          mean_pressure=("pressure_score","mean")).reset_index().to_csv(
              output_dir/"pressure_distribution.csv", index=False)
    classified.loc[classified["pressure_eligible"]].groupby(
        ["pressure_context","pressure_level"], dropna=False
    ).agg(deliveries=("match_id","size"), matches=("match_id","nunique"),
          mean_score=("pressure_score","mean")).reset_index().to_csv(
              output_dir/"pressure_context_summary.csv", index=False)

    # Compact, reproducible visual summary for the Phase 2 report.
    try:
        import matplotlib.pyplot as plt
        counts = classified.loc[classified["pressure_eligible"], "pressure_level"].value_counts().reindex(
            ["low", "moderate", "high", "very_high"], fill_value=0
        )
        fig, ax = plt.subplots(figsize=(8, 4.5))
        counts.plot(kind="bar", ax=ax)
        ax.set_title("Regulation Deliveries by Pressure Level")
        ax.set_xlabel("Pressure level")
        ax.set_ylabel("Delivery count")
        ax.tick_params(axis="x", rotation=0)
        fig.tight_layout()
        fig.savefig(output_dir/"pressure_level_distribution.png", dpi=160)
        plt.close(fig)
    except ImportError:
        pass

    semantics["row_count"] = int(len(ball))
    semantics["wide_rows"] = int((state["extras_type_norm"]=="wide").sum())
    semantics["overstep_rows"] = int((state["extras_type_norm"]=="overstep").sum())
    semantics["super_over_rows"] = int(state["is_super_over"].sum())
    semantics["regulation_pressure_eligible_rows"] = int(classified["pressure_eligible"].sum())
    semantics["missing_match_metadata_rows"] = int(state["comp_id"].isna().sum())
    with open(output_dir/"scoring_semantics_audit.json","w",encoding="utf-8") as f:
        json.dump(semantics,f,indent=2,default=str)

    findings = [
        "# PRESSURE-X Phase 2 — Pressure Classification",
        "",
        "## Observed scoring semantics",
        f"- Ball-by-ball rows: {len(ball):,}",
        f"- `runs` is treated as batter runs; observed values range {ball['runs'].min()}–{ball['runs'].max()}.",
        "- Team runs per delivery are reconstructed as `runs + extras1_runs + extras_2_runs`.",
        f"- Wide rows: {semantics['wide_rows']:,}; Overstep rows: {semantics['overstep_rows']:,}. Both are treated as illegal deliveries and do not consume a legal ball.",
        f"- Innings 3/4 rows (Super Overs): {semantics['super_over_rows']:,}; excluded from regulation pressure scores.",
        "- Wickets lost are reconstructed from the recorded `is_wicket` flag. Bowler-credit treatment is deferred to the bowling model.",
        "",
        "## Pressure model",
        "- First innings: 35% wicket-loss pressure, 35% innings progress, 30% scoring-rate deficit against competition-season median first-innings run rate.",
        "- Chases: 35% required-run-rate intensity, 25% wickets lost, 20% time scarcity, 20% required-vs-current run-rate gap.",
        "- Score bands: low (0–25), moderate (25–50), high (50–75), very high (75–100).",
        "- These are transparent initial heuristic weights and require sensitivity analysis in later phases.",
        "",
        "## Important limitations",
        "- The data pack does not include a formal data dictionary. The field semantics above are inferred from observed row patterns.",
        "- Revised target and revised overs are used when populated; otherwise a T20/T20I default of 20 overs is used.",
        "- Innings 3 and 4 are treated as Super Overs based on the observed tied-match examples.",
        "- First-innings par is estimated from median final run rate within competition-season. Sparse groups fall back to the overall median.",
        "- Phase 2 labels match situation pressure, not an individual player's performance quality.",
        "",
        "## Output files",
        "- `pressure_classified_deliveries.csv`: delivery-level pre-ball state and pressure labels.",
        "- `pressure_distribution.csv`: format/season/innings pressure distribution.",
        "- `pressure_context_summary.csv`: pressure level summary.",
        "- `scoring_semantics_audit.json`: observed scoring-field audit."
    ]
    (report_dir/"phase2_findings.md").write_text("\n".join(findings),encoding="utf-8")
    summary = {
        "input_rows": int(len(ball)),
        "classified_rows": int(len(classified)),
        "eligible_rows": int(classified["pressure_eligible"].sum()),
        "super_over_rows": int(classified["is_super_over"].sum()),
        "pressure_level_counts": classified.loc[classified["pressure_eligible"],"pressure_level"].value_counts().to_dict(),
        "pressure_context_counts": classified.loc[classified["pressure_eligible"],"pressure_context"].value_counts().to_dict(),
    }
    with open(output_dir/"phase2_summary.json","w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,default=str)
    return summary
