# PRESSURE-X Phase 4.2 — Reliability and Consistency Review

## Scope and execution

- Competition scope: IPL and T20I only.
- Classified deliveries before scope filter: 200,999.
- Retained deliveries: 194,014; excluded out-of-scope deliveries: 6,985.
- Eligible candidates after pressure and normal baseline requirements: 151 batters and 210 bowlers.
- No final Unstop Top 10 is created. All lists are provisional.

## Method changes

- Pressure-vs-normal differences now use separate exposure reliability weights for both groups. Each weight is exposure / (exposure + 60); the product scales the observed difference.
- This is an explicit heuristic to reduce the influence of weak pressure or normal samples. It is not a formal Bayesian posterior or a claim of statistical significance.
- The consistency merge now preserves canonical weighted match fields and avoids duplicate/suffixed columns.
- Weighted match mean and dispersion are descriptive only. Confidence intervals are not reported because the weighted spread of match-level aggregates does not justify a simple standard-error calculation.
- Stronger reliability tier: at least 120 pressure balls/legal balls, 120 normal balls/legal balls, 10 pressure matches and 5 normal matches. Other eligible candidates are marked limited.

## Reliability distribution

- Batters: {'limited': 97, 'stronger': 54}
- Bowlers: {'limited': 112, 'stronger': 98}
- Batting consistency records with weighted mean: 671
- Bowling consistency records with weighted mean: 467

## Provisional top 20 batters

| Rank | Player | Pressure balls | Normal balls | Pressure matches | Tier | Rating |
|---:|---|---:|---:|---:|---|---:|
| 1 | Matthew Wade | 162 | 265 | 14 | stronger | 2.789 |
| 2 | Kieron Pollard | 127 | 84 | 12 | limited | 2.586 |
| 3 | Anuj Rawat | 97 | 169 | 9 | limited | 2.496 |
| 4 | Towhid Hridoy | 128 | 804 | 6 | limited | 2.414 |
| 5 | Nurul Hasan | 96 | 141 | 12 | limited | 2.412 |
| 6 | Gareth Delany | 168 | 128 | 16 | stronger | 2.283 |
| 7 | Mosaddek Hossain | 77 | 36 | 6 | limited | 2.235 |
| 8 | Jason Holder | 262 | 185 | 41 | stronger | 2.170 |
| 9 | Fakhar Zaman | 48 | 815 | 7 | limited | 2.076 |
| 10 | Aiden Markram | 185 | 1486 | 15 | stronger | 2.050 |
| 11 | Dasun Shanaka | 310 | 464 | 32 | stronger | 2.036 |
| 12 | Curtis Campher | 68 | 458 | 8 | limited | 2.029 |
| 13 | Sikandar Raza | 186 | 816 | 15 | stronger | 2.008 |
| 14 | Jaker Ali Anik | 200 | 312 | 17 | stronger | 1.922 |
| 15 | Babar Azam | 48 | 1133 | 6 | limited | 1.890 |
| 16 | Gulbadin Naib | 42 | 160 | 5 | limited | 1.887 |
| 17 | Tristan Stubbs | 385 | 696 | 30 | stronger | 1.864 |
| 18 | M Shahrukh Khan | 147 | 263 | 22 | stronger | 1.863 |
| 19 | Ryan Burl | 189 | 517 | 17 | stronger | 1.853 |
| 20 | Marco Jansen | 217 | 60 | 28 | limited | 1.808 |

## Provisional top 20 bowlers

| Rank | Player | Pressure legal balls | Normal legal balls | Pressure matches | Tier | Rating |
|---:|---|---:|---:|---:|---|---:|
| 1 | Umran Malik | 116 | 446 | 13 | limited | 2.513 |
| 2 | Andre Russell | 203 | 550 | 28 | stronger | 2.469 |
| 3 | Shadab Khan | 148 | 684 | 17 | stronger | 2.375 |
| 4 | Sunil Narine | 232 | 1298 | 29 | stronger | 2.216 |
| 5 | Abrar Ahmed | 204 | 560 | 23 | stronger | 2.205 |
| 6 | Mohammad Nawaz | 130 | 874 | 16 | stronger | 2.178 |
| 7 | Jamie Overton | 154 | 344 | 14 | stronger | 2.047 |
| 8 | Mohit Sharma | 255 | 396 | 24 | stronger | 1.994 |
| 9 | Matthew Humphreys | 46 | 259 | 5 | limited | 1.975 |
| 10 | Anshul Kamboj | 85 | 406 | 8 | limited | 1.958 |
| 11 | Sai Kishore | 98 | 367 | 10 | limited | 1.958 |
| 12 | Akeal Hosein | 108 | 1585 | 14 | limited | 1.913 |
| 13 | Brijesh Sharma | 50 | 227 | 8 | limited | 1.802 |
| 14 | Jofra Archer | 183 | 1078 | 30 | stronger | 1.738 |
| 15 | Shardul Thakur | 239 | 732 | 29 | stronger | 1.723 |
| 16 | Sean Abbott | 80 | 364 | 11 | limited | 1.698 |
| 17 | Shamar Joseph | 102 | 373 | 12 | limited | 1.684 |
| 18 | Ashwani Kumar | 45 | 139 | 5 | limited | 1.642 |
| 19 | Nitish Reddy | 172 | 395 | 22 | stronger | 1.627 |
| 20 | Gudakesh Motie | 86 | 652 | 11 | limited | 1.574 |

## Weight sensitivity

| Role | Alternative | Top-10 overlap | Spearman rank correlation |
|---|---|---:|---:|
| Batter | scoring_impact | 90% | 0.951 |
| Batter | survival | 80% | 0.943 |
| Batter | equal | 90% | 0.993 |
| Bowler | wicket_impact | 90% | 0.977 |
| Bowler | control | 80% | 0.984 |
| Bowler | equal | 90% | 0.985 |

## Exposure sensitivity

| Role | Minimum pressure exposure | Top-10 overlap vs balanced |
|---|---:|---:|
| Batter | 20 | 100% |
| Batter | 30 | 100% |
| Batter | 45 | 100% |
| Batter | 60 | 90% |
| Batter | 90 | 80% |
| Bowler | 20 | 100% |
| Bowler | 30 | 100% |
| Bowler | 45 | 100% |
| Bowler | 60 | 90% |
| Bowler | 90 | 80% |

## Interpretation and limitations

- The balanced score is a provisional ordering, not an objective truth. Alternative weight schemes change some Top-10 membership.
- Candidates in the limited tier should not be described as equally reliable as stronger-tier candidates, even if their raw composite score is higher.
- Match-level consistency summaries are descriptive; they do not prove repeatability or provide formal uncertainty intervals.
- The two-sample exposure adjustment is a transparent heuristic. A future version could replace it with a player-level hierarchical model or bootstrap analysis if the project scope and validation time permit.
- Do not submit a final Top 10 until the candidate evidence and competition eligibility have been reviewed against the event requirements.