# 实验对比

| run | d:d | d:d_no_soft | d:d_no_stages |
|---|---:|---:|---:|
| 全体 hit_at_1 | 0.778 | 0.756 | 0.744 |
| 全体 primary_at_5 | 0.978 | 0.978 | 0.956 |
| 全体 recall_at_5 | 0.581 | 0.567 | 0.528 |
| 全体 ndcg_at_10 | 0.660 | 0.645 | 0.619 |
| 全体 task_success_at_5 | 0.922 | 0.922 | 0.856 |
| 全体 window_primary_at_5 | 0.963 | 0.926 | 0.963 |
| 全体 stage_coverage_at_5 | 0.907 | 0.907 | 0.657 |
| 全体 all_stages_at_5 | 0.722 | 0.722 | 0.389 |
| 全体 candidate_task_success | 1.000 | 1.000 | 0.978 |
| current hit_at_1 | 0.778 | 0.667 | 0.778 |
| current primary_at_5 | 0.944 | 0.944 | 0.944 |
| current recall_at_5 | 0.625 | 0.551 | 0.625 |
| current ndcg_at_10 | 0.697 | 0.624 | 0.697 |
| current task_success_at_5 | 0.944 | 0.944 | 0.944 |
| current window_primary_at_5 | 0.889 | 0.778 | 0.889 |
| current stage_coverage_at_5 | — | — | — |
| current all_stages_at_5 | — | — | — |
| current candidate_task_success | 1.000 | 1.000 | 1.000 |
| evolution hit_at_1 | 0.833 | 0.833 | 0.667 |
| evolution primary_at_5 | 1.000 | 1.000 | 0.889 |
| evolution recall_at_5 | 0.907 | 0.907 | 0.639 |
| evolution ndcg_at_10 | 0.888 | 0.888 | 0.683 |
| evolution task_success_at_5 | 0.722 | 0.722 | 0.389 |
| evolution window_primary_at_5 | — | — | — |
| evolution stage_coverage_at_5 | 0.907 | 0.907 | 0.657 |
| evolution all_stages_at_5 | 0.722 | 0.722 | 0.389 |
| evolution candidate_task_success | 1.000 | 1.000 | 0.889 |
| foundation hit_at_1 | 0.833 | 0.833 | 0.833 |
| foundation primary_at_5 | 0.944 | 0.944 | 0.944 |
| foundation recall_at_5 | 0.542 | 0.542 | 0.542 |
| foundation ndcg_at_10 | 0.752 | 0.752 | 0.752 |
| foundation task_success_at_5 | 0.944 | 0.944 | 0.944 |
| foundation window_primary_at_5 | — | — | — |
| foundation stage_coverage_at_5 | — | — | — |
| foundation all_stages_at_5 | — | — | — |
| foundation candidate_task_success | 1.000 | 1.000 | 1.000 |
| historical hit_at_1 | 0.667 | 0.667 | 0.667 |
| historical primary_at_5 | 1.000 | 1.000 | 1.000 |
| historical recall_at_5 | 0.458 | 0.458 | 0.458 |
| historical ndcg_at_10 | 0.509 | 0.509 | 0.509 |
| historical task_success_at_5 | 1.000 | 1.000 | 1.000 |
| historical window_primary_at_5 | 1.000 | 1.000 | 1.000 |
| historical stage_coverage_at_5 | — | — | — |
| historical all_stages_at_5 | — | — | — |
| historical candidate_task_success | 1.000 | 1.000 | 1.000 |
| latest hit_at_1 | 0.778 | 0.778 | 0.778 |
| latest primary_at_5 | 1.000 | 1.000 | 1.000 |
| latest recall_at_5 | 0.375 | 0.375 | 0.375 |
| latest ndcg_at_10 | 0.453 | 0.453 | 0.453 |
| latest task_success_at_5 | 1.000 | 1.000 | 1.000 |
| latest window_primary_at_5 | 1.000 | 1.000 | 1.000 |
| latest stage_coverage_at_5 | — | — | — |
| latest all_stages_at_5 | — | — | — |
| latest candidate_task_success | 1.000 | 1.000 | 1.000 |

## 逐题 Task@5 对比（相对第一个 run）

| qid | d:d_no_soft | d:d_no_stages |
|---|---|---|
| latest-browser | = (1→1) | = (1→1) |
| current-browser | = (1→1) | = (1→1) |
| foundation-browser | = (1→1) | = (1→1) |
| historical-browser | = (1→1) | = (1→1) |
| evolution-browser | = (1→1) | = (1→1) |
| latest-router | = (1→1) | = (1→1) |
| current-router | = (1→1) | = (1→1) |
| foundation-router | = (1→1) | = (1→1) |
| historical-router | = (1→1) | = (1→1) |
| evolution-router | = (1→1) | = (1→1) |
| latest-memory | = (1→1) | = (1→1) |
| current-memory | = (1→1) | = (1→1) |
| foundation-memory | = (1→1) | = (1→1) |
| historical-memory | = (1→1) | = (1→1) |
| evolution-memory | = (0→0) | loss (0→0) |
| latest-mcp | = (1→1) | = (1→1) |
| current-mcp | = (1→1) | = (1→1) |
| foundation-mcp | = (1→1) | = (1→1) |
| historical-mcp | = (1→1) | = (1→1) |
| evolution-mcp | = (1→1) | loss (1→0) |
| latest-cost | = (1→1) | = (1→1) |
| current-cost | = (1→1) | = (1→1) |
| foundation-cost | = (1→1) | = (1→1) |
| historical-cost | = (1→1) | = (1→1) |
| evolution-cost | = (0→0) | = (0→0) |
| latest-selfhost | = (1→1) | = (1→1) |
| current-selfhost | = (1→1) | = (1→1) |
| foundation-selfhost | = (1→1) | = (1→1) |
| historical-selfhost | = (1→1) | = (1→1) |
| evolution-selfhost | = (1→1) | loss (1→0) |

- d:d_no_soft: win 0 / tie 30 / loss 0
- d:d_no_stages: win 0 / tie 27 / loss 3

## 诊断

- d:d hybrid: calls=39 requested=3000 median_ms=2556.5 p95_ms=2770.9 fallback=0
- d:d fts: calls=39 requested=3000 median_ms=1777.6 p95_ms=1997.5 fallback=0
- d:d vector: calls=39 requested=3000 median_ms=2534.0 p95_ms=2794.4 fallback=0
- d:d_no_soft hybrid: calls=39 requested=3000 median_ms=2545.2 p95_ms=2776.6 fallback=0
- d:d_no_soft fts: calls=39 requested=3000 median_ms=1760.4 p95_ms=1979.3 fallback=0
- d:d_no_soft vector: calls=39 requested=3000 median_ms=2551.8 p95_ms=2769.8 fallback=0
- d:d_no_stages hybrid: calls=30 requested=3000 median_ms=1384.5 p95_ms=2785.1 fallback=0
- d:d_no_stages fts: calls=30 requested=3000 median_ms=546.9 p95_ms=1976.1 fallback=0
- d:d_no_stages vector: calls=30 requested=3000 median_ms=1350.7 p95_ms=2762.6 fallback=0
