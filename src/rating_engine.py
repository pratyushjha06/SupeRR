
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

BATTER_MIN_BALLS=30
BOWLER_MIN_LEGAL_BALLS=30
MIN_PRESSURE_MATCHES=5
BATTER_MIN_NORMAL_BALLS=30
BOWLER_MIN_NORMAL_LEGAL_BALLS=30
MIN_NORMAL_MATCHES=3
STRONG_PRESSURE_BALLS=120
STRONG_NORMAL_BALLS=120
STRONG_PRESSURE_MATCHES=10
STRONG_NORMAL_MATCHES=5
PRIOR_BALLS=60.0
PRIOR_LEGAL_BALLS=60.0

def _num(df, col, default=np.nan):
    return pd.to_numeric(df[col],errors="coerce") if col in df else pd.Series(default,index=df.index,dtype=float)

def _robust_z(s: pd.Series, higher_is_better=True) -> pd.Series:
    x=pd.to_numeric(s,errors="coerce")
    med=x.median()
    mad=(x-med).abs().median()
    scale=1.4826*mad if pd.notna(mad) and mad>1e-12 else x.std(ddof=0)
    if pd.isna(scale) or scale<=1e-12:
        z=pd.Series(0.0,index=x.index)
    else:
        z=((x-med)/scale).clip(-3,3)
    return z if higher_is_better else -z

def _shrink_rate(pressure_rate, normal_rate, exposure, prior_exposure=60.0):
    """Shrink pressure rate toward the player's normal rate using exposure-based weight."""
    w=exposure/(exposure+prior_exposure)
    return normal_rate + w*(pressure_rate-normal_rate), w

def _confidence_adjusted_delta(pressure_rate, normal_rate, pressure_exposure, normal_exposure, prior=60.0):
    """Discount a pressure-vs-normal delta for uncertainty in BOTH samples.

    This is a transparent heuristic reliability adjustment, not a formal
    sampling model or Bayesian posterior.
    """
    def as_series(value):
        if isinstance(value, pd.Series):
            return pd.to_numeric(value, errors="coerce")
        return pd.Series([pd.to_numeric(value, errors="coerce")])
    pw = as_series(pressure_exposure).fillna(0).clip(lower=0)
    nw = as_series(normal_exposure).fillna(0).clip(lower=0)
    p_weight = pw / (pw + prior)
    n_weight = nw / (nw + prior)
    delta = as_series(pressure_rate) - as_series(normal_rate)
    return delta * p_weight * n_weight, p_weight, n_weight

def _attach_consistency(d, consistency, player_col):
    """Attach one canonical consistency record per player without suffix collisions."""
    cols = ["player_id", "pressure_match_count", "match_metric_mean", "match_metric_std",
            "match_metric_median", "weighted_match_metric_mean", "weighted_match_metric_std",
            "consistency_exposure_balls"]
    c = consistency.reindex(columns=cols).drop_duplicates("player_id", keep="first")
    old = [x for x in cols if x != "player_id" and x in d.columns]
    d = d.drop(columns=old, errors="ignore")
    d = d.merge(c, left_on=player_col, right_on="player_id", how="left", validate="many_to_one")
    d["consistency_exposure_balls"] = _num(d, "consistency_exposure_balls").fillna(0)
    # Weighted dispersion is descriptive only. No confidence interval is inferred
    # from a weighted spread of match aggregates.
    d["consistency_coverage_ratio"] = _num(d, "consistency_exposure_balls") / _num(
        d, "pressure_balls" if "pressure_balls" in d else "pressure_legal_balls"
    ).replace(0, np.nan)
    return d

def _score_components(df, specs):
    zcols={}
    for metric, higher in specs:
        zcols[metric]=_robust_z(df[metric],higher)
    return zcols

