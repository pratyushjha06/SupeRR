# PRESSURE-X Phase 5 — Cut-line governance (recomputed after leakage correction)

## Governance rule

The balanced rating is the primary ordering. A rank-10/rank-11 gap of **0.001 points or less** triggers a practical-tie evidence review. This tolerance is analyst-selected; it is not a confidence interval, p-value, or claim of statistical equivalence. Outside that band, retain the balanced-score ordering and disclose the challenger evidence.

## Batter cut-line

- Rank 10: **Mark Chapman** (limited reliability)
- Rank 11 challenger: **Ryan Burl** (stronger reliability)
- Balanced rating gap: **0.059202**; practical tie: **False**
- Pressure exposure: Mark Chapman 99 balls / 9 matches; Ryan Burl 187 balls / 16 matches.
- Match-level favourable components: Mark Chapman 4/4; Ryan Burl 3/4.
- Alternative-weight gaps (rank 10 minus rank 11): scoring-impact 0.021855; survival 0.096549; equal 0.036424.
- Governance outcome: retain **Mark Chapman** by the primary balanced rating. Disclose that the omitted challenger has a stronger reliability tier; do not hide this trade-off.

## Bowler cut-line

- Rank 10: **Shardul Thakur** (stronger reliability)
- Rank 11 challenger: **Jamie Overton** (stronger reliability)
- Balanced rating gap: **0.055137**; practical tie: **False**
- Pressure exposure: Shardul Thakur 237 legal balls / 29 matches; Jamie Overton 153 legal balls / 14 matches.
- Match-level favourable components: Shardul Thakur 3/4; Jamie Overton 4/4.
- Alternative-weight gaps (rank 10 minus rank 11): wicket-impact 0.145268; control 0.285639; equal -0.306236.
- Pressure economy: Shardul Thakur 9.316; Jamie Overton 7.294.
- Pressure wickets/over: Shardul Thakur 0.532; Jamie Overton 0.588.
- Governance outcome: retain **Shardul Thakur** by the primary balanced rating and disclose the challenger's stronger match-level evidence.

## Important reanalysis note

The Phase 2 first-innings par-rate reference was corrected to use only completed first-innings matches with strictly earlier match dates in the same competition-season. At least three prior matches are required; otherwise a documented neutral fallback of 8.0 runs per over is used. All downstream phases were rerun from the original supplied data. Consequently, candidate ranks and cut-line gaps differ from the earlier Phase 5/6 draft; older draft ranking statements must not be reused.

## Limitations

- Match-level medians are descriptive robustness evidence, not causal proof or a significance test.
- Reliability tiers are exposure-based categories, not formal uncertainty intervals.
- IPL/T20I format-year scores are independently standardised and must not be averaged across subsets.
- Some format-year subsets do not have ten eligible batters under the fixed thresholds; thresholds are not silently relaxed.

## Output files

- `outputs/phase5_cutline_governance_decisions.csv`
- `outputs/phase5_governance_decisions.json`
