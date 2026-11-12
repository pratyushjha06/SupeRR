# PRESSURE-X Phase 3 — Player Performance Analysis

- Input deliveries: 200,999
- Eligible regulation deliveries: 200,904
- Batters with high/very-high pressure exposure: 729
- Bowlers with high/very-high pressure exposure: 506

## Batting methodology
- Batter runs use the observed `runs` field; team runs are `runs + extras1_runs + extras_2_runs`.
- Batter balls faced exclude wides and include Overstep/no-ball deliveries.
- Dismissals are attributed using `dismissed_player_id`, not assumed to be the striker. This captures non-striker run-outs.
- Batting metrics: strike rate, runs per ball, dot-ball percentage, boundary percentage and dismissal rate.

## Bowling methodology
- Legal balls exclude observed `wide` and `Overstep` delivery types.
- Bowler-conceded runs include batter runs plus wide/Overstep extras. Byes, leg-byes and penalty extras are excluded.
- `other` extra components are not charged to the bowler because their precise meaning is not documented; rows are separately flagged.
- The data contains one leg-byes-labelled row with `runs=1` and zero recorded extras. It is flagged as a source-semantic anomaly; the bowler-conceded calculation follows the leg-byes label and does not charge that run to the bowler. Batting `runs` remains source-field-based pending external scorecard verification.
- Credited wickets include caught, bowled, LBW, stump/stumped and hit wicket variants. Run-outs and retired-out/obstructing-field dismissals are not credited.
- Bowling metrics: economy, dot-ball percentage, wickets per over, boundary-conceded percentage and charged extras per over.

## Pressure vs normal
- Pressure = Phase 2 high + very_high labels; normal = low + moderate labels.
- Metrics are calculated separately for each group; this phase does not generate final player rankings.
- Match-level pressure strike rate (batting) and economy (bowling) are summarized using mean, median and standard deviation.

## Reliability and limitations
- Sample-size reports expose pressure balls/legal balls, runs, wickets and pressure-match counts.
- Minimum eligibility thresholds and shrinkage weights are deliberately deferred to Phase 4, where ranking sensitivity can be tested.
- `runs` and extras interpretation is inferred from observed rows because the pack has no formal data dictionary. Verify edge cases against official scorecards if possible.
- Unknown `other` extras are treated conservatively for bowler runs; results should be sensitivity-tested.
- Match-level consistency standard deviation is descriptive and should not be interpreted as a confidence interval.

## Outputs
- `batting_pressure_vs_normal.csv`, `bowling_pressure_vs_normal.csv`
- `batting_player_group_metrics.csv`, `bowling_player_group_metrics.csv`
- `batting_match_consistency.csv`, `bowling_match_consistency.csv`
- `batting_sample_size_report.csv`, `bowling_sample_size_report.csv`
- `phase3_extras_treatment.csv`, `phase3_dismissal_treatment.csv`
- No final top-10 rankings are generated in Phase 3.