# PRESSURE-X — Phase 1: Data Audit & Exploratory Analysis

This phase inventories and profiles the six CSV tables supplied for SupeRR Selector Season 2. It deliberately does **not** create pressure labels or player rankings.

## Requirements
- Python 3.10–3.12 recommended
- Windows PowerShell or Command Prompt
- The six original CSV files in `data/raw/`

## Windows setup

Open PowerShell in the `PRESSURE-X` folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run Phase 1

```powershell
python run_phase1.py
```

The first run reads the full ball-by-ball file and may take a little time. It creates outputs under `outputs/`.

## Expected source files

```text
data/raw/
  competitions.csv
  teams.csv
  matches.csv
  ball_by_ball.csv
  competition_team_player_mapping.csv
  playing_eleven.csv
```

If you need to extract the supplied ZIP manually, extract the six CSVs from its `Data Pack` folder into `data/raw/`. Do not put the ZIP itself in `data/raw/`.

## Main outputs

- `dataset_audit.json` — machine-readable audit summary.
- `*_column_profile.csv` — per-table column, dtype, missingness and uniqueness profile.
- `matches_by_format_season.csv` — matches by format and season.
- `competition_profile.csv` — competition metadata profile.
- `batter_participation_eda.csv` — striker delivery-row and recorded-run summaries.
- `bowler_participation_eda.csv` — bowler delivery-row and wicket-event summaries.
- `innings_profile.csv` — innings-level descriptive profile.
- `extras_type_profile.csv` — extras label distribution.
- `competition_formats.png`, `competition_seasons.png` — quick charts.

## Important interpretation safeguards

1. `delivery_rows` is not yet called legal balls or balls faced. Wides and no-balls need correct treatment.
2. The `runs`, `extras1_runs`, and `extras_2_runs` fields are profiled separately. Do not assume their exact scoring semantics until the data dictionary or targeted row validation confirms them.
3. Missing dismissal and extras labels can be structurally normal; they are not automatically data errors.
4. The audit keeps all competition formats visible. The problem statement references IPL and T20I, while the pack includes T20 competitions. Competition eligibility must be explicitly decided before ranking.
5. Innings 3 and 4 appear in the ball-by-ball file; investigate these as possible Super Overs before applying normal innings logic.
6. Phase 1 counts and profiles are descriptive only. They are not player performance ratings.

## Reproducibility

Keep the original raw CSV files unchanged. All generated profiles and charts are written to `outputs/`.


## Phase 2 — Pressure classification

Run `python run_phase2.py` after Phase 1 dependencies are installed. This reconstructs delivery-level pre-ball match state, treats `wide` and `Overstep` as illegal deliveries, excludes innings 3/4 from regulation pressure labels, and writes pressure outputs under `outputs/`. See `reports/phase2_findings.md` and `outputs/scoring_semantics_audit.json` for assumptions and observed data patterns.


## Phase 3 — Player performance analysis

Run after Phase 2:

```powershell
python run_phase3.py
```

Phase 3 reads `outputs/pressure_classified_deliveries.csv` and writes player-level pressure-versus-normal metrics, match-level consistency summaries, sample-size reports, and scoring-treatment audits into `outputs/`. It does **not** generate final player rankings.

### Phase 3 outputs

- `batting_pressure_vs_normal.csv` — player batting metrics split into pressure and normal groups.
- `bowling_pressure_vs_normal.csv` — player bowling metrics split into pressure and normal groups.
- `batting_player_group_metrics.csv` / `bowling_player_group_metrics.csv` — long-form group-level aggregates.
- `batting_match_consistency.csv` / `bowling_match_consistency.csv` — match-level pressure metric mean, median and standard deviation.
- `batting_sample_size_report.csv` / `bowling_sample_size_report.csv` — pressure exposure counts for later eligibility and reliability adjustments.
- `phase3_extras_treatment.csv` / `phase3_dismissal_treatment.csv` — transparent treatment audits.
- `phase3_summary.json` — execution summary.
- `reports/phase3_findings.md` — methodology and limitations.

### Performance definitions

