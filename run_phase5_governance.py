from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
REPORTS = ROOT / 'reports'
TOLERANCE = 0.001  # pre-declared practical-tie band in rating points


def main():
    batter = pd.read_csv(OUT / 'phase4_9_batter_cutline_challengers.csv')
    bowler = pd.read_csv(OUT / 'phase4_9_bowler_cutline_challengers.csv')
    bm = pd.read_csv(OUT / 'phase4_8_batter_match_level_validation.csv')
    bw = pd.read_csv(OUT / 'phase4_8_bowler_match_level_validation.csv')

    b11 = batter.loc[batter.omitted_rank.eq(11)].iloc[0]
    w11 = bowler.loc[bowler.omitted_rank.eq(11)].iloc[0]
    a = bw.loc[bw.bowler_name.eq(w11.cutoff_candidate)].iloc[0]
    s = bw.loc[bw.bowler_name.eq(w11.omitted_candidate)].iloc[0]

    bowler_gap = float(w11.balanced_rating_gap_vs_cutoff)
    in_tie_band = abs(bowler_gap) <= TOLERANCE
    # Within the practical-tie band: compare reliability first, then pressure exposure,
    # then pressure-match count, then match-level favourable components. If still tied,
    # retain the higher unrounded balanced rating.
    tie_break = sorted(
        [a, s],
        key=lambda r: (
            1 if r.reliability_tier == 'stronger' else 0,
            float(r.pressure_legal_balls),
            float(r.pressure_matches),
            int(str(r.match_median_favourable_components).split('/')[0]),
            float(r.rating_balanced),
        ), reverse=True
    )
    practical_winner = tie_break[0].bowler_name if in_tie_band else w11.cutoff_candidate

    # Batter cutline remains a score-led decision: the gap exceeds the practical-tie band.
    batter_gap = float(b11.balanced_rating_gap_vs_cutoff)
    batter_status = 'retain incumbent; challenger outside practical-tie band' if abs(batter_gap) > TOLERANCE else 'apply tie-break review'

    decisions = [
        {'role':'batter','incumbent':b11.cutoff_candidate,'challenger':b11.omitted_candidate,
         'balanced_rating_gap_incumbent_minus_challenger':batter_gap,'practical_tie_band':TOLERANCE,
         'strict_score_order':b11.cutoff_candidate,'governance_outcome':b11.cutoff_candidate,
         'status':batter_status,'reliability_incumbent':b11.cutoff_reliability,
         'reliability_challenger':b11.omitted_reliability,
         'match_evidence_incumbent':b11.cutoff_match_favourable,
         'match_evidence_challenger':b11.omitted_match_favourable},
        {'role':'bowler','incumbent':w11.cutoff_candidate,'challenger':w11.omitted_candidate,
         'balanced_rating_gap_incumbent_minus_challenger':bowler_gap,'practical_tie_band':TOLERANCE,
         'strict_score_order':w11.cutoff_candidate,'governance_outcome':practical_winner if in_tie_band else w11.cutoff_candidate,
         'status':'practical tie; challenger preferred by exposure and match-level evidence; both limited' if in_tie_band else 'retain incumbent',
         'reliability_incumbent':w11.cutoff_reliability,'reliability_challenger':w11.omitted_reliability,
         'pressure_balls_incumbent':int(a.pressure_legal_balls),'pressure_balls_challenger':int(s.pressure_legal_balls),
         'pressure_matches_incumbent':int(a.pressure_matches),'pressure_matches_challenger':int(s.pressure_matches),
         'match_evidence_incumbent':a.match_median_favourable_components,
         'match_evidence_challenger':s.match_median_favourable_components,
         'pressure_economy_incumbent':float(a.pressure_economy),'pressure_economy_challenger':float(s.pressure_economy),
         'pressure_wickets_per_over_incumbent':float(a.pressure_wickets_per_over),'pressure_wickets_per_over_challenger':float(s.pressure_wickets_per_over)}
    ]
    OUT.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)
    pd.DataFrame(decisions).to_csv(OUT/'phase5_cutline_governance_decisions.csv', index=False)
    payload={'practical_tie_tolerance_rating_points':TOLERANCE,'decisions':decisions,
             'policy':'Balanced rating remains primary. If rank-10 and rank-11 candidates differ by no more than 0.001 rating points, treat them as practically tied for governance review; resolve by stronger reliability tier, then greater pressure exposure, then more pressure matches, then more favourable match-level median components; if still tied, retain higher unrounded balanced rating.',
             'important_caveat':'The 0.001 band is an explicit analyst-selected governance threshold, not a statistically estimated confidence interval. This is not a significance test and does not change the underlying rating formula.'}
    (OUT/'phase5_governance_decisions.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    report=f'''# PRESSURE-X Phase 5 — Cut-line governance and submission readiness

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

## Batter cut-line: {b11.cutoff_candidate} vs {b11.omitted_candidate}
- Balanced-rating gap (incumbent minus challenger): **{batter_gap:.6f}**.
- Practical-tie tolerance: **{TOLERANCE:.3f}**.
- Reliability: incumbent **{b11.cutoff_reliability}**; challenger **{b11.omitted_reliability}**.
- Match-level favourable components: incumbent **{b11.cutoff_match_favourable}**; challenger **{b11.omitted_match_favourable}**.
- Decision: **retain {b11.cutoff_candidate} provisionally**. The gap is outside the practical-tie band, and the incumbent remains ahead under the alternative weighting checks recorded in Phase 4.9. Explicitly disclose {b11.omitted_candidate} as the closest challenger.

## Bowler cut-line: {w11.cutoff_candidate} vs {w11.omitted_candidate}
- Balanced-rating gap (incumbent minus challenger): **{bowler_gap:.8f}** — inside the practical-tie band.
- Strict balanced-score order: **{w11.cutoff_candidate}** remains rank 10, ahead by a tiny amount.
- Both candidates have **limited** reliability; do not describe either as high-confidence.
- Pressure exposure: {w11.cutoff_candidate} **{int(a.pressure_legal_balls)} legal balls / {int(a.pressure_matches)} matches**; {w11.omitted_candidate} **{int(s.pressure_legal_balls)} legal balls / {int(s.pressure_matches)} matches**.
- Match-level favourable components: {w11.cutoff_candidate} **{a.match_median_favourable_components}**; {w11.omitted_candidate} **{s.match_median_favourable_components}**.
- Supporting descriptive context: pressure economy {w11.cutoff_candidate} **{a.pressure_economy:.3f}** vs {w11.omitted_candidate} **{s.pressure_economy:.3f}**; pressure wickets/over **{a.pressure_wickets_per_over:.3f}** vs **{s.pressure_wickets_per_over:.3f}**.
- Governance recommendation under the declared tie policy: **{practical_winner}**. Keep the strict score rank and governance recommendation separately visible; if the submission requires a single ordered list, state this tie-break rule in the methodology before presenting the list. The data do not justify claiming a decisive performance gap.

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
'''
    (REPORTS/'phase5_cutline_governance_and_readiness.md').write_text(report,encoding='utf-8')
    print(json.dumps({'tolerance':TOLERANCE,'batter_gap':batter_gap,'bowler_gap':bowler_gap,'bowler_strict_rank10':w11.cutoff_candidate,'bowler_governance_recommendation':practical_winner,'report':str(REPORTS/'phase5_cutline_governance_and_readiness.md')},indent=2))

if __name__ == '__main__':
    main()
