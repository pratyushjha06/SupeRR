# PRESSURE-X Phase 1 — Findings from supplied data

## Dataset inventory

| File | Rows | Columns | Exact duplicate rows |
|---|---:|---:|---:|
| competitions.csv | 141 | 4 | 0 |
| teams.csv | 353 | 3 | 0 |
| matches.csv | 883 | 22 | 0 |
| ball_by_ball.csv | 200,999 | 33 | 0 |
| competition_team_player_mapping.csv | 6,413 | 6 | 0 |
| playing_eleven.csv | 28,381 | 9 | 0 |

## Coverage and integrity

- **matches in matches file:** 883
- **matches with ball by ball:** 867
- **matches without ball by ball:** 16
- **ball by ball match ids not in matches:** 0
- **match competition ids missing from competitions:** 0
- **playing eleven match ids not in matches:** 0
- **mapping competition ids not in competitions:** 0

- Match date range: **2022-01-22 to 2026-11-01**.

## Competition scope

- Competition rows by format: **{'T20I': 134, 'T20': 7}**.
- Match records by format after joining competitions: **{'T20I': 482, 'T20': 401}**.
- The seven T20 competition records should be inspected individually. The source pack includes IPL and non-IPL T20 competitions; do not assume all T20 competitions are IPL.

## Player coverage

- **strikers:** 888
- **bowlers:** 647
- **playing eleven:** 1,082
- **competition mapping:** 1,217

## Key cautions before Phase 2

- 16 match records have no corresponding ball-by-ball rows. No unmatched delivery match IDs were found.
- Innings values 3 and 4 occur in delivery data and need Super Over / extra-innings handling.
- Missing dismissal fields are expected on non-wicket deliveries; missing match-result and revised-target fields can be structurally valid.
- The `runs`, `extras1_runs`, and `extras_2_runs` semantics must be validated before deriving batter runs, team totals, bowler-conceded runs, legal balls, or economy.
- `delivery_rows` in EDA outputs are record counts, not legal balls or balls faced.

## Phase 1 decision

The six CSVs load successfully. Exact duplicate rows are zero in all six tables, and the principal match/competition/player joins have no orphan IDs in the tested directions. Phase 2 can proceed after targeted validation of scoring/extras semantics and competition eligibility.