- Pressure deliveries: Phase 2 `high` and `very_high`.
- Normal deliveries: Phase 2 `low` and `moderate`.
- Batter balls faced: excludes wides; includes Overstep/no-ball deliveries.
- Bowler legal balls: excludes wides and Overstep.
- Bowler wickets: caught, bowled, LBW, stump and hit-wicket dismissal types; run-outs, retired-out and obstructing-field dismissals are not credited.
- Bowler-conceded runs: batter runs plus wide/Overstep extras; byes, leg-byes and penalty extras are excluded. Ambiguous `other` extras are not charged to the bowler.
- A source anomaly (one leg-byes-labelled row with `runs=1` and zero extra runs) is flagged and not charged to the bowler.

Run all tests:

```powershell
python -m pytest -v
```


## Phase 4 — Statistical ratings and reliability

Run after Phase 3:

```powershell
python run_phase4.py
```

Phase 4 produces provisional review rankings only. It does not create the final Unstop Top 10.

### Current working eligibility
- Batters: at least 30 pressure balls across at least 5 pressure matches.
- Bowlers: at least 30 pressure legal balls across at least 5 pressure matches.

### Statistical method
- Pressure rates shrink toward each player's own normal rate using exposure/(exposure + 60).
- Direction-aware pressure-vs-normal deltas are robust-standardized using median/MAD, with clipping at +/-3.
- Multiple weight schemes are compared for batting and bowling.
- Match-level mean, standard deviation and approximate 95% intervals are reported.
- Sensitivity tests compare alternative weights and minimum exposure thresholds.

### Phase 4 outputs
- `batter_ratings_all.csv`, `bowler_ratings_all.csv`
- `provisional_batter_rankings.csv`, `provisional_bowler_rankings.csv`
- `provisional_batter_top20_review.csv`, `provisional_bowler_top20_review.csv`
- `ranking_sensitivity.csv`
- `phase4_summary.json`
- `reports/phase4_findings.md`

The ratings are relative analytical indices, not probabilities. Eligibility thresholds and weights must be reviewed before final submission.


## Phase 4.1 — competition scope, baseline eligibility and reliability

Phase 4.1 supersedes the earlier Phase 4 runner. Run:

```powershell
python run_phase4.py
```

The runner now:
- filters the analysis to IPL and T20I competitions only, as stated in the original challenge brief;
- rebuilds Phase 3 performance tables on that scoped delivery set;
- requires both pressure and normal exposure (batters: 30 balls and 3 normal matches; bowlers: 30 legal balls and 3 normal matches), in addition to the existing pressure thresholds;
- excludes missing/non-finite ratings from ranked outputs;
- calculates ball-weighted match-level consistency summaries;
- reports reliability tiers and sensitivity on the scoped eligible pool.

All rankings remain provisional. Phase 4.1 does **not** create a final Unstop Top 10.

## Phase 4.2 — Two-sample reliability and consistency refinement

Run `python run_phase4.py` after Phase 1 and Phase 2 have been completed. Phase 4 reruns Phase 3 on the IPL/T20I-only delivery subset and regenerates the player metrics and rankings.

Phase 4.2 refinements:
- Pressure-vs-normal metric differences are discounted using separate pressure and normal exposure weights: `n / (n + 60)` for each sample. Their product scales the observed difference. This is a transparent reliability heuristic, not a formal Bayesian posterior or inferential confidence interval.
- The consistency-table merge now removes overlapping pre-existing columns before merging, preserving one canonical set of weighted match metrics.
- Weighted match mean and dispersion are retained as descriptive consistency diagnostics. The project no longer reports pseudo-confidence intervals derived from weighted match-level aggregates.
- `stronger` reliability requires at least 120 pressure balls/legal balls, 120 normal balls/legal balls, 10 pressure matches and 5 normal matches. Eligible candidates below any of these thresholds are marked `limited`.
- Expanded top-20 review CSVs retain pressure and normal metrics, adjusted deltas, component scores, exposure, reliability and consistency fields.

Key Phase 4.2 outputs:
- `provisional_batter_rankings.csv`, `provisional_bowler_rankings.csv`
- `provisional_batter_top20_review.csv`, `provisional_bowler_top20_review.csv`
- `batter_ratings_all.csv`, `bowler_ratings_all.csv`
- `ranking_sensitivity.csv`, `phase4_summary.json`
- `reports/phase4_2_findings.md`

Run tests with `python -m pytest -v`. Rankings remain provisional; no final Unstop Top 10 is generated.


## Phase 4.3 — Candidate Validation Review

