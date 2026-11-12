
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

BATTER_MIN_BALLS=30
BOWLER_MIN_LEGAL_BALLS=30
MIN_PRESSURE_MATCHES=5
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

def _score_components(df, specs):
    zcols={}
    for metric, higher in specs:
        zcols[metric]=_robust_z(df[metric],higher)
    return zcols

def build_batter_ratings(bat: pd.DataFrame, sample: pd.DataFrame, consistency: pd.DataFrame):
    d=bat.merge(sample[["striker_id","pressure_balls","pressure_matches"]],on="striker_id",how="left",suffixes=("","_sample"))
    d["pressure_balls"]=d["pressure_balls"].fillna(d.get("pressure_balls",0)).fillna(0)
    d["pressure_matches"]=_num(d,"pressure_matches").fillna(0)
    d["eligible"]= (d.pressure_balls>=BATTER_MIN_BALLS)&(d.pressure_matches>=MIN_PRESSURE_MATCHES)
    # Smoothed pressure rates shrink toward each player's normal rate.
    for metric, exposure, prior in [
        ("strike_rate","pressure_balls",PRIOR_BALLS),
        ("dot_ball_pct","pressure_balls",PRIOR_BALLS),
        ("boundary_pct","pressure_balls",PRIOR_BALLS),
        ("dismissal_rate_pct","pressure_balls",PRIOR_BALLS),
    ]:
        p=_num(d,f"pressure_{metric}")
        n=_num(d,f"normal_{metric}")
        d[f"shrunk_pressure_{metric}"],d[f"{metric}_reliability_weight"]=_shrink_rate(p,n,_num(d,exposure).fillna(0),prior)
        d[f"adjusted_{metric}_delta"]=d[f"shrunk_pressure_{metric}"]-n
    d["sr_component"]=d["adjusted_strike_rate_delta"]
    d["dot_component"]=-d["adjusted_dot_ball_pct_delta"]
    d["boundary_component"]=d["adjusted_boundary_pct_delta"]
    d["dismissal_component"]=-d["adjusted_dismissal_rate_pct_delta"]
    specs=[("sr_component",True),("dot_component",True),("boundary_component",True),("dismissal_component",True)]
    z=_score_components(d,specs)
    for k,v in z.items(): d["z_"+k]=v
    # Match consistency: reward higher mean pressure SR, penalize volatility via uncertainty not extra score.
    d=d.drop(columns=["pressure_match_count","match_metric_mean","match_metric_std","match_metric_median"],errors="ignore")
    d=d.merge(consistency[["player_id","pressure_match_count","match_metric_mean","match_metric_std","match_metric_median"]],
              left_on="striker_id",right_on="player_id",how="left")
    d["match_metric_se"]=d["match_metric_std"]/np.sqrt(d["pressure_match_count"].clip(lower=1))
    d["match_metric_ci_low"]=d["match_metric_mean"]-1.96*d["match_metric_se"]
    d["match_metric_ci_high"]=d["match_metric_mean"]+1.96*d["match_metric_se"]
    d["uncertainty_flag"]=np.select(
        [d.pressure_balls<60,d.pressure_match_count<8,d.match_metric_se.isna()],
        ["low_exposure","few_pressure_matches","insufficient_match_variance"],default="standard"
    )
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
    d["eligible"]=(d.pressure_legal_balls>=BOWLER_MIN_LEGAL_BALLS)&(d.pressure_matches>=MIN_PRESSURE_MATCHES)
    # Shrink pressure rates toward the player's normal rates. For economy/dot/boundary rates,
    # exposure is legal balls; wickets per over uses the same exposure proxy.
    for metric in ["economy","dot_ball_pct","wickets_per_over","boundary_conceded_pct","charged_extras_per_over"]:
        p=_num(d,f"pressure_{metric}"); n=_num(d,f"normal_{metric}")
        d[f"shrunk_pressure_{metric}"],d[f"{metric}_reliability_weight"]=_shrink_rate(p,n,_num(d,"pressure_legal_balls").fillna(0),PRIOR_LEGAL_BALLS)
        d[f"adjusted_{metric}_delta"]=d[f"shrunk_pressure_{metric}"]-n
    d["economy_component"]=-d["adjusted_economy_delta"]
    d["dot_component"]=d["adjusted_dot_ball_pct_delta"]
    d["wicket_component"]=d["adjusted_wickets_per_over_delta"]
    d["boundary_component"]=-d["adjusted_boundary_conceded_pct_delta"]
    d["extras_component"]=-d["adjusted_charged_extras_per_over_delta"]
    specs=[("economy_component",True),("dot_component",True),("wicket_component",True),("boundary_component",True),("extras_component",True)]
    z=_score_components(d,specs)
    for k,v in z.items(): d["z_"+k]=v
    d=d.drop(columns=["pressure_match_count","match_metric_mean","match_metric_std","match_metric_median"],errors="ignore")
    d=d.merge(consistency[["player_id","pressure_match_count","match_metric_mean","match_metric_std","match_metric_median"]],
              left_on="bowler_id",right_on="player_id",how="left")
    d["match_metric_se"]=d["match_metric_std"]/np.sqrt(d["pressure_match_count"].clip(lower=1))
    d["match_metric_ci_low"]=d["match_metric_mean"]-1.96*d["match_metric_se"]
    d["match_metric_ci_high"]=d["match_metric_mean"]+1.96*d["match_metric_se"]
    d["uncertainty_flag"]=np.select(
        [d.pressure_legal_balls<60,d.pressure_match_count<8,d.match_metric_se.isna()],
        ["low_exposure","few_pressure_matches","insufficient_match_variance"],default="standard"
    )
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
    x=df.loc[df.eligible].copy().sort_values(rating_col,ascending=False)
    x["provisional_rank"]=range(1,len(x)+1)
    cols=[id_col,name_col,"provisional_rank",rating_col,"pressure_balls" if "pressure_balls" in x else "pressure_legal_balls",
          "pressure_matches","uncertainty_flag","match_metric_mean","match_metric_std","match_metric_ci_low","match_metric_ci_high"]
    return x[[c for c in cols if c in x.columns]]

