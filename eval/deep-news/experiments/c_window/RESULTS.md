# C RESULTS — 硬窗口预筛

- run：`runs/experiments/c/20260917T065912.691820Z/`；valid=true；snapshot_unchanged=true；0 运行错误。
- 所有 window 题输出日期 100% 在声明窗口内（allowed 集合校验 + transport 越界断言）；无空集合题触发；窗内文档不足时只返回实际篇数。
- 对照 B/A（compare.py）：

| route | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowPrimary@5 | StageCov@5 | AllStages@5 | CandidateTask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid | 0.833 | 1.000 | 0.662 | 0.867 | 0.944 | 0.694 | 0.333 | 1.000 |
| fts | 0.733 | 1.000 | 0.641 | 0.900 | 0.944 | 0.778 | 0.500 | 1.000 |
| vector | 0.567 | 0.833 | 0.494 | 0.767 | 0.889 | 0.500 | 0.333 | 0.933 |

## 解读

- **硬窗口是显著单步收益**：latest/historical 两组 Task@5 与 WindowPrimary@5 三路线全部 1.000——基线中"窗内文章深埋 rank 16–47"的问题被召回前筛选直接解决。
- Task@5 全体：A 0.767 → B 0.689 → C 0.844。B 丢掉的时间信号由 C 用确定性方式补回并超过基线。
- **recall@5 / nDCG@10 低于 A/B 需要谨慎归因**：窗外同主题文档被筛除后不再计入分母覆盖，这是口径效应；但不能据此断言排序毫无损失——窗外 grade-2 文档对核心指标仍计分，两种效应并存，本设计无法完全分离。
- evolution 与 B 相同（单次主题检索，无阶段机制）：等待 D。
- 逐题核查：latest-selfhost（基线失败题）三路线修复；historical-mcp 基线 hybrid 失败 → C 修复。

## 结论边界

`WindowPrimary@5` 是"Top5 命中窗内首选"的成功率，值为 1 不代表五篇都在窗内；日期取 frontmatter 而非文件名（规避 34/431 文件名日期不一致）。
