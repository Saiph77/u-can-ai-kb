# C RESULTS — 硬窗口预筛

- run：`runs/experiments/c/20260917T040657.705333Z/`；valid=true；0 运行错误。
- 所有 window 题输出日期 100% 合规（allowed 集合校验 + transport 越界断言）；无空集合题触发。
- 对照 B/A（compare.py）：

| route | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowP@5 | StageCov@5 | AllStages@5 | CandidateTask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid | 0.833 | 1.000 | 0.661 | 0.867 | 0.944 | 0.694 | 0.333 | 1.000 |
| fts | 0.767 | 1.000 | 0.653 | 0.900 | 0.944 | 0.778 | 0.500 | 1.000 |
| vector | 0.567 | 0.867 | 0.500 | 0.800 | 0.889 | 0.500 | 0.333 | 0.933 |

## 解读

- **硬窗口是最大单步收益**：latest/historical 两组 WindowPrimary@5 达 0.944（hybrid/fts），latest Task@5 三路线全部 1.000，historical 1.000（hybrid/fts）——基线中「召回在 rank 16–47 的窗口内文章」问题被预筛直接解决。
- Task@5 全体：A 0.800 → B 0.767 → C 0.867/0.900/0.800。B 丢掉的时间信号由 C 用确定性方式补回并超过基线。
- **nDCG@10 / Recall@5 的下降是指标口径副作用，非相关性退步**：窗外的高分文档（同主题不同时期）被筛除后不再计入 recall/nDCG 分母覆盖。Primary@5 反而上升（vector .800→.867）说明窗内排序仍健康。
- evolution 未变（与 B 相同的单次主题检索）：等待 D 的分阶段机制。
- 特别核查 latest-selfhost（基线失败题）：C 三路线全部修复；historical-mcp hybrid 修复、fts/vector 仍受候选深度影响。

## 结论边界

窗口内文档数不足时只返回实际篇数，不凑数；日期来自 frontmatter 而非文件名（34/431 文件名日期不一致的坑已规避）。
