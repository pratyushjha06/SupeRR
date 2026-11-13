# PRESSURE-X Phase 4.4 — Competition Criteria & Candidate Readiness Audit

**Status: pre-submission audit only. No final Unstop rankings have been authorized or created.**

## 1. What the official Round 1 brief actually requires

The supplied *SupeRR Selector Season 2 — Round 1 Problem Statement* requires:
1. Two ordered Top-10 lists: batters and bowlers.
2. A methodology report explaining pressure definition, rating construction, analysis and final rankings.
3. Coverage of pressure indicators and rationale; batting/bowling metrics and baselines; sample-size and match-context fairness; use of IPL and T20I; evidence for each Top 10 and its ordering; consistency and limitations.
4. Reproducible, transparent analysis grounded in supplied data—not player reputation.
5. No duplicate player within a role's Top 10 and Unstop dropdown selections must match the report.

**Important:** The brief does not provide a numeric scoring rubric or evaluator weightings. This audit therefore checks the explicit deliverables and methodological expectations; it does not invent a competition score.

## 2. Compliance assessment

| Requirement                                       | Brief status            | Current project evidence                                                          | Remaining action                                                                         |
|:--------------------------------------------------|:------------------------|:----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------|
| Two ordered top-10 lists                          | Required                | Provisional rankings exist; final lists not selected                              | Not complete until final Unstop lists are locked                                         |
| Pressure definition and rationale                 | Required                | First-innings and chase heuristic defined with explicit weighted indicators       | Explain why these thresholds/weights are meaningful; add pressure-context examples       |
| Batting and bowling metrics and baselines         | Required                | Pressure-vs-normal metrics and direction-aware composite ratings implemented      | Document every metric definition and run/extras/dismissal treatment                      |
| Fair comparisons across sample sizes and contexts | Required                | Minimum exposure, match counts, reliability tiers, two-sample exposure adjustment | No explicit IPL-vs-T20I/season normalization demonstrated; assess format/context effects |
| Use of IPL and T20I data                          | Required                | Strict IPL/T20I filter applied; 194,014 deliveries retained                       | Document how pooled comparison handles differences in format/season                      |
| Evidence for final top 10 and ordering            | Required                | Top-20 evidence and sensitivity tables available                                  | Need final per-player evidence table for chosen 10 and rank rationale                    |
| Consistency and limitations                       | Required                | Weighted match-level mean/dispersion and limitations documented                   | Consistency metric is descriptive and does not yet enter score; state this clearly       |
| Reproducibility                                   | Implied by transparency | Source code, data, tests and outputs included                                     | Run from clean environment and include versioned run instructions                        |
| Optional journey photos/video                     | Optional                | Not prepared                                                                      | No impact on scoring per brief                                                           |

## 3. Data scope and eligibility

- Classified deliveries before scope filter: 200,999
- IPL/T20I deliveries retained: 194,014
- Other competition deliveries excluded: 6,985
- Eligible batters after pressure and normal-baseline minimums: 151
- Eligible bowlers: 210
- Stronger-tier batters: 54
- Stronger-tier bowlers: 98

The project applies IPL and T20I scope as required. It currently pools those formats in a common candidate population for robust standardization. The brief asks for fair comparisons and use of both formats, but does not prescribe a normalization method. **The lack of explicit format/season stratified ranking checks remains a material methodological limitation.**

## 4. Pressure definition — what is defensible and what needs explanation

The current model uses two distinct heuristics:
- First innings: wicket-loss pressure (35%), innings progress (35%), and scoring-rate deficit against the competition-season median first-innings run rate (30%).
- Chases: required-run-rate intensity (35%), wickets lost (25%), time scarcity (20%), and required-vs-current run-rate gap (20%).

It classifies pressure into low, moderate, high and very-high score bands. This satisfies the brief's request that the team define pressure, but the methodology report must explicitly justify the chosen weights and thresholds.

Limitations to disclose:
- First-innings pressure is a heuristic; it does not directly include match closeness or target context.
- Chase pressure uses required rate, wickets and time, but the current model does not explicitly model match win probability or the actual closeness of the contest.
- Competition-season median first-innings run rate is a baseline, not a full venue, opponent or innings-phase model.
- The pressure labels describe match context, not whether an individual player performed well.

## 5. Candidate readiness — balanced versus stronger-tier views

The current balanced Top 10 lists include limited-reliability players. For a challenge explicitly titled “Most Reliable Players Under Pressure,” the stronger-tier lists are a more defensible **review starting point**, because each selected player meets the project's stricter exposure thresholds. They are not automatically the final answer: the stricter tier is a project-defined rule, not a rule supplied by the competition.

