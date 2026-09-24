# 实验对比

| run | a:a | b:b | c:c | d:d |
|---|---:|---:|---:|---:|
| 全体 hit_at_1 | 0.689 | 0.756 | 0.711 | 0.767 |
| 全体 primary_at_5 | 0.933 | 0.922 | 0.944 | 0.967 |
| 全体 recall_at_5 | 0.594 | 0.588 | 0.505 | 0.573 |
| 全体 ndcg_at_10 | 0.669 | 0.689 | 0.599 | 0.655 |
| 全体 task_success_at_5 | 0.767 | 0.689 | 0.844 | 0.911 |
| 全体 window_primary_at_5 | 0.870 | 0.667 | 0.926 | 0.963 |
| 全体 stage_coverage_at_5 | 0.574 | 0.657 | 0.657 | 0.907 |
| 全体 all_stages_at_5 | 0.333 | 0.389 | 0.389 | 0.722 |
| 全体 candidate_task_success | 0.956 | 0.978 | 0.978 | 1.000 |
| current hit_at_1 | 0.667 | 0.667 | 0.667 | 0.778 |
| current primary_at_5 | 1.000 | 0.944 | 0.944 | 0.944 |
| current recall_at_5 | 0.653 | 0.551 | 0.551 | 0.625 |
| current ndcg_at_10 | 0.676 | 0.624 | 0.624 | 0.697 |
| current task_success_at_5 | 1.000 | 0.944 | 0.944 | 0.944 |
| current window_primary_at_5 | 1.000 | 0.778 | 0.778 | 0.889 |
| current stage_coverage_at_5 | — | — | — | — |
| current all_stages_at_5 | — | — | — | — |
| current candidate_task_success | 1.000 | 1.000 | 1.000 | 1.000 |
| evolution hit_at_1 | 0.556 | 0.667 | 0.667 | 0.833 |
| evolution primary_at_5 | 0.833 | 0.889 | 0.889 | 1.000 |
| evolution recall_at_5 | 0.574 | 0.639 | 0.639 | 0.907 |
| evolution ndcg_at_10 | 0.624 | 0.683 | 0.683 | 0.888 |
| evolution task_success_at_5 | 0.333 | 0.389 | 0.389 | 0.722 |
| evolution window_primary_at_5 | — | — | — | — |
| evolution stage_coverage_at_5 | 0.574 | 0.657 | 0.657 | 0.907 |
| evolution all_stages_at_5 | 0.333 | 0.389 | 0.389 | 0.722 |
| evolution candidate_task_success | 0.778 | 0.889 | 0.889 | 1.000 |
| foundation hit_at_1 | 0.778 | 0.778 | 0.778 | 0.778 |
| foundation primary_at_5 | 0.889 | 0.889 | 0.889 | 0.889 |
| foundation recall_at_5 | 0.500 | 0.500 | 0.500 | 0.500 |
| foundation ndcg_at_10 | 0.725 | 0.725 | 0.725 | 0.725 |
| foundation task_success_at_5 | 0.889 | 0.889 | 0.889 | 0.889 |
| foundation window_primary_at_5 | — | — | — | — |
| foundation stage_coverage_at_5 | — | — | — | — |
| foundation all_stages_at_5 | — | — | — | — |
| foundation candidate_task_success | 1.000 | 1.000 | 1.000 | 1.000 |
| historical hit_at_1 | 0.833 | 0.833 | 0.667 | 0.667 |
| historical primary_at_5 | 1.000 | 0.944 | 1.000 | 1.000 |
| historical recall_at_5 | 0.676 | 0.606 | 0.458 | 0.458 |
| historical ndcg_at_10 | 0.704 | 0.702 | 0.509 | 0.509 |
| historical task_success_at_5 | 0.889 | 0.667 | 1.000 | 1.000 |
| historical window_primary_at_5 | 0.889 | 0.667 | 1.000 | 1.000 |
| historical stage_coverage_at_5 | — | — | — | — |
| historical all_stages_at_5 | — | — | — | — |
| historical candidate_task_success | 1.000 | 1.000 | 1.000 | 1.000 |
| latest hit_at_1 | 0.611 | 0.833 | 0.778 | 0.778 |
| latest primary_at_5 | 0.944 | 0.944 | 1.000 | 1.000 |
| latest recall_at_5 | 0.569 | 0.644 | 0.375 | 0.375 |
| latest ndcg_at_10 | 0.613 | 0.711 | 0.453 | 0.453 |
| latest task_success_at_5 | 0.722 | 0.556 | 1.000 | 1.000 |
| latest window_primary_at_5 | 0.722 | 0.556 | 1.000 | 1.000 |
| latest stage_coverage_at_5 | — | — | — | — |
| latest all_stages_at_5 | — | — | — | — |
| latest candidate_task_success | 1.000 | 1.000 | 1.000 | 1.000 |