def build_batter_ratings(bat: pd.DataFrame, sample: pd.DataFrame, consistency: pd.DataFrame):
    d=bat.merge(sample[["striker_id","pressure_balls","pressure_matches"]],on="striker_id",how="left",suffixes=("","_sample"))
    d["pressure_balls"]=d["pressure_balls"].fillna(d.get("pressure_balls",0)).fillna(0)
    d["pressure_matches"]=_num(d,"pressure_matches").fillna(0)
    d["normal_balls_faced"]=_num(d,"normal_balls_faced").fillna(0)
    d["normal_exposure_matches"]=_num(d,"normal_exposure_matches").fillna(0)
    d["eligible"]= (
        (d.pressure_balls>=BATTER_MIN_BALLS)
        &(d.pressure_matches>=MIN_PRESSURE_MATCHES)
        &(d.normal_balls_faced>=BATTER_MIN_NORMAL_BALLS)
        &(d.normal_exposure_matches>=MIN_NORMAL_MATCHES)
    )
    # Discount each pressure-vs-normal difference for the reliability of both samples.
    for metric in ["strike_rate", "dot_ball_pct", "boundary_pct", "dismissal_rate_pct"]:
        p, n = _num(d, f"pressure_{metric}"), _num(d, f"normal_{metric}")
        delta, pw, nw = _confidence_adjusted_delta(p, n, d.pressure_balls, d.normal_balls_faced, PRIOR_BALLS)
        d[f"pressure_{metric}_reliability_weight"] = pw
        d[f"normal_{metric}_reliability_weight"] = nw
        d[f"combined_{metric}_reliability_weight"] = pw * nw
        d[f"adjusted_{metric}_delta"] = delta
        d[f"shrunk_pressure_{metric}"] = n + delta
    d["sr_component"]=d["adjusted_strike_rate_delta"]
    d["dot_component"]=-d["adjusted_dot_ball_pct_delta"]
    d["boundary_component"]=d["adjusted_boundary_pct_delta"]
    d["dismissal_component"]=-d["adjusted_dismissal_rate_pct_delta"]
    specs=[("sr_component",True),("dot_component",True),("boundary_component",True),("dismissal_component",True)]
    z=_score_components(d,specs)
    for k,v in z.items(): d["z_"+k]=v
    # Consistency is descriptive; it is not converted into a formal confidence interval.
    d = _attach_consistency(d, consistency, "striker_id")
    d["uncertainty_flag"] = np.select(
        [~d.eligible, d.pressure_balls < 60, d.normal_balls_faced < 60,
         d.pressure_matches < 8, d.normal_exposure_matches < 5,
         d.weighted_match_metric_std.isna()],
        ["baseline_or_pressure_ineligible", "low_pressure_exposure", "low_normal_baseline",
         "few_pressure_matches", "few_normal_matches", "insufficient_match_variance"],
        default="standard")
    d["reliability_tier"] = np.select(
        [~d.eligible,
         (d.pressure_balls < STRONG_PRESSURE_BALLS) | (d.normal_balls_faced < STRONG_NORMAL_BALLS)
         | (d.pressure_matches < STRONG_PRESSURE_MATCHES) | (d.normal_exposure_matches < STRONG_NORMAL_MATCHES)],
        ["not_eligible", "limited"], default="stronger")
    weights={
        "balanced":{"z_sr_component":0.35,"z_dot_component":0.20,"z_boundary_component":0.15,"z_dismissal_component":0.30},
        "scoring_impact":{"z_sr_component":0.45,"z_dot_component":0.15,"z_boundary_component":0.25,"z_dismissal_component":0.15},
        "survival":{"z_sr_component":0.20,"z_dot_component":0.25,"z_boundary_component":0.10,"z_dismissal_component":0.45},
        "equal":{"z_sr_component":0.25,"z_dot_component":0.25,"z_boundary_component":0.25,"z_dismissal_component":0.25},
    }
    for scheme,ws in weights.items():
        d[f"rating_{scheme}"]=sum(d[col]*w for col,w in ws.items())
    d["provisional_rating"]=d["rating_balanced"]
    return d,weights