### Batters — current balanced Top 10
|   rank | striker_name     |   rating_balanced | reliability_tier   | uncertainty_flag      |
|-------:|:-----------------|------------------:|:-------------------|:----------------------|
|      1 | Matthew Wade     |           2.78915 | stronger           | standard              |
|      2 | Kieron Pollard   |           2.58563 | limited            | standard              |
|      3 | Anuj Rawat       |           2.49634 | limited            | standard              |
|      4 | Towhid Hridoy    |           2.41412 | limited            | few_pressure_matches  |
|      5 | Nurul Hasan      |           2.4115  | limited            | standard              |
|      6 | Gareth Delany    |           2.28284 | stronger           | standard              |
|      7 | Mosaddek Hossain |           2.23549 | limited            | low_normal_baseline   |
|      8 | Jason Holder     |           2.17046 | stronger           | standard              |
|      9 | Fakhar Zaman     |           2.07624 | limited            | low_pressure_exposure |
|     10 | Aiden Markram    |           2.0502  | stronger           | standard              |

### Batters — stronger-tier Top 10 diagnostic
|   rank | striker_name    |   rating_balanced | reliability_tier   | uncertainty_flag   |
|-------:|:----------------|------------------:|:-------------------|:-------------------|
|      1 | Matthew Wade    |           2.78915 | stronger           | standard           |
|      2 | Gareth Delany   |           2.28284 | stronger           | standard           |
|      3 | Jason Holder    |           2.17046 | stronger           | standard           |
|      4 | Aiden Markram   |           2.0502  | stronger           | standard           |
|      5 | Dasun Shanaka   |           2.03585 | stronger           | standard           |
|      6 | Sikandar Raza   |           2.00819 | stronger           | standard           |
|      7 | Jaker Ali Anik  |           1.92206 | stronger           | standard           |
|      8 | Tristan Stubbs  |           1.86395 | stronger           | standard           |
|      9 | M Shahrukh Khan |           1.86314 | stronger           | standard           |
|     10 | Ryan Burl       |           1.85304 | stronger           | standard           |

### Bowlers — current balanced Top 10
|   rank | bowler_name       |   rating_balanced | reliability_tier   | uncertainty_flag      |
|-------:|:------------------|------------------:|:-------------------|:----------------------|
|      1 | Umran Malik       |           2.51335 | limited            | standard              |
|      2 | Andre Russell     |           2.4687  | stronger           | standard              |
|      3 | Shadab Khan       |           2.37513 | stronger           | standard              |
|      4 | Sunil Narine      |           2.21604 | stronger           | standard              |
|      5 | Abrar Ahmed       |           2.20482 | stronger           | standard              |
|      6 | Mohammad Nawaz    |           2.17817 | stronger           | standard              |
|      7 | Jamie Overton     |           2.04676 | stronger           | standard              |
|      8 | Mohit Sharma      |           1.9944  | stronger           | standard              |
|      9 | Matthew Humphreys |           1.9755  | limited            | low_pressure_exposure |
|     10 | Anshul Kamboj     |           1.95825 | limited            | standard              |

### Bowlers — stronger-tier Top 10 diagnostic
|   rank | bowler_name    |   rating_balanced | reliability_tier   | uncertainty_flag   |
|-------:|:---------------|------------------:|:-------------------|:-------------------|
|      1 | Andre Russell  |           2.4687  | stronger           | standard           |
|      2 | Shadab Khan    |           2.37513 | stronger           | standard           |
|      3 | Sunil Narine   |           2.21604 | stronger           | standard           |
|      4 | Abrar Ahmed    |           2.20482 | stronger           | standard           |
|      5 | Mohammad Nawaz |           2.17817 | stronger           | standard           |
|      6 | Jamie Overton  |           2.04676 | stronger           | standard           |
|      7 | Mohit Sharma   |           1.9944  | stronger           | standard           |
|      8 | Jofra Archer   |           1.73842 | stronger           | standard           |
|      9 | Shardul Thakur |           1.72339 | stronger           | standard           |
|     10 | Nitish Reddy   |           1.62711 | stronger           | standard           |

## 6. Candidate-specific weaknesses to resolve

