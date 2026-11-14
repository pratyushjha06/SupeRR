# PRESSURE-X Phase 6 — Final technical audit after leakage correction

## Audit scope

The audit inspected the exact Phase 6 project archive, the original SupeRR Selector Season 2 Round 1 problem statement, the pressure engine, rating engine, governance runner, tests, reports, and submission documents. The official challenge requires two ordered Top-10 lists (batters and bowlers) and a methodology report covering pressure definition, performance metrics and baselines, fair comparisons, evidence for selected players, reliability and limitations.

## Findings and remediation

### Critical: first-innings par-rate future-information leakage — fixed

The previous implementation used the median final first-innings run rate from the entire competition-season. This allowed later matches, and potentially the current match's final outcome, to affect pressure scores for earlier deliveries.

The corrected implementation now:
- calculates final run rates from completed first innings;
- uses only matches with a strictly earlier match date in the same competition-season;
- excludes matches on the same date;
- requires at least three prior completed matches;
- uses a documented 8.0 runs-per-over fallback before sufficient history exists.

Two regression tests verify prior-date-only calculation and same-date exclusion. The full project was rerun from the original supplied data after the correction.

### Critical: stale Phase 5 governance runner — fixed

The original governance runner expected columns not present in the current Phase 4.8 output schema. It failed when rerun against the regenerated data. The runner now reads the candidate review and cut-line outputs directly, preserves the balanced-score order, and reports the actual rank-10/rank-11 exposure, reliability and match evidence.

### Submission documents — refreshed

The previous Phase 6 draft documents contained rankings and cut-line examples from the pre-correction run. They have been regenerated using the current candidate review outputs. The report and presentation now explicitly describe the leakage correction and use the recomputed provisional rankings.

## Recomputed pipeline results

- Original ball-by-ball rows: 200,999.
- Matches in match table: 883.
- Matches with ball-by-ball: 867; without ball-by-ball: 16.
- Date range in supplied match data: 2022-01-22 to 2026-11-01.
- In-scope IPL/T20I deliveries: 194,014.
- Excluded out-of-scope deliveries: 6,985.
- Eligible batter candidates after baseline requirements: 153.
- Eligible bowler candidates after baseline requirements: 209.
- Full pipeline: Phase 1, Phase 2, Phase 3, Phase 4, Phases 4.3–4.9 and Phase 5 governance regenerated.
- Automated tests: 40 passed.

## Recomputed rank-10/rank-11 cut lines

- Batter: Mark Chapman at rank 10; Ryan Burl at rank 11; balanced-rating gap 0.059202. Ryan Burl has a stronger reliability tier; Mark Chapman remains ahead in the balanced score and the tested alternate weighting gaps. This trade-off is explicitly disclosed.
- Bowler: Shardul Thakur at rank 10; Jamie Overton at rank 11; balanced-rating gap 0.055137. Both have stronger reliability. Jamie Overton has more favourable match-level median components (4/4 versus 3/4), but the balanced score remains the primary ordering and the gap is outside the 0.001 governance review band.

These names supersede the earlier draft cut-line examples (Aiden Markram/Dasun Shanaka and Anshul Kamboj/Sai Kishore), which were produced before the leakage correction.

## Current limitations and remaining work

- The pressure formula and component weights are heuristic design choices, not learned causal coefficients.
- The 8.0 runs-per-over fallback applies before three prior matches are available in a competition-season.
- Baseline matching does not fully control for batting position, player role, or every innings phase because the supplied fields do not provide complete reliable context for all players.
- Exposure-based shrinkage and reliability tiers are heuristics, not formal posterior estimates.
- No match-cluster bootstrap confidence intervals or causal estimates are claimed.
- Match-level medians are descriptive robustness diagnostics, not significance tests.
- Final Unstop dropdown selections must be confirmed by the user and made consistent with the final uploaded report.

## Verdict

The implementation is reproducible and all tests pass after the critical correction. The submission package is substantially safer than the previous draft, but the rankings should still be presented as provisional until the final selection decision is explicitly confirmed. No claim of guaranteed competition placement is appropriate.