def _sensitivity(df, id_col, rating_cols, role):
    base=df.loc[df.eligible].sort_values("rating_balanced",ascending=False)
    base_ids=base[id_col].tolist()
    rows=[]
    for col in rating_cols:
        ranked=df.loc[df.eligible].sort_values(col,ascending=False)
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
        elig=df[(df[exposure]>=threshold)&(df.pressure_matches>=MIN_PRESSURE_MATCHES)].sort_values("rating_balanced",ascending=False)
        n=min(10,len(base_ids),len(elig))
        overlap=len(set(base_ids[:n])&set(elig[id_col].head(n)))/max(n,1)
        rows.append({"role":role,"scheme":f"min_exposure_{threshold}","top10_overlap_vs_balanced":overlap,"rank_order_correlation":np.nan})
    return pd.DataFrame(rows)

def run_phase4(outputs:Path,reports:Path):
    outputs,reports=Path(outputs),Path(reports)
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
    # Compact top 20 review sheets (not final Unstop lists).
    brank.head(20).to_csv(outputs/"provisional_batter_top20_review.csv",index=False)
    wrank.head(20).to_csv(outputs/"provisional_bowler_top20_review.csv",index=False)
    summary={
        "batter_candidates_eligible":int(br.eligible.sum()),
        "bowler_candidates_eligible":int(wr.eligible.sum()),
        "batter_min_pressure_balls":BATTER_MIN_BALLS,
        "bowler_min_pressure_legal_balls":BOWLER_MIN_LEGAL_BALLS,
        "minimum_pressure_matches":MIN_PRESSURE_MATCHES,
        "prior_exposure_balls":PRIOR_BALLS,
        "prior_exposure_legal_balls":PRIOR_LEGAL_BALLS,
        "rankings_status":"provisional_review_only",
        "final_unstop_top10_created":False
    }
    with open(outputs/"phase4_summary.json","w",encoding="utf-8") as f:json.dump(summary,f,indent=2)
    reports.mkdir(parents=True,exist_ok=True)
    lines=[
        "# PRESSURE-X Phase 4 — Rating, Reliability and Sensitivity","",
        "## Eligibility",
        f"- Batters: at least {BATTER_MIN_BALLS} pressure balls and {MIN_PRESSURE_MATCHES} pressure matches.",
        f"- Bowlers: at least {BOWLER_MIN_LEGAL_BALLS} pressure legal balls and {MIN_PRESSURE_MATCHES} pressure matches.",
        "- These are transparent working thresholds for review, not universal statistical standards.",
        "",
        "## Shrinkage and normalization",
        f"- Pressure rates are shrunk toward each player's normal rate with prior exposure of {PRIOR_BALLS:.0f} balls/legal balls.",
        "- Reliability weight = exposure / (exposure + prior exposure).",
        "- Direction-aware metric deltas are converted to robust z-scores using median and MAD (fallback to standard deviation), clipped at +/-3.",
        "- Positive components always mean improvement under pressure.",
        "",
        "## Rating schemes",
        "- Batters: balanced, scoring-impact, survival and equal weights.",
        "- Bowlers: balanced, wicket-impact, control and equal weights.",
        "- Balanced score is the provisional default; alternative schemes are used for sensitivity checks.",
        "",
        "## Uncertainty and consistency",
        "- Match-level pressure strike rate (batters) and economy (bowlers) have mean, median, standard deviation and an approximate 95% interval around the mean using mean +/- 1.96*SD/sqrt(matches).",
        "- The interval is descriptive and assumes independent match observations; it is not a formal Bayesian posterior interval.",
        "- Low-exposure and few-match flags are retained in review tables.",
        "",
        "## Sensitivity",
        "- Top-10 overlap and rank-order correlation are compared across weight schemes.",
        "- Eligibility sensitivity is checked at 20, 30, 45, 60 and 90 pressure balls/legal balls while holding minimum matches constant.",
        "",
        "## Important caveats",
        "- Phase 2 pressure labels and Phase 3 metric semantics flow through unchanged; this phase does not independently revalidate scorecards.",
        "- The composite score is a transparent relative index, not a probability of success or an objective measure of player talent.",
        "- Provisional rankings must be manually reviewed for exposure, role/context and anomalous metric values before submission.",
        "- No final Unstop Top 10 is generated.",
        "",
        "## Outputs",
        "- `batter_ratings_all.csv`, `bowler_ratings_all.csv`",
        "- `provisional_batter_rankings.csv`, `provisional_bowler_rankings.csv`",
        "- `provisional_batter_top20_review.csv`, `provisional_bowler_top20_review.csv`",
        "- `ranking_sensitivity.csv`, `phase4_summary.json`"
    ]
    (reports/"phase4_findings.md").write_text("\\n".join(lines),encoding="utf-8")
    return summary