### Batters
- Kieron Pollard: balanced rank 2, but normal exposure is only 84 balls; does not meet the stronger normal-exposure threshold.
- Anuj Rawat: balanced rank 3, pressure exposure is 97 balls and 9 pressure matches; limited tier.
- Towhid Hridoy: balanced rank 4, pressure matches only 6 despite large normal exposure; limited tier and few pressure matches.
- Nurul Hasan: balanced rank 5; pressure exposure 96 balls, below stronger threshold.
- Mosaddek Hossain: balanced rank 7; normal baseline only 36 balls across 5 matches, close to the minimum eligibility boundary.
- Fakhar Zaman: balanced rank 9; only 48 pressure balls and 7 pressure matches.
- Matthew Wade leads the balanced list and meets stronger thresholds, but still has 14 pressure matches and 162 pressure balls—adequate by the project's rule, not a massive sample.
- Jason Holder has 262 pressure balls over 41 matches, a relatively broad pressure sample; however, his dismissal-rate delta is slightly worse under pressure, so his overall rating is metric-tradeoff dependent.

### Bowlers
- Umran Malik leads the balanced list but is limited tier: 116 pressure legal balls, just below the 120-ball stronger threshold.
- Matthew Humphreys: only 46 pressure legal balls across 5 pressure matches; high rank is fragile.
- Anshul Kamboj: 85 pressure legal balls across 8 matches; limited pressure exposure.
- Abrar Ahmed, Shadab Khan, Sunil Narine, Andre Russell, Mohammad Nawaz, Jamie Overton and Mohit Sharma meet the stronger-tier rule and remain strong review candidates.
- Bowling leaders have different profiles: economy/control, wicket-taking and dot-ball suppression can move the order depending on the weighting scheme.

Full per-candidate metrics and scheme ranks are included in the accompanying CSVs and workbook.

## 7. Ranking sensitivity

The balanced top 10 is not invariant:
- Batters: 9/10 overlap under scoring-impact weights, 8/10 under survival weights, and 9/10 under equal weights.
- Bowlers: 9/10 overlap under wicket-impact weights, 8/10 under control weights, and 9/10 under equal weights.
- Raising the minimum pressure exposure to 60 balls/legal balls leaves 9/10 of the balanced Top 10 in common for each role; at 90, overlap falls to 8/10.

This is meaningful robustness evidence, but it also shows that the scoring design affects membership. The methodology report should show these alternatives rather than hiding them.

## 8. High-priority fixes before final submission

1. **Format/season fairness:** run separate IPL-only and T20I-only rankings, and season-level checks; identify candidates whose rank is driven mostly by one format or competition.
2. **Role/context fairness:** examine batter role and bowling role where the supplied data supports it. An opener, finisher and lower-order hitter may face systematically different pressure opportunities.
3. **Pressure definition validation:** show examples of high/very-high pressure deliveries and compare the distribution by format and innings phase. Explain why the score cutoffs are appropriate.
4. **Top-10 evidence:** produce a final one-page evidence table for each selected player: pressure and normal sample, pressure matches, key deltas, reliability tier, match dispersion and alternate-scheme rank.
5. **Methodology report:** state the scoring formula and all weights; define each metric and extras/dismissal handling; disclose limitations and the heuristic nature of reliability adjustment.
6. **Submission consistency:** copy the exact final ordered lists into Unstop and the methodology report; no duplicates within each role.


## 10. Format-split robustness check (exploratory)

The Phase 4.4 audit independently reran the Phase 3 metrics and Phase 4 rating calculation for IPL-only and T20I-only deliveries, using the same eligibility and scoring logic. The robust z-scores are recalculated within each format, so **these scores and ranks are not directly comparable across formats**. This is a diagnostic of whether the same names emerge within each environment, not a substitute for the pooled ranking.

### IPL-only batter Top 10
| format   |   rank | player           |   rating_balanced | reliability_tier   | uncertainty_flag      |
|:---------|-------:|:-----------------|------------------:|:-------------------|:----------------------|
| IPL      |      1 | Anuj Rawat       |           2.19226 | limited            | standard              |
| IPL      |      2 | Liam Livingstone |           2.18903 | limited            | standard              |
| IPL      |      3 | M Shahrukh Khan  |           1.91508 | stronger           | standard              |
| IPL      |      4 | Jos Buttler      |           1.87402 | limited            | low_pressure_exposure |
| IPL      |      5 | Ayush Badoni     |           1.79805 | stronger           | standard              |
| IPL      |      6 | Rashid Khan      |           1.73707 | limited            | low_normal_baseline   |
| IPL      |      7 | Kieron Pollard   |           1.6085  | limited            | low_normal_baseline   |
| IPL      |      8 | Sanju Samson     |           1.55457 | limited            | standard              |
| IPL      |      9 | Aiden Markram    |           1.54036 | limited            | standard              |
| IPL      |     10 | Sameer Rizvi     |           1.53176 | limited            | few_pressure_matches  |

