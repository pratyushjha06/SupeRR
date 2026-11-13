# PRESSURE-X Phase 5 — Cut-line governance and submission readiness

## Purpose and boundary
This phase formalises how close rank-10/rank-11 decisions are discussed. It does not change the Phase 4 balanced-rating formula, eligibility thresholds, pressure labels, or underlying candidate ranks. It does not publish a final Top 10.

## Pre-declared practical-tie policy
The balanced rating remains the primary ranking measure. For governance review only, a rank-10/rank-11 rating gap of **0.001 points or less** is treated as a practical tie. This is an analyst-selected tolerance for avoiding false precision in nearly identical displayed scores; it is **not** a confidence interval, p-value, or claim of statistical equivalence.

Within that band, apply this order:
1. Stronger reliability tier.
2. Greater pressure exposure (legal balls for bowlers; balls faced for batters).
3. More pressure-exposure matches.
4. More favourable match-level median components.
5. If still tied, retain the higher unrounded balanced rating.

Outside the band, retain the balanced-rating order and explain the challenger as a cut-line sensitivity, not a tie.

## Batter cut-line: Aiden Markram vs Dasun Shanaka
- Balanced-rating gap (incumbent minus challenger): **0.014353**.
- Practical-tie tolerance: **0.001**.
- Reliability: incumbent **stronger**; challenger **stronger**.
- Match-level favourable components: incumbent **3/4**; challenger **3/4**.
- Decision: **retain Aiden Markram provisionally**. The gap is outside the practical-tie band, and the incumbent remains ahead under the alternative weighting checks recorded in Phase 4.9. Explicitly disclose Dasun Shanaka as the closest challenger.

## Bowler cut-line: Anshul Kamboj vs Sai Kishore
- Balanced-rating gap (incumbent minus challenger): **0.00004566** — inside the practical-tie band.
- Strict balanced-score order: **Anshul Kamboj** remains rank 10, ahead by a tiny amount.
- Both candidates have **limited** reliability; do not describe either as high-confidence.
- Pressure exposure: Anshul Kamboj **85 legal balls / 8 matches**; Sai Kishore **98 legal balls / 10 matches**.
- Match-level favourable components: Anshul Kamboj **3/4**; Sai Kishore **4/4**.
- Supporting descriptive context: pressure economy Anshul Kamboj **8.188** vs Sai Kishore **7.286**; pressure wickets/over **0.706** vs **0.735**.
- Governance recommendation under the declared tie policy: **Sai Kishore**. Keep the strict score rank and governance recommendation separately visible; if the submission requires a single ordered list, state this tie-break rule in the methodology before presenting the list. The data do not justify claiming a decisive performance gap.

## Interpretation and limitations
- Match-level medians are descriptive robustness evidence, not causal proof or a significance test.
- The rating gap alone does not quantify uncertainty. Reliability tiers and exposure counts must accompany the decision.
- The tolerance is a transparent editorial rule. A reviewer can reproduce the result and challenge the tolerance without altering raw metrics.
- Format/season analyses remain separate evidence. Independently standardised format-year scores must not be averaged as if they shared one scale.
- Some individual years lack enough eligible batters for a full Top 10 under the existing thresholds; do not lower thresholds silently.
- IPL and T20I are the in-scope competitions. Out-of-scope T20 competitions remain excluded.

## Submission-readiness checklist
- [ ] State the IPL/T20I scope and date range exactly as defined by the supplied data.
- [ ] Define pressure states and explain the innings-specific pressure calculation.
- [ ] Explain batter and bowler metric definitions, including wides, oversteps, extras, dismissals, and credited wickets.
- [ ] Show normal vs pressure baselines, sample sizes, reliability tiers, and uncertainty flags for every selected player.
- [ ] Explain the rating components, directionality, shrinkage, robust standardisation, and balanced weights.
- [ ] Report alternate-weighting and exposure-threshold sensitivity without averaging those rankings into the main score.
- [ ] Include format/season coverage and explain years with fewer than ten eligible batters.
- [ ] Include match-level validation as supporting evidence, not causal inference.
- [ ] Disclose the rank-10/rank-11 cut-line comparisons and the pre-declared tie policy.
- [ ] Re-run scripts and tests from the clean project folder before submission.

## Files generated
- `outputs/phase5_cutline_governance_decisions.csv`
- `outputs/phase5_governance_decisions.json`
- `reports/phase5_cutline_governance_and_readiness.md`
