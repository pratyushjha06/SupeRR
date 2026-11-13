# PRESSURE-X Phase 4.5 — Format and Season Fairness Analysis

**Status: robustness analysis only. No final Unstop Top 10 has been created.**

## 1. Purpose

Phase 4.5 investigates whether pooled IPL/T20I rankings conceal different format- or year-specific performance patterns. It reruns Phase 3 aggregation and the Phase 4 rating engine separately for each IPL season and each T20I calendar year, applying the same eligibility and scoring rules.

Calendar year is used for T20I because the source metadata includes cross-year season labels (for example, 2022/23 and 2024/25). Grouping by calendar year avoids treating three-match fragments as standalone seasons. IPL is grouped by its competition year.

## 2. Scope and year coverage

| format   |   calendar_year |   matches |   deliveries |   eligible_batters |   eligible_bowlers | batter_top10_complete   | bowler_top10_complete   |
|:---------|----------------:|----------:|-------------:|-------------------:|-------------------:|:------------------------|:------------------------|
| IPL      |            2022 |        74 |        17909 |                 19 |                 35 | True                    | True                    |
| IPL      |            2023 |        74 |        17863 |                 20 |                 35 | True                    | True                    |
| IPL      |            2024 |        74 |        17103 |                 18 |                 34 | True                    | True                    |
| IPL      |            2025 |        75 |        17285 |                 20 |                 33 | True                    | True                    |
| IPL      |            2026 |        74 |        17527 |                 11 |                 32 | True                    | True                    |
| T20I     |            2022 |       106 |        24556 |                 18 |                 38 | True                    | True                    |
| T20I     |            2023 |        66 |        15125 |                  5 |                 15 | False                   | True                    |
| T20I     |            2024 |       111 |        24173 |                 13 |                 43 | True                    | True                    |
| T20I     |            2025 |       127 |        26914 |                 16 |                 44 | True                    | True                    |
| T20I     |            2026 |        72 |        15559 |                  8 |                 18 | False                   | True                    |

T20I 2023 and 2026 do not have enough eligible batters to produce a full Top 10 under the existing minimum-exposure rules (5 and 8 eligible batters respectively). This is a coverage limitation, not a reason to relax eligibility silently.

## 3. What the format/year splits reveal

### 3.1 Format-level divergence

The separate format-only Top 10 lists from Phase 4.4 had zero overlap for batters and zero overlap for bowlers. Phase 4.5 now checks whether candidates recur across multiple year-level rankings within each format.

The format-specific ratings are re-standardized within each subset. Therefore, **a score of 2.0 in IPL is not numerically comparable to a score of 2.0 in T20I**. These tables test candidate recurrence and rank stability only.

### 3.2 Pooled batter Top 10: year-level recurrence

|   pooled_rank | player           | pooled_tier   |   format_year_buckets_eligible |   format_year_top10_count |   best_year_rank |   median_year_rank | appearances                      |
|--------------:|:-----------------|:--------------|-------------------------------:|--------------------------:|-----------------:|-------------------:|:---------------------------------|
|             1 | Matthew Wade     | stronger      |                              1 |                         1 |                4 |                  4 | T20I 2022: #4                    |
|             2 | Kieron Pollard   | limited       |                              2 |                         2 |                4 |                  6 | IPL 2022: #4; T20I 2022: #8      |
|             3 | Anuj Rawat       | limited       |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance |
|             4 | Towhid Hridoy    | limited       |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance |
|             5 | Nurul Hasan      | limited       |                              1 |                         1 |               10 |                 10 | T20I 2022: #10                   |
|             6 | Gareth Delany    | stronger      |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance |
|             7 | Mosaddek Hossain | limited       |                              1 |                         1 |                1 |                  1 | T20I 2022: #1                    |
|             8 | Jason Holder     | stronger      |                              2 |                         2 |                5 |                  6 | T20I 2022: #5; T20I 2025: #7     |
|             9 | Fakhar Zaman     | limited       |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance |
|            10 | Aiden Markram    | stronger      |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance |

### 3.3 Pooled bowler Top 10: year-level recurrence

|   pooled_rank | player            | pooled_tier   |   format_year_buckets_eligible |   format_year_top10_count |   best_year_rank |   median_year_rank | appearances                              |
|--------------:|:------------------|:--------------|-------------------------------:|--------------------------:|-----------------:|-------------------:|:-----------------------------------------|
|             1 | Umran Malik       | limited       |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance         |
|             2 | Andre Russell     | stronger      |                              2 |                         1 |                2 |                  2 | IPL 2022: #2                             |
|             3 | Shadab Khan       | stronger      |                              1 |                         1 |               10 |                 10 | T20I 2026: #10                           |
|             4 | Sunil Narine      | stronger      |                              3 |                         3 |                3 |                  4 | IPL 2024: #5; IPL 2025: #3; IPL 2026: #4 |
|             5 | Abrar Ahmed       | stronger      |                              2 |                         2 |                1 |                  4 | T20I 2025: #1; T20I 2026: #7             |
|             6 | Mohammad Nawaz    | stronger      |                              1 |                         1 |                2 |                  2 | T20I 2025: #2                            |
|             7 | Jamie Overton     | stronger      |                              1 |                         0 |              nan |                nan | No format-year Top 10 appearance         |
|             8 | Mohit Sharma      | stronger      |                              2 |                         2 |                1 |                  3 | IPL 2023: #5; IPL 2024: #1               |
|             9 | Matthew Humphreys | limited       |                              0 |                         0 |              nan |                nan | No format-year Top 10 appearance         |
|            10 | Anshul Kamboj     | limited       |                              1 |                         1 |                1 |                  1 | IPL 2026: #1                             |

