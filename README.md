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
