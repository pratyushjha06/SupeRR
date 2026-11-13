# PRESSURE-X Phase 4.1 — Implementation and Run Summary

## Implemented changes
1. Strict competition filtering to IPL seasons and T20I competitions only.
2. Phase 3 metrics are regenerated using the scoped delivery file each time `run_phase4.py` runs.
3. Separate minimum pressure and normal exposure rules.
   - Batters: >=30 pressure balls, >=5 pressure matches, >=30 normal balls, >=3 normal matches.
   - Bowlers: >=30 pressure legal balls, >=5 pressure matches, >=30 normal legal balls, >=3 normal matches.
4. Non-finite composite ratings are excluded from rankings and sensitivity comparisons.
5. Match-level consistency now reports ball-weighted mean and weighted dispersion, with total pressure-ball exposure.
6. Reliability tiers distinguish ineligible records, limited evidence and stronger evidence.
7. Alternative weighting and exposure-threshold sensitivity are recalculated on the scoped candidate pool.
8. No final Unstop Top 10 is generated.

## Latest execution
- Classified deliveries before scope filter: 200,999
- IPL/T20I classified deliveries retained: 194,014
- Out-of-scope T20 deliveries excluded: 6,985
- Pressure-exposure-eligible batters before normal-baseline filter: 245
- Final eligible batters after normal-baseline filter: 151
- Pressure-exposure-eligible bowlers: 210
- Final eligible bowlers after normal-baseline filter: 210
- Batter candidates excluded for insufficient normal baseline: 94
- Bowler candidates excluded for insufficient normal baseline: 0

## Validation
- Full test suite: 20 passed.
- Phase 4.1 runner: completed successfully.
- Ranking status: provisional review only.
- Final Unstop Top 10: not created.

## Run on Windows
```powershell
.venv\Scripts\activate
python run_phase4.py
python -m pytest -v
```

The Phase 4.1 runner requires Phase 1 and Phase 2 outputs. The ZIP includes the original data pack, Phase 1–3 source, Phase 4.1 source, tests and current outputs.