def build_bowler_ratings(bowl: pd.DataFrame, sample: pd.DataFrame, consistency: pd.DataFrame):
    d=bowl.merge(sample[["bowler_id","pressure_legal_balls","pressure_matches"]],on="bowler_id",how="left",suffixes=("","_sample"))
    d["pressure_legal_balls"]=d["pressure_legal_balls"].fillna(0)
    d["pressure_matches"]=_num(d,"pressure_matches").fillna(0)
    d["normal_legal_balls"]=_num(d,"normal_legal_balls").fillna(0)
    d["normal_exposure_matches"]=_num(d,"normal_exposure_matches").fillna(0)
    d["eligible"]=(
        (d.pressure_legal_balls>=BOWLER_MIN_LEGAL_BALLS)
        &(d.pressure_matches>=MIN_PRESSURE_MATCHES)
        &(d.normal_legal_balls>=BOWLER_MIN_NORMAL_LEGAL_BALLS)
        &(d.normal_exposure_matches>=MIN_NORMAL_MATCHES)
    )
    # Discount each pressure-vs-normal difference for the reliability of both samples.
    for metric in ["economy", "dot_ball_pct", "wickets_per_over", "boundary_conceded_pct", "charged_extras_per_over"]:
        p, n = _num(d, f"pressure_{metric}"), _num(d, f"normal_{metric}")
        delta, pw, nw = _confidence_adjusted_delta(p, n, d.pressure_legal_balls, d.normal_legal_balls, PRIOR_LEGAL_BALLS)
        d[f"pressure_{metric}_reliability_weight"] = pw
        d[f"normal_{metric}_reliability_weight"] = nw
        d[f"combined_{metric}_reliability_weight"] = pw * nw
        d[f"adjusted_{metric}_delta"] = delta
        d[f"shrunk_pressure_{metric}"] = n + delta
    d["economy_component"]=-d["adjusted_economy_delta"]
    d["dot_component"]=d["adjusted_dot_ball_pct_delta"]
    d["wicket_component"]=d["adjusted_wickets_per_over_delta"]
    d["boundary_component"]=-d["adjusted_boundary_conceded_pct_delta"]
    d["extras_component"]=-d["adjusted_charged_extras_per_over_delta"]
    specs=[("economy_component",True),("dot_component",True),("wicket_component",True),("boundary_component",True),("extras_component",True)]
    z=_score_components(d,specs)
    for k,v in z.items(): d["z_"+k]=v
    # Consistency is descriptive; it is not converted into a formal confidence interval.
    d = _attach_consistency(d, consistency, "bowler_id")
    d["uncertainty_flag"] = np.select(
        [~d.eligible, d.pressure_legal_balls < 60, d.normal_legal_balls < 60,
         d.pressure_matches < 8, d.normal_exposure_matches < 5,
         d.weighted_match_metric_std.isna()],
        ["baseline_or_pressure_ineligible", "low_pressure_exposure", "low_normal_baseline",
         "few_pressure_matches", "few_normal_matches", "insufficient_match_variance"],
        default="standard")
    d["reliability_tier"] = np.select(
        [~d.eligible,
         (d.pressure_legal_balls < STRONG_PRESSURE_BALLS) | (d.normal_legal_balls < STRONG_NORMAL_BALLS)
         | (d.pressure_matches < STRONG_PRESSURE_MATCHES) | (d.normal_exposure_matches < STRONG_NORMAL_MATCHES)],
        ["not_eligible", "limited"], default="stronger")
    weights={
        "balanced":{"z_economy_component":0.30,"z_dot_component":0.20,"z_wicket_component":0.25,"z_boundary_component":0.15,"z_extras_component":0.10},
        "wicket_impact":{"z_economy_component":0.20,"z_dot_component":0.15,"z_wicket_component":0.40,"z_boundary_component":0.15,"z_extras_component":0.10},
        "control":{"z_economy_component":0.35,"z_dot_component":0.30,"z_wicket_component":0.15,"z_boundary_component":0.15,"z_extras_component":0.05},
        "equal":{"z_economy_component":0.20,"z_dot_component":0.20,"z_wicket_component":0.20,"z_boundary_component":0.20,"z_extras_component":0.20},
    }
    for scheme,ws in weights.items():
        d[f"rating_{scheme}"]=sum(d[col]*w for col,w in ws.items())
    d["provisional_rating"]=d["rating_balanced"]
    return d,weights