### T20I-only batter Top 10
| format   |   rank | player           |   rating_balanced | reliability_tier   | uncertainty_flag      |
|:---------|-------:|:-----------------|------------------:|:-------------------|:----------------------|
| T20I     |      1 | Nurul Hasan      |           2.50635 | limited            | standard              |
| T20I     |      2 | Towhid Hridoy    |           2.49206 | limited            | few_pressure_matches  |
| T20I     |      3 | Mosaddek Hossain |           2.4597  | limited            | low_normal_baseline   |
| T20I     |      4 | Gareth Delany    |           2.3689  | stronger           | standard              |
| T20I     |      5 | Jason Holder     |           2.33963 | stronger           | standard              |
| T20I     |      6 | Suryakumar Yadav |           2.22686 | limited            | few_pressure_matches  |
| T20I     |      7 | Curtis Campher   |           2.07254 | limited            | standard              |
| T20I     |      8 | Fakhar Zaman     |           2.04465 | limited            | low_pressure_exposure |
| T20I     |      9 | Tristan Stubbs   |           2.03727 | limited            | few_pressure_matches  |
| T20I     |     10 | Matthew Wade     |           1.98272 | stronger           | standard              |

### IPL-only bowler Top 10
| format   |   rank | player         |   rating_balanced | reliability_tier   | uncertainty_flag      |
|:---------|-------:|:---------------|------------------:|:-------------------|:----------------------|
| IPL      |      1 | Umran Malik    |           2.79332 | limited            | few_pressure_matches  |
| IPL      |      2 | Sunil Narine   |           1.96163 | stronger           | standard              |
| IPL      |      3 | Mohit Sharma   |           1.81716 | stronger           | standard              |
| IPL      |      4 | Andre Russell  |           1.79961 | stronger           | standard              |
| IPL      |      5 | Sai Kishore    |           1.7263  | limited            | standard              |
| IPL      |      6 | Anshul Kamboj  |           1.70796 | limited            | standard              |
| IPL      |      7 | Brijesh Sharma |           1.54557 | limited            | low_pressure_exposure |
| IPL      |      8 | Ashwani Kumar  |           1.48612 | limited            | low_pressure_exposure |
| IPL      |      9 | Rasikh Salam   |           1.38162 | stronger           | standard              |
| IPL      |     10 | Harshit Rana   |           1.37168 | stronger           | standard              |

### T20I-only bowler Top 10
| format   |   rank | player            |   rating_balanced | reliability_tier   | uncertainty_flag      |
|:---------|-------:|:------------------|------------------:|:-------------------|:----------------------|
| T20I     |      1 | Shadab Khan       |           2.58996 | stronger           | standard              |
| T20I     |      2 | Mohammad Nawaz    |           2.38007 | stronger           | standard              |
| T20I     |      3 | Jamie Overton     |           2.32245 | limited            | standard              |
| T20I     |      4 | Abrar Ahmed       |           2.28386 | stronger           | standard              |
| T20I     |      5 | Matthew Humphreys |           2.16653 | limited            | low_pressure_exposure |
| T20I     |      6 | Nitish Reddy      |           2.09315 | limited            | standard              |
| T20I     |      7 | Akeal Hosein      |           2.04757 | limited            | standard              |
| T20I     |      8 | Gudakesh Motie    |           1.84341 | limited            | standard              |
| T20I     |      9 | Sean Abbott       |           1.82895 | limited            | standard              |
| T20I     |     10 | Marco Jansen      |           1.82418 | limited            | low_pressure_exposure |

**Finding:** There is no overlap between the IPL-only and T20I-only Top 10 lists for either batters or bowlers in this exploratory split. This is a material warning that pooled rankings may conceal format-specific candidate differences. It does not mean either format-specific list is the correct final list: each format subset has fewer deliveries and its own relative standardization. The final methodology should explain how pooled IPL/T20I comparison is justified and show the split as a limitation/robustness diagnostic.

## 11. Recommendation

Do not submit the current balanced lists without resolving the limited-tier cases. Use the stronger-tier shortlists as the primary review pool, then check format/season stability before deciding the final order. If the team retains a limited-tier player, explain the trade-off with raw sample evidence.

**Phase 4.4 outcome:** The project has the required analytical foundations and most of the methodology evidence. The format-split diagnostic now demonstrates substantial differences between IPL-only and T20I-only candidate lists. The remaining major gap is demonstrating that the pooled final ranking is fair across IPL/T20I contexts and that each selected player's ordering is supported by clear, reproducible evidence.

---
