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
