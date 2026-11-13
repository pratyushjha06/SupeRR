# PRESSURE-X Phase 4.8 — Match-Level Candidate Evidence Validation

## Purpose
This phase independently reconstructs candidate performance at the player-match level for the pooled Top 15 batters and Top 15 bowlers. It checks whether the pooled Top-10 candidate cases remain directionally supported when the evidence is viewed as match-level distributions rather than only pooled aggregate rates.

It is a validation layer, not a new ranking formula. It does not modify pooled ratings, change eligibility thresholds, or produce the final Unstop Top 10.

## Data scope and filtering
- Retained only matches whose competition is an `IPL YYYY` competition or whose `match_format` is `T20I`.
- Retained regulation innings and rows marked pressure-eligible by the existing Phase 2 classifier.
- Pressure group: `high` + `very_high`.
- Normal group: `low` + `moderate`.
- Unclassified rows were excluded from this comparison.
- In-scope eligible regulation deliveries used in this audit: 193,933.
- Candidate match-level records: 747 batter candidate match/group records and 849 bowler candidate match/group records.

## Metric reconstruction
### Batters
- Balls faced: all deliveries other than wides.
- Runs: batter runs.
- Dot balls: zero batter runs on a non-wide delivery.
- Boundary events: four/six flags.
- Dismissals: attributed to `dismissed_player_id`, including a non-striker dismissed by run-out.
- Match rates: strike rate, dot-ball percentage, boundary percentage and dismissals per 100 balls.

### Bowlers
- Legal balls: exclude wides and oversteps.
- Runs charged: batter runs plus wide/overstep extras; byes, leg-byes and penalty are not charged to the bowler.
- Dot balls: zero bowler-charged runs on a legal delivery.
- Wickets: caught, bowled, lbw, stump and hit wicket.
- Match rates: economy, dot-ball percentage, wickets per over and boundary events per legal ball.

The player-match medians are calculated by first computing each player's rate separately in each match and then taking the median across matches in pressure and normal groups. Each match therefore contributes one observation regardless of ball volume. These are descriptive diagnostics, not the project's pooled/shrunk rating metrics.

## Batter candidate validation
Deltas are pressure match-median minus normal match-median. Positive strike-rate and boundary deltas are favourable; negative dot-ball and dismissal-rate deltas are favourable.

| Rank | Batter | Pressure matches | Normal matches | Pressure balls | Normal balls | Favourable components | SR Δ | Dot% Δ | Boundary% Δ | Dismissal Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Matthew Wade | 14 | 24 | 162 | 265 | 4/4 | 82.7 | -21.1 | 14.5 | -4.4 |
| 2 | Kieron Pollard | 12 | 10 | 127 | 84 | 4/4 | 60.3 | -32.6 | 18.4 | -7.1 |
| 3 | Anuj Rawat | 9 | 17 | 97 | 169 | 4/4 | 18.2 | -16.9 | 5.0 | -5.0 |
| 4 | Towhid Hridoy | 6 | 49 | 128 | 804 | 4/4 | 28.8 | -5.2 | 3.6 | -0.6 |
| 5 | Nurul Hasan | 12 | 17 | 96 | 141 | 3/4 | 107.8 | -17.6 | 21.1 | 0.0 |
| 6 | Gareth Delany | 16 | 23 | 168 | 128 | 3/4 | 40.6 | -6.3 | 11.8 | 6.9 |
| 7 | Mosaddek Hossain | 6 | 5 | 77 | 36 | 4/4 | 108.1 | -47.0 | 13.1 | -25.0 |
| 8 | Jason Holder | 41 | 29 | 262 | 185 | 3/4 | 23.1 | -16.7 | 13.3 | 2.9 |
| 9 | Fakhar Zaman | 7 | 46 | 48 | 815 | 4/4 | 116.2 | -14.3 | 27.5 | -5.6 |
| 10 | Aiden Markram | 15 | 91 | 185 | 1486 | 3/4 | 53.4 | -13.3 | 9.6 | 0.0 |
| 11 | Dasun Shanaka | 32 | 48 | 310 | 464 | 3/4 | 61.1 | -16.6 | 20.0 | 3.3 |
| 12 | Curtis Campher | 8 | 34 | 68 | 458 | 4/4 | 50.0 | -19.7 | 15.2 | -2.5 |
| 13 | Sikandar Raza | 15 | 56 | 186 | 816 | 3/4 | 50.0 | -11.7 | 7.5 | 1.6 |
| 14 | Jaker Ali Anik | 17 | 30 | 200 | 312 | 3/4 | 50.0 | -7.5 | 8.0 | 5.9 |
| 15 | Babar Azam | 6 | 52 | 48 | 1133 | 4/4 | 62.3 | -30.0 | 11.0 | -1.2 |

## Bowler candidate validation
Deltas are pressure match-median minus normal match-median. Negative economy and boundary deltas are favourable; positive dot-ball and wickets-per-over deltas are favourable.

