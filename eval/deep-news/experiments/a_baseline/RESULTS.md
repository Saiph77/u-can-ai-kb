# A RESULTS — 冻结基线

## 离线回放（复现验收）

- run：`runs/experiments/a_replay/20260917T065546.517536Z/`（第二轮修正后重跑）
- transport：ReplayTransport，输入 `runs/20260915T091207.064600Z/latest.json` 的 90 条 raw_hits。
- 结果：30 题 × 3 路线的去重文档顺序与全部单题指标与历史结果**逐项一致**（脚本比对 0 差异，容差 ≤1e-12）。

## 真实运行（基线分数）

- run：`runs/experiments/a/20260917T065548.152941Z/`；valid=true；snapshot_unchanged=true；zg 0.2.2 / potion-multilingual-128m / 索引 manifest 指纹已记录进 run.json。
- 30 题 × 3 路线 × 1 调用，limit=100；指标与历史基线一致。

| route | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowPrimary@5 | StageCov@5 | AllStages@5 | CandidateTask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid | 0.833 | 1.000 | 0.748 | 0.800 | 0.889 | 0.694 | 0.333 | 0.967 |
| fts | 0.733 | 1.000 | 0.729 | 0.800 | 0.889 | 0.639 | 0.333 | 0.967 |
| vector | 0.500 | 0.800 | 0.528 | 0.700 | 0.833 | 0.389 | 0.333 | 0.933 |

- hybrid 失败题：evolution-memory、historical-mcp、evolution-mcp、evolution-cost、latest-selfhost、evolution-selfhost。
- 耗时（单轮顺序运行，仅诊断）：median hybrid 1389ms / fts 552ms / vector 1357ms。

## 说明

「离线复现一致」与「真实运行分数」是两次不同实验；本文件分别列出。基线复现包含重复片段占用 100 片段预算的原始行为，未扩大 limit。

## 指标口径

- `WindowPrimary@5` = Top5 是否命中**窗口内** grade-2 金标（成功率，非窗口内 precision）。
- `CandidateTask` 在完整候选列表上算任务成功，不受 Top10 截断影响。