## 逐题 Task@5 对比（相对第一个 run）

| qid | b:b | c:c | d:d |
|---|---|---|---|
| latest-browser | = (1→1) | = (1→1) | = (1→1) |
| current-browser | = (1→1) | = (1→1) | = (1→1) |
| foundation-browser | = (1→1) | = (1→1) | = (1→1) |
| historical-browser | loss (1→1) | = (1→1) | = (1→1) |
| evolution-browser | = (1→1) | = (1→1) | = (1→1) |
| latest-router | = (1→1) | = (1→1) | = (1→1) |
| current-router | = (1→1) | = (1→1) | = (1→1) |
| foundation-router | = (1→1) | = (1→1) | = (1→1) |
| historical-router | = (1→1) | win (1→1) | win (1→1) |
| evolution-router | = (1→1) | = (1→1) | = (1→1) |
| latest-memory | loss (1→1) | = (1→1) | = (1→1) |
| current-memory | = (1→1) | = (1→1) | = (1→1) |
| foundation-memory | = (1→1) | = (1→1) | = (1→1) |
| historical-memory | = (1→1) | = (1→1) | = (1→1) |
| evolution-memory | = (0→0) | = (0→0) | win (0→0) |
| latest-mcp | loss (1→1) | = (1→1) | = (1→1) |
| current-mcp | = (1→1) | = (1→1) | = (1→1) |
| foundation-mcp | = (1→1) | = (1→1) | = (1→1) |
| historical-mcp | loss (1→0) | win (1→1) | win (1→1) |
| evolution-mcp | = (0→0) | = (0→0) | win (0→1) |
| latest-cost | loss (0→0) | win (0→1) | win (0→1) |
| current-cost | = (1→1) | = (1→1) | = (1→1) |
| foundation-cost | = (1→1) | = (1→1) | = (1→1) |
| historical-cost | = (1→1) | = (1→1) | = (1→1) |
| evolution-cost | = (0→0) | = (0→0) | = (0→0) |
| latest-selfhost | = (0→0) | win (0→1) | win (0→1) |
| current-selfhost | loss (1→1) | loss (1→1) | loss (1→1) |
| foundation-selfhost | = (1→1) | = (1→1) | = (1→1) |
| historical-selfhost | loss (1→1) | = (1→1) | = (1→1) |
| evolution-selfhost | win (0→0) | win (0→0) | win (0→1) |

- b:b: win 1 / tie 22 / loss 7
- c:c: win 5 / tie 24 / loss 1
- d:d: win 7 / tie 22 / loss 1

## 诊断

- a:a hybrid: calls=30 requested=3000 median_ms=1389.2 p95_ms=1439.8 fallback=0
- a:a fts: calls=30 requested=3000 median_ms=551.7 p95_ms=573.1 fallback=0
- a:a vector: calls=30 requested=3000 median_ms=1357.2 p95_ms=1413.1 fallback=0
- b:b hybrid: calls=30 requested=3000 median_ms=1374.9 p95_ms=1431.8 fallback=0
- b:b fts: calls=30 requested=3000 median_ms=548.3 p95_ms=559.7 fallback=0
- b:b vector: calls=30 requested=3000 median_ms=1382.2 p95_ms=1470.0 fallback=0
- c:c hybrid: calls=30 requested=3000 median_ms=1533.3 p95_ms=2975.6 fallback=0
- c:c fts: calls=30 requested=3000 median_ms=580.1 p95_ms=2066.3 fallback=0
- c:c vector: calls=30 requested=3000 median_ms=1512.2 p95_ms=2895.0 fallback=0
- d:d hybrid: calls=39 requested=3000 median_ms=2673.6 p95_ms=2987.2 fallback=0
- d:d fts: calls=39 requested=3000 median_ms=1828.3 p95_ms=2057.4 fallback=0
- d:d vector: calls=39 requested=3000 median_ms=2715.4 p95_ms=2975.8 fallback=0
