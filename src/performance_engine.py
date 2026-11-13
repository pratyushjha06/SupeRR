
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

HIGH_LEVELS = {"high", "very_high"}
BOWLER_CREDIT_DISMISSALS = {
    "caught", "bowled", "lbw", "stump", "hit wicket",
    "caught and bowled", "caught&bowled"
}
BYE_TYPES = {"byes", "legbyes", "leg-byes", "penalty"}

def _norm_text(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.lower()

def _safe_div(a, b):
    numerator, denominator = np.broadcast_arrays(np.asarray(a, dtype=float), np.asarray(b, dtype=float))
    out = np.full(numerator.shape, np.nan, dtype=float)
    np.divide(numerator, denominator, out=out, where=denominator > 0)
    return out

def prepare_performance_events(df: pd.DataFrame) -> pd.DataFrame:
    """Derive auditable batting/bowling event fields from Phase 2 delivery data."""
    d = df.copy()
    d["extras_type_norm"] = _norm_text(d["extras_type"])
    d["dismissal_norm"] = _norm_text(d["dismissal_type"])
    d["batter_runs"] = pd.to_numeric(d["runs"], errors="coerce").fillna(0)
    d["extras1_runs"] = pd.to_numeric(d["extras1_runs"], errors="coerce").fillna(0)
    d["extras_2_runs"] = pd.to_numeric(d["extras_2_runs"], errors="coerce").fillna(0)
    d["team_runs_this_delivery"] = d["batter_runs"] + d["extras1_runs"] + d["extras_2_runs"]
    d["is_wide"] = d["extras_type_norm"].eq("wide")
    d["is_overstep"] = d["extras_type_norm"].eq("overstep")
    d["is_legal_delivery"] = ~(d["is_wide"] | d["is_overstep"])
    # In the observed data, runs can be recorded on Overstep rows (batter runs off a no-ball).
    # Batter balls faced exclude wides; a no-ball is faced.
    d["batter_ball_faced"] = ~d["is_wide"]
    d["is_batter_dot"] = d["batter_runs"].eq(0)
    d["is_batter_boundary"] = d["batter_runs"].isin([4, 6])
    d["wicket_event"] = d["is_wicket"].fillna(False).astype(bool)
    d["bowler_credit_wicket"] = (
        d["wicket_event"] & d["dismissal_norm"].isin(BOWLER_CREDIT_DISMISSALS)
    )
    # Bowler-conceded runs: batter runs + wide/no-ball extras. Byes, leg-byes and
    # penalty extras are not charged to the bowler. "other" extras are ambiguous,
    # so their extra component is not assigned to the bowler; this is flagged.
    charged_extra = np.where(d["extras_type_norm"].isin({"wide", "overstep"}),
                             d["extras1_runs"] + d["extras_2_runs"], 0)
    bye_or_penalty = d["extras_type_norm"].isin(BYE_TYPES)
    # Respect the extras label for bowler attribution even where the source's
    # `runs` field conflicts with it (one observed leg-byes row has runs=1).
    bowler_batter_runs = d["batter_runs"].where(~bye_or_penalty, 0)
    d["bowler_runs_conceded"] = bowler_batter_runs + charged_extra
    d["ambiguous_extra_row"] = d["extras_type_norm"].eq("other")
    d["scoring_semantics_anomaly"] = bye_or_penalty & d["batter_runs"].ne(0)
    d["bowler_dot_delivery"] = d["is_legal_delivery"] & d["bowler_runs_conceded"].eq(0)
    d["bowler_boundary_conceded"] = d["is_batter_boundary"]
    d["bowler_extra_runs_charged"] = charged_extra
    d["pressure_group"] = np.where(
        d["pressure_level"].astype(str).isin(HIGH_LEVELS), "pressure",
        np.where(d["pressure_level"].astype(str).isin({"low","moderate"}), "normal", "excluded")
    )
    d["analysis_eligible"] = (
        d["pressure_eligible"].fillna(False).astype(bool)
        & d["is_regulation_innings"].fillna(False).astype(bool)
        & ~d["is_super_over"].fillna(False).astype(bool)
        & d["pressure_group"].isin(["pressure","normal"])
    )
    return d

def _aggregate_batting(events: pd.DataFrame) -> pd.DataFrame:
    e = events.loc[events["analysis_eligible"]].copy()
    striker = e.loc[e["striker_id"].notna()].copy()
    agg = striker.groupby(["striker_id", "pressure_group"], dropna=False).agg(
        batting_runs=("batter_runs","sum"), balls_faced=("batter_ball_faced","sum"),
        dot_balls=("is_batter_dot","sum"), boundaries=("is_batter_boundary","sum"),
        fours=("is_four","sum"), sixes=("is_six","sum"),
        batting_deliveries=("match_id","size"), matches=("match_id","nunique"),
        team_runs=("team_runs_this_delivery","sum")
    ).reset_index().rename(columns={"striker_id":"player_id"})

    # Use dismissed_player_id so non-striker run-outs are assigned to the correct batter.
    w = e.loc[e["wicket_event"] & e["dismissed_player_id"].notna()]
    if len(w):
        dismiss = w.groupby(["dismissed_player_id","pressure_group"],dropna=False).agg(
            dismissals=("match_id","size"), dismissal_matches=("match_id","nunique")
        ).reset_index().rename(columns={"dismissed_player_id":"player_id"})
        agg = agg.merge(dismiss,on=["player_id","pressure_group"],how="outer")
    else:
        agg["dismissals"] = 0
        agg["dismissal_matches"] = 0

    # Include players dismissed as non-strikers even if they faced no ball in that group.
    names = pd.concat([
        e[["striker_id","striker_name"]].rename(columns={"striker_id":"player_id","striker_name":"player_name"}),
        e[["non_striker_id","non_striker_name"]].rename(columns={"non_striker_id":"player_id","non_striker_name":"player_name"})
    ],ignore_index=True).dropna(subset=["player_id","player_name"]).drop_duplicates("player_id")
    agg = agg.merge(names,on="player_id",how="left")
    numeric = ["batting_runs","balls_faced","dot_balls","boundaries","fours","sixes",
               "batting_deliveries","matches","team_runs","dismissals","dismissal_matches"]
    agg[numeric] = agg[numeric].fillna(0)
    agg["strike_rate"] = _safe_div(agg["batting_runs"]*100,agg["balls_faced"])
    agg["runs_per_ball"] = _safe_div(agg["batting_runs"],agg["balls_faced"])
    agg["dot_ball_pct"] = _safe_div(agg["dot_balls"]*100,agg["balls_faced"])
    agg["boundary_pct"] = _safe_div(agg["boundaries"]*100,agg["balls_faced"])
    agg["dismissal_rate_pct"] = _safe_div(agg["dismissals"]*100,agg["balls_faced"])
    return agg.rename(columns={"player_id":"striker_id","player_name":"striker_name"})

def _aggregate_bowling(events: pd.DataFrame) -> pd.DataFrame:
    e = events.loc[events["analysis_eligible"] & events["bowler_id"].notna()].copy()
    keys = ["bowler_id","bowler_name","pressure_group"]
    agg = e.groupby(keys,dropna=False).agg(
        runs_conceded=("bowler_runs_conceded","sum"),
        legal_balls=("is_legal_delivery","sum"),
        bowled_deliveries=("match_id","size"),
        dot_balls=("bowler_dot_delivery","sum"),
        credited_wickets=("bowler_credit_wicket","sum"),
        boundaries_conceded=("bowler_boundary_conceded","sum"),
        charged_extras=("bowler_extra_runs_charged","sum"),
        ambiguous_extra_rows=("ambiguous_extra_row","sum"),
        matches=("match_id","nunique"),
    ).reset_index()
    agg["overs_legal"] = agg["legal_balls"] / 6.0
    agg["economy"] = _safe_div(agg["runs_conceded"]*6,agg["legal_balls"])
    agg["dot_ball_pct"] = _safe_div(agg["dot_balls"]*100,agg["legal_balls"])
    agg["wickets_per_over"] = _safe_div(agg["credited_wickets"]*6,agg["legal_balls"])
    agg["boundary_conceded_pct"] = _safe_div(agg["boundaries_conceded"]*100,agg["legal_balls"])
    agg["charged_extras_per_over"] = _safe_div(agg["charged_extras"]*6,agg["legal_balls"])
    return agg

def _wide_player_table(agg: pd.DataFrame, id_col: str, name_col: str, metric_cols: list[str], role: str) -> pd.DataFrame:
    if agg.empty:
        return pd.DataFrame(columns=[id_col,name_col])
    idx=[id_col,name_col]
    parts=[]
    for group in ["pressure","normal"]:
        sub=agg[agg.pressure_group.eq(group)].drop(columns=["pressure_group"])
        sub=sub.rename(columns={c:f"{group}_{c}" for c in sub.columns if c not in idx})
        parts.append(sub)
    out=parts[0]
    if len(parts)>1:
        out=out.merge(parts[1],on=idx,how="outer")
    for metric in metric_cols:
        p=f"pressure_{metric}"; n=f"normal_{metric}"
        if p in out and n in out:
            # Direction-normalized deltas are handled explicitly below, not here.
            out[f"{metric}_delta"] = out[p] - out[n]
    return out

def _match_consistency(events: pd.DataFrame, role: str) -> pd.DataFrame:
    if role=="batting":
        e=events.loc[events.analysis_eligible & events.striker_id.notna()].copy()
        g=e.groupby(["striker_id","striker_name","match_id","pressure_group"],dropna=False).agg(
            runs=("batter_runs","sum"), balls=("batter_ball_faced","sum"),
            dots=("is_batter_dot","sum"), boundaries=("is_batter_boundary","sum")
        ).reset_index()
        g["metric"]=_safe_div(g["runs"]*100,g["balls"])
        g=g[g.pressure_group.eq("pressure") & (g["balls"] > 0)].copy()
        rows=[]
        for (pid,pname), grp in g.groupby(["striker_id","striker_name"]):
            w=grp["balls"].astype(float)
            x=grp["metric"].astype(float)
            wm=float(np.average(x,weights=w)) if w.sum()>0 else np.nan
            wvar=float(np.average((x-wm)**2,weights=w)) if w.sum()>0 else np.nan
            rows.append({"player_id":pid,"player_name":pname,
                "pressure_match_count":int(grp["match_id"].nunique()),
                "match_metric_mean":float(x.mean()),"match_metric_std":float(x.std(ddof=1)) if len(x)>1 else np.nan,
                "match_metric_median":float(x.median()),"weighted_match_metric_mean":wm,
                "weighted_match_metric_std":float(np.sqrt(wvar)) if pd.notna(wvar) else np.nan,
                "consistency_exposure_balls":int(w.sum())})
        return pd.DataFrame(rows)
    e=events.loc[events.analysis_eligible & events.bowler_id.notna()].copy()
    g=e.groupby(["bowler_id","bowler_name","match_id","pressure_group"],dropna=False).agg(
        runs=("bowler_runs_conceded","sum"), legal=("is_legal_delivery","sum"),
        wickets=("bowler_credit_wicket","sum")
    ).reset_index()
    g["metric"]=_safe_div(g["runs"]*6,g["legal"])
    g=g[g.pressure_group.eq("pressure") & (g["legal"] > 0)].copy()
    rows=[]
    for (pid,pname), grp in g.groupby(["bowler_id","bowler_name"]):
        w=grp["legal"].astype(float)
        x=grp["metric"].astype(float)
        wm=float(np.average(x,weights=w)) if w.sum()>0 else np.nan
        wvar=float(np.average((x-wm)**2,weights=w)) if w.sum()>0 else np.nan
        rows.append({"player_id":pid,"player_name":pname,
            "pressure_match_count":int(grp["match_id"].nunique()),
            "match_metric_mean":float(x.mean()),"match_metric_std":float(x.std(ddof=1)) if len(x)>1 else np.nan,
            "match_metric_median":float(x.median()),"weighted_match_metric_mean":wm,
            "weighted_match_metric_std":float(np.sqrt(wvar)) if pd.notna(wvar) else np.nan,
            "consistency_exposure_balls":int(w.sum())})
    return pd.DataFrame(rows)

def run_phase3(input_csv: Path, output_dir: Path, report_dir: Path) -> dict:
    input_csv, output_dir, report_dir = Path(input_csv),Path(output_dir),Path(report_dir)
    output_dir.mkdir(parents=True,exist_ok=True); report_dir.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(input_csv,low_memory=False)
    events=prepare_performance_events(df)
    bat=_aggregate_batting(events)
    bowl=_aggregate_bowling(events)
    bat.to_csv(output_dir/"batting_player_group_metrics.csv",index=False)
    bowl.to_csv(output_dir/"bowling_player_group_metrics.csv",index=False)

    bat_wide=_wide_player_table(
        bat,"striker_id","striker_name",
        ["batting_runs","balls_faced","dismissals","strike_rate","runs_per_ball","dot_ball_pct","boundary_pct","dismissal_rate_pct","matches"],
        "batting"
    )
    bowl_wide=_wide_player_table(
        bowl,"bowler_id","bowler_name",
        ["runs_conceded","legal_balls","credited_wickets","economy","dot_ball_pct","wickets_per_over","boundary_conceded_pct","charged_extras_per_over","matches"],
        "bowling"
    )
    bat_cons=_match_consistency(events,"batting")
    bowl_cons=_match_consistency(events,"bowling")
    bat_cons.to_csv(output_dir/"batting_match_consistency.csv",index=False)
    bowl_cons.to_csv(output_dir/"bowling_match_consistency.csv",index=False)

    bat_wide=bat_wide.rename(columns={"pressure_matches":"pressure_exposure_matches","normal_matches":"normal_exposure_matches"})
    bowl_wide=bowl_wide.rename(columns={"pressure_matches":"pressure_exposure_matches","normal_matches":"normal_exposure_matches"})
    bat_wide=bat_wide.merge(bat_cons,left_on=["striker_id","striker_name"],right_on=["player_id","player_name"],how="left").drop(columns=["player_id","player_name"],errors="ignore")
    bowl_wide=bowl_wide.merge(bowl_cons,left_on=["bowler_id","bowler_name"],right_on=["player_id","player_name"],how="left").drop(columns=["player_id","player_name"],errors="ignore")
    bat_wide.to_csv(output_dir/"batting_pressure_vs_normal.csv",index=False)
    bowl_wide.to_csv(output_dir/"bowling_pressure_vs_normal.csv",index=False)

    # Eligibility diagnostics; no final rankings are produced in Phase 3.
    bat_exp=bat[bat.pressure_group.eq("pressure")].groupby(["striker_id","striker_name"]).agg(
        pressure_balls=("balls_faced","sum"),pressure_runs=("batting_runs","sum"),
        pressure_dismissals=("dismissals","sum"),pressure_matches=("matches","max")
    ).reset_index().sort_values(["pressure_balls","pressure_matches"],ascending=False)
    bowl_exp=bowl[bowl.pressure_group.eq("pressure")].groupby(["bowler_id","bowler_name"]).agg(
        pressure_legal_balls=("legal_balls","sum"),pressure_wickets=("credited_wickets","sum"),
        pressure_runs_conceded=("runs_conceded","sum"),pressure_matches=("matches","max")
    ).reset_index().sort_values(["pressure_legal_balls","pressure_matches"],ascending=False)
    bat_exp.to_csv(output_dir/"batting_sample_size_report.csv",index=False)
    bowl_exp.to_csv(output_dir/"bowling_sample_size_report.csv",index=False)

    # Audit the ambiguous extras and dismissal-credit rules for transparency.
    extras=events.groupby("extras_type_norm",dropna=False).agg(
        rows=("match_id","size"),batter_runs=("batter_runs","sum"),
        extras1=("extras1_runs","sum"),extras2=("extras_2_runs","sum"),
        bowler_runs_assigned=("bowler_runs_conceded","sum"),
        ambiguous_rows=("ambiguous_extra_row","sum"),
        scoring_anomaly_rows=("scoring_semantics_anomaly","sum")
    ).reset_index()
    extras.to_csv(output_dir/"phase3_extras_treatment.csv",index=False)
    dismiss=events.loc[events.wicket_event].groupby(["dismissal_norm"],dropna=False).agg(
        wicket_events=("match_id","size"),
        credited_to_bowler=("bowler_credit_wicket","sum")
    ).reset_index()
    dismiss.to_csv(output_dir/"phase3_dismissal_treatment.csv",index=False)

    summary={
        "input_deliveries":int(len(df)),
        "eligible_deliveries":int(events.analysis_eligible.sum()),
        "batters_with_pressure_exposure":int(bat_exp.striker_id.nunique()),
        "bowlers_with_pressure_exposure":int(bowl_exp.bowler_id.nunique()),
        "pressure_batter_match_observations":int(bat_cons.pressure_match_count.sum()) if len(bat_cons) else 0,
        "pressure_bowler_match_observations":int(bowl_cons.pressure_match_count.sum()) if len(bowl_cons) else 0,
        "bowler_credit_dismissal_types":sorted(BOWLER_CREDIT_DISMISSALS),
        "ambiguous_other_extra_deliveries":int(events.ambiguous_extra_row.sum()),
        "bye_or_penalty_rows_with_nonzero_runs_field":int(events.scoring_semantics_anomaly.sum()),
        "rankings_generated":False
    }
    with open(output_dir/"phase3_summary.json","w",encoding="utf-8") as f: json.dump(summary,f,indent=2)
    report=[
        "# PRESSURE-X Phase 3 — Player Performance Analysis","",
        f"- Input deliveries: {summary['input_deliveries']:,}",
        f"- Eligible regulation deliveries: {summary['eligible_deliveries']:,}",
        f"- Batters with high/very-high pressure exposure: {summary['batters_with_pressure_exposure']:,}",
        f"- Bowlers with high/very-high pressure exposure: {summary['bowlers_with_pressure_exposure']:,}","",
        "## Batting methodology",
        "- Batter runs use the observed `runs` field; team runs are `runs + extras1_runs + extras_2_runs`.",
        "- Batter balls faced exclude wides and include Overstep/no-ball deliveries.",
        "- Dismissals are attributed using `dismissed_player_id`, not assumed to be the striker. This captures non-striker run-outs.",
        "- Batting metrics: strike rate, runs per ball, dot-ball percentage, boundary percentage and dismissal rate.",
        "",
        "## Bowling methodology",
        "- Legal balls exclude observed `wide` and `Overstep` delivery types.",
        "- Bowler-conceded runs include batter runs plus wide/Overstep extras. Byes, leg-byes and penalty extras are excluded.",
        "- `other` extra components are not charged to the bowler because their precise meaning is not documented; rows are separately flagged.",
        "- The data contains one leg-byes-labelled row with `runs=1` and zero recorded extras. It is flagged as a source-semantic anomaly; the bowler-conceded calculation follows the leg-byes label and does not charge that run to the bowler. Batting `runs` remains source-field-based pending external scorecard verification.",
        "- Credited wickets include caught, bowled, LBW, stump/stumped and hit wicket variants. Run-outs and retired-out/obstructing-field dismissals are not credited.",
        "- Bowling metrics: economy, dot-ball percentage, wickets per over, boundary-conceded percentage and charged extras per over.",
        "",
        "## Pressure vs normal",
        "- Pressure = Phase 2 high + very_high labels; normal = low + moderate labels.",
        "- Metrics are calculated separately for each group; this phase does not generate final player rankings.",
        "- Match-level pressure strike rate (batting) and economy (bowling) are summarized using mean, median and standard deviation.",
        "",
        "## Reliability and limitations",
        "- Sample-size reports expose pressure balls/legal balls, runs, wickets and pressure-match counts.",
        "- Minimum eligibility thresholds and shrinkage weights are deliberately deferred to Phase 4, where ranking sensitivity can be tested.",
        "- `runs` and extras interpretation is inferred from observed rows because the pack has no formal data dictionary. Verify edge cases against official scorecards if possible.",
        "- Unknown `other` extras are treated conservatively for bowler runs; results should be sensitivity-tested.",
        "- Match-level consistency standard deviation is descriptive and should not be interpreted as a confidence interval.",
        "",
        "## Outputs",
        "- `batting_pressure_vs_normal.csv`, `bowling_pressure_vs_normal.csv`",
        "- `batting_player_group_metrics.csv`, `bowling_player_group_metrics.csv`",
        "- `batting_match_consistency.csv`, `bowling_match_consistency.csv`",
        "- `batting_sample_size_report.csv`, `bowling_sample_size_report.csv`",
        "- `phase3_extras_treatment.csv`, `phase3_dismissal_treatment.csv`",
        "- No final top-10 rankings are generated in Phase 3."
    ]
    (report_dir/"phase3_findings.md").write_text("\n".join(report),encoding="utf-8")
    return summary
