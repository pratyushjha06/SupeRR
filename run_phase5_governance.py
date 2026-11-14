from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
REPORTS = ROOT / 'reports'
TOLERANCE = 0.001  # pre-declared governance tolerance; not a statistical interval


def main():
    batter_cut = pd.read_csv(OUT / 'phase4_9_batter_cutline_challengers.csv')
    bowler_cut = pd.read_csv(OUT / 'phase4_9_bowler_cutline_challengers.csv')
    batter_pool = pd.read_csv(OUT / 'phase4_7_batter_candidate_review.csv')
    bowler_pool = pd.read_csv(OUT / 'phase4_7_bowler_candidate_review.csv')

    b = batter_cut.loc[batter_cut.omitted_rank.eq(11)].iloc[0]
    w = bowler_cut.loc[bowler_cut.omitted_rank.eq(11)].iloc[0]
    b_inc = batter_pool.loc[batter_pool.striker_name.eq(b.cutoff_candidate)].iloc[0]
    b_ch = batter_pool.loc[batter_pool.striker_name.eq(b.omitted_candidate)].iloc[0]
    w_inc = bowler_pool.loc[bowler_pool.bowler_name.eq(w.cutoff_candidate)].iloc[0]
    w_ch = bowler_pool.loc[bowler_pool.bowler_name.eq(w.omitted_candidate)].iloc[0]

    b_gap = float(b.balanced_rating_gap_vs_cutoff)
    w_gap = float(w.balanced_rating_gap_vs_cutoff)
    b_tie = abs(b_gap) <= TOLERANCE
    w_tie = abs(w_gap) <= TOLERANCE

    # Governance does not silently replace the score ordering. A practical tie
    # only triggers a separately disclosed evidence review.
    decisions = [
        {
            'role': 'batter', 'strict_score_rank10': b.cutoff_candidate,
            'rank11_challenger': b.omitted_candidate,
            'balanced_rating_gap_rank10_minus_rank11': b_gap,
            'practical_tie_tolerance': TOLERANCE, 'within_practical_tie_band': bool(b_tie),
            'rank10_reliability': str(b_inc.reliability_tier),
            'rank11_reliability': str(b_ch.reliability_tier),
            'rank10_pressure_exposure': int(b_inc.pressure_balls),
            'rank11_pressure_exposure': int(b_ch.pressure_balls),
            'rank10_pressure_matches': int(b_inc.pressure_matches),
            'rank11_pressure_matches': int(b_ch.pressure_matches),
            'rank10_match_evidence': str(b.cutoff_match_favourable),
            'rank11_match_evidence': str(b.omitted_match_favourable),
            'alternate_weight_gaps': {
                'scoring_impact': float(b.rating_scoring_impact_gap_vs_cutoff),
                'survival': float(b.rating_survival_gap_vs_cutoff),
                'equal': float(b.rating_equal_gap_vs_cutoff),
            },
            'governance_outcome': b.cutoff_candidate,
            'decision': 'retain balanced-score rank 10; disclose challenger reliability advantage' if not b_tie else 'review under pre-declared tie policy',
        },
        {
            'role': 'bowler', 'strict_score_rank10': w.cutoff_candidate,
            'rank11_challenger': w.omitted_candidate,
            'balanced_rating_gap_rank10_minus_rank11': w_gap,
            'practical_tie_tolerance': TOLERANCE, 'within_practical_tie_band': bool(w_tie),
            'rank10_reliability': str(w_inc.reliability_tier),
            'rank11_reliability': str(w_ch.reliability_tier),
            'rank10_pressure_exposure': int(w_inc.pressure_legal_balls),
            'rank11_pressure_exposure': int(w_ch.pressure_legal_balls),
            'rank10_pressure_matches': int(w_inc.pressure_matches),
            'rank11_pressure_matches': int(w_ch.pressure_matches),
            'rank10_match_evidence': str(w.cutoff_match_favourable),
            'rank11_match_evidence': str(w.omitted_match_favourable),
            'alternate_weight_gaps': {
                'wicket_impact': float(w.rating_wicket_impact_gap_vs_cutoff),
                'control': float(w.rating_control_gap_vs_cutoff),
                'equal': float(w.rating_equal_gap_vs_cutoff),
            },
            'rank10_pressure_economy': float(w_inc.pressure_economy),
            'rank11_pressure_economy': float(w_ch.pressure_economy),
            'rank10_pressure_wickets_per_over': float(w_inc.pressure_wickets_per_over),
            'rank11_pressure_wickets_per_over': float(w_ch.pressure_wickets_per_over),
            'governance_outcome': w.cutoff_candidate,
            'decision': 'retain balanced-score rank 10; disclose challenger match-level advantage' if not w_tie else 'review under pre-declared tie policy',
        },
    ]
    OUT.mkdir(exist_ok=True); REPORTS.mkdir(exist_ok=True)
    pd.DataFrame(decisions).to_csv(OUT / 'phase5_cutline_governance_decisions.csv', index=False)
    policy = ('Balanced rating remains the primary ordering. A rank-10/rank-11 gap no larger than '
              f'{TOLERANCE:.3f} points triggers governance review; this is an analyst-selected '
              'tolerance, not a confidence interval or significance test. Outside that band, '
              'retain the balanced-score order and disclose reliability, match evidence and '
              'alternative-weight results for the challenger.')
    payload = {'practical_tie_tolerance_rating_points': TOLERANCE,
               'policy': policy, 'decisions': decisions,
               'caveat': 'This is a ranking-governance rule, not statistical evidence of equivalence.',
               'important_caveat': 'The practical-tie tolerance is analyst-selected and is not a statistically estimated confidence interval.'}
    (OUT / 'phase5_governance_decisions.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')

    report = f'''# PRESSURE-X Phase 5 — Cut-line governance (recomputed after leakage correction)

## Governance rule

The balanced rating is the primary ordering. A rank-10/rank-11 gap of **{TOLERANCE:.3f} points or less** triggers a practical-tie evidence review. This tolerance is analyst-selected; it is not a confidence interval, p-value, or claim of statistical equivalence. Outside that band, retain the balanced-score ordering and disclose the challenger evidence.

## Batter cut-line

- Rank 10: **{b.cutoff_candidate}** ({b.cutoff_reliability} reliability)
- Rank 11 challenger: **{b.omitted_candidate}** ({b.omitted_reliability} reliability)
- Balanced rating gap: **{b_gap:.6f}**; practical tie: **{b_tie}**
- Pressure exposure: {b.cutoff_candidate} {int(b_inc.pressure_balls)} balls / {int(b_inc.pressure_matches)} matches; {b.omitted_candidate} {int(b_ch.pressure_balls)} balls / {int(b_ch.pressure_matches)} matches.
- Match-level favourable components: {b.cutoff_candidate} {b.cutoff_match_favourable}; {b.omitted_candidate} {b.omitted_match_favourable}.
- Alternative-weight gaps (rank 10 minus rank 11): scoring-impact {float(b.rating_scoring_impact_gap_vs_cutoff):.6f}; survival {float(b.rating_survival_gap_vs_cutoff):.6f}; equal {float(b.rating_equal_gap_vs_cutoff):.6f}.
- Governance outcome: retain **{b.cutoff_candidate}** by the primary balanced rating. Disclose that the omitted challenger has a stronger reliability tier; do not hide this trade-off.

## Bowler cut-line

- Rank 10: **{w.cutoff_candidate}** ({w.cutoff_reliability} reliability)
- Rank 11 challenger: **{w.omitted_candidate}** ({w.omitted_reliability} reliability)
- Balanced rating gap: **{w_gap:.6f}**; practical tie: **{w_tie}**
- Pressure exposure: {w.cutoff_candidate} {int(w_inc.pressure_legal_balls)} legal balls / {int(w_inc.pressure_matches)} matches; {w.omitted_candidate} {int(w_ch.pressure_legal_balls)} legal balls / {int(w_ch.pressure_matches)} matches.
- Match-level favourable components: {w.cutoff_candidate} {w.cutoff_match_favourable}; {w.omitted_candidate} {w.omitted_match_favourable}.
- Alternative-weight gaps (rank 10 minus rank 11): wicket-impact {float(w.rating_wicket_impact_gap_vs_cutoff):.6f}; control {float(w.rating_control_gap_vs_cutoff):.6f}; equal {float(w.rating_equal_gap_vs_cutoff):.6f}.
- Pressure economy: {w.cutoff_candidate} {float(w_inc.pressure_economy):.3f}; {w.omitted_candidate} {float(w_ch.pressure_economy):.3f}.
- Pressure wickets/over: {w.cutoff_candidate} {float(w_inc.pressure_wickets_per_over):.3f}; {w.omitted_candidate} {float(w_ch.pressure_wickets_per_over):.3f}.
- Governance outcome: retain **{w.cutoff_candidate}** by the primary balanced rating and disclose the challenger's stronger match-level evidence.

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
'''
    (REPORTS / 'phase5_cutline_governance_and_readiness.md').write_text(report, encoding='utf-8')
    print(json.dumps({'batter_rank10': b.cutoff_candidate, 'batter_rank11': b.omitted_candidate,
                      'batter_gap': b_gap, 'bowler_rank10': w.cutoff_candidate,
                      'bowler_rank11': w.omitted_candidate, 'bowler_gap': w_gap,
                      'tie_tolerance': TOLERANCE}, indent=2))

if __name__ == '__main__':
    main()