## 4. Main findings

### Batters

- Matthew Wade appears in the T20I 2022 year-level Top 10 (rank 4), but not across multiple format-year groups.
- Kieron Pollard appears in both IPL 2022 (rank 4) and T20I 2022 (rank 8), but is limited-tier in the pooled ranking due to normal-baseline exposure.
- Jason Holder appears in T20I 2022 (rank 5) and T20I 2025 (rank 7), providing the clearest multi-year recurrence among the pooled top-10 batters.
- Mosaddek Hossain appears first in T20I 2022, but his pooled reliability remains limited and normal baseline exposure is relatively thin.
- Anuj Rawat, Towhid Hridoy, Gareth Delany, Fakhar Zaman and Aiden Markram do not appear in a year-specific Top 10 under the current year-level eligibility rules. Their pooled rank is therefore not independently corroborated by a year-level Top 10.
- A missing year-level Top 10 appearance does not mean poor performance; it may mean the player did not reach the minimum exposure in any single year, while qualifying after data is pooled across years.

### Bowlers

- Sunil Narine appears in IPL 2024, 2025 and 2026 Top 10s (ranks 5, 3 and 4): strongest recurrence among pooled top-10 bowlers.
- Abrar Ahmed appears in T20I 2025 (rank 1) and 2026 (rank 7).
- Mohit Sharma appears in IPL 2023 (rank 5) and 2024 (rank 1).
- Andre Russell appears in IPL 2022 (rank 2), but not repeatedly in the year-specific Top 10.
- Shadab Khan appears in T20I 2026 (rank 10); his pooled ranking has limited year-specific recurrence.
- Jamie Overton is stronger-tier in the pooled rating, but does not appear in a year-level Top 10. This is a warning that the pooled rating aggregates exposure that is not concentrated enough within one calendar year to reproduce a year-level Top 10.
- Umran Malik, despite leading the pooled bowler ranking, does not appear in a year-level Top 10 under the separate-year eligibility thresholds. This makes his pooled #1 position particularly important to scrutinize rather than accept at face value.
- Matthew Humphreys and Anshul Kamboj also have limited pooled reliability; Humphreys does not recur in year-level Top 10s, while Anshul appears at #1 in IPL 2026.

## 5. Interpretation: why pooled and year-level rankings differ

1. **Exposure pooling:** a player can accumulate enough pressure and normal deliveries over several years to qualify in the pooled data, even if no single year independently meets the same thresholds.
2. **Competition/format mix:** pooled ratings combine IPL and T20I opportunities, while split ratings compare players only within one format or year.
3. **Within-subset standardization:** robust z-scores are recalculated for each subset. This changes the comparison group and can change candidate ordering.
4. **Different role/opportunity mix:** the player roles and pressure situations available in a particular IPL season or T20I calendar year are not identical.
5. **Small candidate populations:** year-level eligible pools are smaller; T20I 2023 and 2026 do not support a full batter Top 10 under current thresholds.

## 6. Fairness recommendation

Do not simply average IPL and T20I scores or average yearly ranks. Those operations would be arbitrary because the score scales are independently standardized and exposure opportunities differ.

Recommended approach for the final methodology:
- Keep the pooled IPL/T20I score as the primary overall evidence base, since the challenge asks for a combined player assessment using IPL and T20I data.
- Add an explicit format exposure breakdown for every final candidate: pressure balls/overs, pressure matches, normal exposure, and share of pressure exposure from IPL versus T20I.
- Add year-level recurrence as a robustness indicator, not as a score component yet.
- Flag candidates whose pooled rank is not supported by any format-year Top 10.
- Consider a format-balanced rating only after defining and justifying how IPL and T20I evidence should be weighted; do not silently force equal format weights.
- Retain the same minimum sample thresholds unless there is a documented methodological reason to change them.

## 7. Candidate readiness decision

### Higher recurrence evidence among pooled Top 10

- **Batters:** Jason Holder and Kieron Pollard have multi-bucket recurrence; Matthew Wade has one year-level appearance with stronger pooled reliability.
- **Bowlers:** Sunil Narine, Abrar Ahmed and Mohit Sharma show the clearest recurrence across multiple year-level groups.

### Candidates needing specific review before final selection

- **Batters:** Anuj Rawat, Towhid Hridoy, Gareth Delany, Fakhar Zaman and Aiden Markram.
- **Bowlers:** Umran Malik, Jamie Overton, Matthew Humphreys and Shadab Khan.

These are audit priorities, not recommended final picks.

## 8. Final status

Phase 4.5 demonstrates that pooled rankings are not uniformly reproduced by year-level rankings. The most important remaining decision is to define a defensible way to combine IPL and T20I evidence while showing each player's format exposure transparently.

**No final Top 10 has been created.** The final selection should wait until the team reviews candidate-level format exposure and approves a documented format-balancing rule.

---