| Rank | Bowler | Pressure matches | Normal matches | Pressure legal balls | Normal legal balls | Favourable components | Econ Δ | Dot% Δ | Wkts/over Δ | Boundary% Δ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Umran Malik | 13 | 30 | 116 | 446 | 4/4 | -2.6 | 8.2 | 0.9 | -11.1 |
| 2 | Andre Russell | 28 | 49 | 203 | 550 | 4/4 | -1.4 | 13.9 | 0.4 | -14.3 |
| 3 | Shadab Khan | 17 | 40 | 148 | 684 | 4/4 | -1.2 | 2.1 | 0.3 | -8.3 |
| 4 | Sunil Narine | 29 | 66 | 232 | 1298 | 4/4 | -2.3 | 16.7 | 0.2 | -10.6 |
| 5 | Abrar Ahmed | 23 | 35 | 204 | 560 | 3/4 | -3.0 | 0.0 | 0.0 | -12.5 |
| 6 | Mohammad Nawaz | 16 | 49 | 130 | 874 | 3/4 | -2.8 | 14.7 | -0.1 | -12.5 |
| 7 | Jamie Overton | 14 | 26 | 154 | 344 | 4/4 | -2.1 | 2.5 | 0.7 | -7.5 |
| 8 | Mohit Sharma | 24 | 28 | 255 | 396 | 3/4 | -0.1 | 10.0 | 0.1 | 0.0 |
| 9 | Matthew Humphreys | 5 | 14 | 46 | 259 | 4/4 | -3.5 | 25.0 | 0.8 | -14.6 |
| 10 | Anshul Kamboj | 8 | 25 | 85 | 406 | 3/4 | -1.8 | -1.4 | 0.4 | -5.6 |
| 11 | Sai Kishore | 10 | 23 | 98 | 367 | 4/4 | -1.7 | 10.4 | 0.6 | -8.9 |
| 12 | Akeal Hosein | 14 | 79 | 108 | 1585 | 2/4 | -2.8 | -8.3 | 0.0 | -16.7 |
| 13 | Brijesh Sharma | 8 | 13 | 50 | 227 | 3/4 | -3.3 | 7.7 | 0.0 | -9.4 |
| 14 | Jofra Archer | 30 | 56 | 183 | 1078 | 2/4 | -2.0 | -10.6 | -0.3 | -11.7 |
| 15 | Shardul Thakur | 29 | 48 | 239 | 732 | 3/4 | -2.6 | 9.3 | 0.0 | -9.0 |

## Key validation observations

### Batters
- The match-level median comparison is directionally favourable on all four measured components for Matthew Wade, Kieron Pollard, Anuj Rawat, Towhid Hridoy, Mosaddek Hossain and Fakhar Zaman.
- Nurul Hasan, Gareth Delany, Jason Holder and Aiden Markram show three favourable components out of four. For Gareth Delany and Jason Holder, dismissal rate is worse in the pressure match-median comparison; this should be disclosed.
- These results do not mean every pressure innings was better. Match-level medians summarize distributions and do not replace the underlying match records.
- The pooled Top-10 candidates have at least six pressure matches in this reconstruction. This is observed coverage, not proof that six matches guarantees statistical reliability.

### Bowlers
- All ten pooled Top-10 bowlers show at least three favourable components out of four in the match-level median comparison.
- Abrar Ahmed and Mohammad Nawaz have three favourable components; wickets per over is not better in the pressure match-median comparison.
- Mohit Sharma's median economy delta is close to zero, so his case is supported more by the other components and pooled model evidence than by a clear median economy improvement.
- Matthew Humphreys has only five pressure matches in this reconstruction and 46 pressure legal balls in the Phase 4 pooled candidate table. His positive directional results are especially sample-sensitive.

## Nearest omitted candidates (pooled ranks 11–15)
The same validation tables include the nearest omitted candidates:
- Batters: Dasun Shanaka, Curtis Campher, Sikandar Raza, Jaker Ali Anik and Babar Azam.
- Bowlers: Sai Kishore, Akeal Hosein, Brijesh Sharma, Jofra Archer and Shardul Thakur.

They should be compared against conditional Top-10 candidates before the final cut. Dasun Shanaka is a stronger-tier batter reserve; Jofra Archer is a stronger-tier bowler reserve. A rank just outside the cut-off should not be treated as a large performance gap without inspecting rating differences and exposure.

## Interpretation and limitations
1. These are pressure-versus-normal comparisons, not causal estimates. Pressure states occur in different match situations from normal states.
2. Match-level medians reduce domination by high-volume matches but give low-ball and high-ball match observations equal weight. They complement rather than replace pooled rates.
3. A match-level pressure/normal count can include a match with only a small number of balls in that group. Read it alongside total balls and the existing reliability tier.
4. The pressure classifier is inherited from Phase 2; this phase does not re-estimate or validate its thresholds.
5. No opposition-strength, batting-position, bowling-phase, venue, toss or match-state adjustment is introduced here.
6. The audit reconstructs selected metrics from the supplied delivery data. It does not prove the data pack is a complete census of every real-world IPL/T20I match in the period.

## Decision
Phase 4.8 supports keeping the current pooled Top 10s as the **primary provisional candidate pools**, with explicit caveats for limited reliability and specific metric weaknesses. It does not justify locking the final lists without a documented comparison against nearest omitted candidates.

**No final Unstop Top 10 has been created in Phase 4.8.**
