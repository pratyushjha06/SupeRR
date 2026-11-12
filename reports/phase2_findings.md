# PRESSURE-X Phase 2 — Pressure Classification

## Observed scoring semantics
- Ball-by-ball rows: 200,999
- `runs` is treated as batter runs; observed values range 0–6.
- Team runs per delivery are reconstructed as `runs + extras1_runs + extras_2_runs`.
- Wide rows: 7,714; Overstep rows: 576. Both are treated as illegal deliveries and do not consume a legal ball.
- Innings 3/4 rows (Super Overs): 38; excluded from regulation pressure scores.
- Wickets lost are reconstructed from the recorded `is_wicket` flag. Bowler-credit treatment is deferred to the bowling model.

## Pressure model
- First innings: 35% wicket-loss pressure, 35% innings progress, 30% scoring-rate deficit against competition-season median first-innings run rate.
- Chases: 35% required-run-rate intensity, 25% wickets lost, 20% time scarcity, 20% required-vs-current run-rate gap.
- Score bands: low (0–25), moderate (25–50), high (50–75), very high (75–100).
- These are transparent initial heuristic weights and require sensitivity analysis in later phases.

## Important limitations
- The data pack does not include a formal data dictionary. The field semantics above are inferred from observed row patterns.
- Revised target and revised overs are used when populated; otherwise a T20/T20I default of 20 overs is used.
- Innings 3 and 4 are treated as Super Overs based on the observed tied-match examples.
- First-innings par is estimated from median final run rate within competition-season. Sparse groups fall back to the overall median.
- Phase 2 labels match situation pressure, not an individual player's performance quality.

## Output files
- `pressure_classified_deliveries.csv`: delivery-level pre-ball state and pressure labels.
- `pressure_distribution.csv`: format/season/innings pressure distribution.
- `pressure_context_summary.csv`: pressure level summary.
- `scoring_semantics_audit.json`: observed scoring-field audit.