def _rank(df, id_col, name_col, rating_col):
    score=pd.to_numeric(df[rating_col],errors="coerce")
    x=df.loc[df.eligible & np.isfinite(score)].copy().sort_values(rating_col,ascending=False)
    x["provisional_rank"]=range(1,len(x)+1)
    exposure_col = "pressure_balls" if "pressure_balls" in x else "pressure_legal_balls"
    normal_col = "normal_balls_faced" if "normal_balls_faced" in x else "normal_legal_balls"
    cols=[id_col,name_col,"provisional_rank",rating_col,exposure_col,normal_col,
          "pressure_matches","normal_exposure_matches","reliability_tier","uncertainty_flag",
          "weighted_match_metric_mean","weighted_match_metric_std","consistency_exposure_balls","consistency_coverage_ratio"]
    return x[[c for c in cols if c in x.columns]]

def _sensitivity(df, id_col, rating_cols, role):
    base=df.loc[df.eligible & np.isfinite(pd.to_numeric(df["rating_balanced"],errors="coerce"))].sort_values("rating_balanced",ascending=False)
    base_ids=base[id_col].tolist()
    rows=[]
    for col in rating_cols:
        ranked=df.loc[df.eligible & np.isfinite(pd.to_numeric(df[col],errors="coerce"))].sort_values(col,ascending=False)
        ids=ranked[id_col].tolist()
        n=min(10,len(base_ids),len(ids))
        overlap=len(set(base_ids[:n])&set(ids[:n]))/max(n,1)
        base_rank={v:i+1 for i,v in enumerate(base_ids)}
        alt_rank={v:i+1 for i,v in enumerate(ids)}
        common=list(set(base_rank)&set(alt_rank))
        corr=pd.Series([base_rank[v] for v in common]).corr(
            pd.Series([alt_rank[v] for v in common]),method="spearman"
        ) if len(common)>1 else np.nan
        rows.append({"role":role,"scheme":col.replace("rating_",""),"top10_overlap_vs_balanced":overlap,"rank_order_correlation":corr})
    # Exposure threshold sensitivity: rerank the balanced rating after changing eligibility cutoffs.
    for threshold in [20,30,45,60,90]:
        exposure="pressure_balls" if role=="batter" else "pressure_legal_balls"
        normal_exposure="normal_balls_faced" if role=="batter" else "normal_legal_balls"
        normal_matches="normal_exposure_matches"
        elig=df[(df[exposure]>=threshold)&(df.pressure_matches>=MIN_PRESSURE_MATCHES)
                &(df[normal_exposure]>=BATTER_MIN_NORMAL_BALLS if role=="batter" else df[normal_exposure]>=BOWLER_MIN_NORMAL_LEGAL_BALLS)
                &(df[normal_matches]>=MIN_NORMAL_MATCHES)
                &np.isfinite(pd.to_numeric(df["rating_balanced"],errors="coerce"))].sort_values("rating_balanced",ascending=False)
        n=min(10,len(base_ids),len(elig))
        overlap=len(set(base_ids[:n])&set(elig[id_col].head(n)))/max(n,1)
        rows.append({"role":role,"scheme":f"min_exposure_{threshold}","top10_overlap_vs_balanced":overlap,"rank_order_correlation":np.nan})
    return pd.DataFrame(rows)

