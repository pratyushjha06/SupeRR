# PRESSURE-X Phase 4.1 — Scope, Baseline and Reliability Engine

## Competition scope
- The original problem statement specifies IPL and T20I data. Phase 4.1 filters to those competitions only.
- Classified deliveries before filter: 200,999; after filter: 194,014; excluded: 6,985.

## Eligibility
- Batters: >= 30 pressure balls, >= 5 pressure matches, >= 30 normal balls, >= 3 normal matches.
- Bowlers: >= 30 pressure legal balls, >= 5 pressure matches, >= 30 normal legal balls, >= 3 normal matches.
- Pressure and normal exposure are separate eligibility requirements. Missing or inadequate baselines are not ranked.

## Shrinkage and normalization
- Pressure rates are shrunk toward each player's normal rate using 60 prior balls/legal balls.
- Direction-aware deltas are robust-z normalized using median/MAD, with standard-deviation fallback and +/-3 clipping.
- Non-finite composite ratings are excluded from all ranked lists.

## Match consistency and reliability
- Match-level strike rate/economy summaries include ball-weighted mean and weighted dispersion, so matches contribute in proportion to pressure balls/legal balls.
- The reported interval remains a descriptive approximation, not a formal Bayesian posterior interval.
- Reliability tiers separate ineligible, limited-exposure and stronger-evidence candidates.

## Sensitivity
- Alternative weights and exposure thresholds are recalculated on the eligible IPL/T20I candidate pool.

## Status
- All rankings remain provisional for review. No final Unstop Top 10 is generated.