Phase 4.3 adds review artifacts without changing the Phase 4.2 scoring engine or creating a final Unstop Top 10.

Run the reproducible review-table generator after Phase 4 has been run:

```powershell
python run_phase4_3_review.py
```

Key deliverables:

- `reports/phase4_3_candidate_validation.md` — interpretation, candidate risks and recommended review protocol.
- `reports/PRESSURE-X_Phase4.3_Candidate_Validation.xlsx` — workbook with scope summary, all-eligible top 20s, stronger-tier shortlists, rank comparisons across weighting schemes and sensitivity results.
- `outputs/phase4_3_*` — CSV review tables and summary JSON.

The stronger-reliability-only lists are diagnostic shortlists, not replacement rankings. Final selection remains provisional and must be made only after reviewing the source metrics and competition requirements.


## Phase 4.5 — Format and Season Fairness Analysis

Run this after the Phase 4.4 outputs have been generated:

```powershell
python run_phase4_5_review.py
```

Phase 4.5 reruns Phase 3 and the Phase 4 rating logic separately for each IPL competition year and T20I calendar year. It creates format-year ranking tables and recurrence diagnostics for the pooled Top 10.

Outputs:
- `reports/phase4_5_format_season_fairness.md`
- `reports/PRESSURE-X_Phase4.5_Format_Season_Fairness.xlsx`
- `outputs/phase4_5_format_year_summary.csv`
- `outputs/phase4_5_batter_year_top10.csv`
- `outputs/phase4_5_bowler_year_top10.csv`
- `outputs/phase4_5_pooled_batter_season_stability.csv`
- `outputs/phase4_5_pooled_bowler_season_stability.csv`

Important: scores are re-standardized within each format-year subset. Compare recurrence and rank positions within a subset; do not compare raw rating values across formats or years. Phase 4.5 is an audit, not a final selection phase.


## Phase 4.6 — Combined IPL/T20I Candidate Evidence Review

Run after Phase 4 has generated the scoped pressure-classified deliveries and candidate files:

```powershell
python run_phase4_6_review.py
```

This creates format-specific candidate metrics for the pooled Top-20 batter and bowler pools, plus format exposure shares. It does **not** create a new composite rating or final Top 10. The pooled balanced rating remains the provisional ordering; format-specific ratings are within-format diagnostics and must not be averaged or compared numerically across formats.

Key outputs:
- `outputs/phase4_6_batter_format_evidence.csv`
- `outputs/phase4_6_bowler_format_evidence.csv`
- `outputs/phase4_6_batter_format_metrics_long.csv`
- `outputs/phase4_6_bowler_format_metrics_long.csv`
- `outputs/phase4_6_summary.json`
- `reports/phase4_6_combined_format_candidate_review.md`
- `reports/PRESSURE-X_Phase4.6_Combined_Format_Evidence.xlsx`


## Phase 4.7 — Candidate-by-Candidate Review

Run:

```powershell
python run_phase4_7_review.py
```

This generates the two candidate review CSVs for the pooled Top-20 batter and bowler pools. The review rubric prioritizes candidates for human review; it is not a new scoring model and does not automatically accept or reject players. See `reports/phase4_7_candidate_by_candidate_review.md` and `reports/PRESSURE-X_Phase4.7_Candidate_Review.xlsx` for the complete rationale and evidence. No final Top 10 is created.


## Phase 4.8 — Match-Level Candidate Evidence Validation

Run:

```powershell
python run_phase4_8_review.py
```

This reconstructs pressure/normal metrics per player per match for the pooled Top-15 batter and bowler candidate pools. It creates candidate-level median comparisons and match-level records. It is a diagnostic validation layer, not a new rating model; it does not create the final Top 10.

See `reports/phase4_8_match_level_candidate_validation.md` and `reports/PRESSURE-X_Phase4.8_Match_Level_Validation.xlsx`.


## Phase 4.9 — Final Cut-Line Challenge

Run:

```powershell
python run_phase4_9_review.py
```

Compares the rank-10 incumbent against every rank-11-to-20 challenger for batters and bowlers. Uses the balanced rating gap, alternate weighting sensitivity, reliability tier, uncertainty flags and match-level median diagnostics. It does not generate final Top-10 lists. See `reports/phase4_9_final_cutline_challenge.md` and `reports/PRESSURE-X_Phase4.9_Cutline_Challenge.xlsx`.