def run_phase4(outputs:Path,reports:Path):
    outputs,reports=Path(outputs),Path(reports)
    # Strict problem-statement scope: IPL and T20I only.
    metadata_path=outputs/"matches_with_competition_metadata.csv"
    delivery_path=outputs/"pressure_classified_deliveries.csv"
    if not metadata_path.exists() or not delivery_path.exists():
        raise FileNotFoundError("Phase 4.1 requires matches_with_competition_metadata.csv and pressure_classified_deliveries.csv. Run Phase 1–2 first.")
    meta=pd.read_csv(metadata_path,usecols=["match_id","comp_name","match_format"])
    is_ipl=meta["comp_name"].astype(str).str.fullmatch(r"IPL\s+\d{4}",case=False,na=False)
    is_t20i=meta["match_format"].astype(str).str.upper().eq("T20I")
    allowed=set(meta.loc[is_ipl|is_t20i,"match_id"])
    all_deliveries=pd.read_csv(delivery_path,low_memory=False)
    before=len(all_deliveries)
    scoped=all_deliveries[all_deliveries["match_id"].isin(allowed)].copy()
    excluded=before-len(scoped)
    scoped_path=outputs/"phase4_1_ipl_t20i_deliveries.csv"
    scoped.to_csv(scoped_path,index=False)
    from src.performance_engine import run_phase3
    phase3_summary=run_phase3(scoped_path,outputs,reports)
    scoped_path.unlink(missing_ok=True)

    bat=pd.read_csv(outputs/"batting_pressure_vs_normal.csv")
    bowl=pd.read_csv(outputs/"bowling_pressure_vs_normal.csv")
    bs=pd.read_csv(outputs/"batting_sample_size_report.csv")
    ws=pd.read_csv(outputs/"bowling_sample_size_report.csv")
    bc=pd.read_csv(outputs/"batting_match_consistency.csv")
    wc=pd.read_csv(outputs/"bowling_match_consistency.csv")
    br,bw=build_batter_ratings(bat,bs,bc)
    wr,ww=build_bowler_ratings(bowl,ws,wc)
    br.to_csv(outputs/"batter_ratings_all.csv",index=False)
    wr.to_csv(outputs/"bowler_ratings_all.csv",index=False)
    brank=_rank(br,"striker_id","striker_name","provisional_rating")
    wrank=_rank(wr,"bowler_id","bowler_name","provisional_rating")
    brank.to_csv(outputs/"provisional_batter_rankings.csv",index=False)
    wrank.to_csv(outputs/"provisional_bowler_rankings.csv",index=False)
    bsens=_sensitivity(br,"striker_id",[f"rating_{x}" for x in bw],"batter")
    wsens=_sensitivity(wr,"bowler_id",[f"rating_{x}" for x in ww],"bowler")
    sens=pd.concat([bsens,wsens],ignore_index=True)
    sens.to_csv(outputs/"ranking_sensitivity.csv",index=False)
    # Expanded review tables retain pressure/normal metrics, adjusted deltas,
    # component scores, exposure, reliability and descriptive consistency fields.
    br_full=br.loc[br.eligible & np.isfinite(pd.to_numeric(br.provisional_rating,errors="coerce"))].sort_values("provisional_rating",ascending=False).head(20).copy()
    wr_full=wr.loc[wr.eligible & np.isfinite(pd.to_numeric(wr.provisional_rating,errors="coerce"))].sort_values("provisional_rating",ascending=False).head(20).copy()
    br_full.insert(0,"provisional_rank",range(1,len(br_full)+1))
    wr_full.insert(0,"provisional_rank",range(1,len(wr_full)+1))
    br_full.to_csv(outputs/"provisional_batter_top20_review.csv",index=False)
    wr_full.to_csv(outputs/"provisional_bowler_top20_review.csv",index=False)
    summary={
        "competition_scope":"IPL and T20I only",
        "classified_deliveries_before_scope_filter":int(before),
        "classified_deliveries_after_scope_filter":int(len(scoped)),
        "excluded_out_of_scope_deliveries":int(excluded),
        "batter_candidates_pressure_eligible":int(((br.pressure_balls>=BATTER_MIN_BALLS)&(br.pressure_matches>=MIN_PRESSURE_MATCHES)).sum()),
        "bowler_candidates_pressure_eligible":int(((wr.pressure_legal_balls>=BOWLER_MIN_LEGAL_BALLS)&(wr.pressure_matches>=MIN_PRESSURE_MATCHES)).sum()),
        "batter_candidates_final_eligible":int(br.eligible.sum()),
        "bowler_candidates_final_eligible":int(wr.eligible.sum()),
        "batter_candidates_excluded_for_baseline":int((((br.pressure_balls>=BATTER_MIN_BALLS)&(br.pressure_matches>=MIN_PRESSURE_MATCHES))&~br.eligible).sum()),
        "bowler_candidates_excluded_for_baseline":int((((wr.pressure_legal_balls>=BOWLER_MIN_LEGAL_BALLS)&(wr.pressure_matches>=MIN_PRESSURE_MATCHES))&~wr.eligible).sum()),
        "batter_reliability_tiers":br.loc[br.eligible,"reliability_tier"].value_counts().to_dict(),
        "bowler_reliability_tiers":wr.loc[wr.eligible,"reliability_tier"].value_counts().to_dict(),
        "batter_consistency_records":int(br.weighted_match_metric_mean.notna().sum()),
        "bowler_consistency_records":int(wr.weighted_match_metric_mean.notna().sum()),
        "batter_min_pressure_balls":BATTER_MIN_BALLS,
        "bowler_min_pressure_legal_balls":BOWLER_MIN_LEGAL_BALLS,
        "batter_min_normal_balls":BATTER_MIN_NORMAL_BALLS,
        "bowler_min_normal_legal_balls":BOWLER_MIN_NORMAL_LEGAL_BALLS,
        "minimum_pressure_matches":MIN_PRESSURE_MATCHES,
        "minimum_normal_matches":MIN_NORMAL_MATCHES,
        "prior_exposure_balls":PRIOR_BALLS,
        "prior_exposure_legal_balls":PRIOR_LEGAL_BALLS,
        "weighted_match_consistency":True,
        "consistency_intervals_reported":False,
        "two_sample_reliability_adjustment":True,
        "strong_reliability_thresholds":{"pressure_balls_or_legal_balls":STRONG_PRESSURE_BALLS,"normal_balls_or_legal_balls":STRONG_NORMAL_BALLS,"pressure_matches":STRONG_PRESSURE_MATCHES,"normal_matches":STRONG_NORMAL_MATCHES},
        "rankings_status":"provisional_review_only",
        "final_unstop_top10_created":False
    }
    with open(outputs/"phase4_summary.json","w",encoding="utf-8") as f:json.dump(summary,f,indent=2)
    reports.mkdir(parents=True,exist_ok=True)
    lines=[
        "# PRESSURE-X Phase 4.2 — Two-Sample Reliability and Consistency Refinement","",
        "## Competition scope",
        "- The original problem statement specifies IPL and T20I data. Phase 4.1 filters to those competitions only.",
        f"- Classified deliveries before filter: {before:,}; after filter: {len(scoped):,}; excluded: {excluded:,}.",
        "",
        "## Eligibility",
        f"- Batters: >= {BATTER_MIN_BALLS} pressure balls, >= {MIN_PRESSURE_MATCHES} pressure matches, >= {BATTER_MIN_NORMAL_BALLS} normal balls, >= {MIN_NORMAL_MATCHES} normal matches.",
        f"- Bowlers: >= {BOWLER_MIN_LEGAL_BALLS} pressure legal balls, >= {MIN_PRESSURE_MATCHES} pressure matches, >= {BOWLER_MIN_NORMAL_LEGAL_BALLS} normal legal balls, >= {MIN_NORMAL_MATCHES} normal matches.",
        "- Pressure and normal exposure are separate eligibility requirements. Missing or inadequate baselines are not ranked.",
        "",
        "## Shrinkage and normalization",
        f"- Pressure rates are shrunk toward each player's normal rate using {PRIOR_BALLS:.0f} prior balls/legal balls.",
        "- Direction-aware deltas are robust-z normalized using median/MAD, with standard-deviation fallback and +/-3 clipping.",
        "- Non-finite composite ratings are excluded from all ranked lists.",
        "",
        "## Match consistency and reliability",
        "- Match-level strike rate/economy summaries include ball-weighted mean and weighted dispersion, so matches contribute in proportion to pressure balls/legal balls.",
        "- Consistency mean and weighted dispersion are descriptive diagnostics only; no confidence interval is reported from weighted match aggregates.",
        "- Pressure-vs-normal deltas are discounted using separate pressure- and normal-exposure reliability weights. This is a transparent heuristic, not a formal posterior model.",
        f"- Stronger-evidence tier requires >= {STRONG_PRESSURE_BALLS} pressure balls/legal balls, >= {STRONG_NORMAL_BALLS} normal balls/legal balls, >= {STRONG_PRESSURE_MATCHES} pressure matches and >= {STRONG_NORMAL_MATCHES} normal matches.",
        "- Reliability tiers separate ineligible, limited-exposure and stronger-evidence candidates.",
        "",
        "## Sensitivity",
        "- Alternative weights and exposure thresholds are recalculated on the eligible IPL/T20I candidate pool.",
        "",
        "## Status",
        "- All rankings remain provisional for review. No final Unstop Top 10 is generated."
    ]
    (reports/"phase4_findings.md").write_text("\n".join(lines),encoding="utf-8")
    return summary
