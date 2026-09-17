# A RESULTS — 冻结基线

## 离线回放（复现验收）

- run：`runs/experiments/a_replay/20260917T040315.049343Z/`
- transport：ReplayTransport，输入 `runs/20260915T091207.064600Z/latest.json` 的 90 条 raw_hits。
- 结果：30 题 × 3 路线的最终文档顺序、全部单题指标、summary 与 by_kind 与历史结果**逐项一致**（脚本比对 0 差异，浮点容差 ≤1e-12）。

## 真实运行（基线分数）

- run：`runs/experiments/a/20260917T040329.995225Z/`；valid=true；zg 0.2.2；30 题 × 3 路线 × 1 调用，limit=100。
- 与 2026-09-15 历史结果一致（同指纹、同语料、同模型）：逐题 hits/metrics 无变化。

| route | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowP@5 | StageCov@5 | AllStages@5 | CandidateTask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid | 0.833 | 1.000 | 0.748 | 0.800 | 0.889 | 0.694 | 0.333 | 0.967 |
| fts | 0.733 | 1.000 | 0.729 | 0.800 | 0.889 | 0.639 | 0.333 | 0.967 |
| vector | 0.500 | 0.800 | 0.528 | 0.700 | 0.833 | 0.389 | 0.333 | 0.933 |

- 失败题（hybrid）：evolution-memory、historical-mcp、evolution-mcp、evolution-cost、latest-selfhost、evolution-selfhost——与历史报告相同。
- 耗时（单轮顺序运行，仅诊断）：median hybrid 1290ms / fts 529ms / vector 1282ms。

## 说明

「离线复现一致」与「真实运行分数」是两次不同实验；本文件分别列出。基线复现包含重复片段占用 100 片段预算的原始行为，未扩大 limit。
