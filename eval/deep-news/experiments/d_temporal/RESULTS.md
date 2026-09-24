# D RESULTS — 软时间偏好 + 分阶段覆盖

三组全量真实运行均 valid=true、snapshot_unchanged=true、0 错误（第二轮修正后 run-id）：

- `runs/experiments/d/20260917T070149.215353Z/`
- `runs/experiments/d_no_soft/20260917T070610.803868Z/`
- `runs/experiments/d_no_stages/20260917T071019.628457Z/`

| label | Task@5 (h/f/v) | WindowPrimary@5 (h/f/v) | AllStages@5 (h/f/v) | StageCov@5 (h/f/v) |
|---|---|---|---|---|
| d | .933/.967/.833 | 1.000/1.000/.889 | .667/.833/.667 | .889/.944/.889 |
| d_no_soft | .933/.967/.833 | .944/.944/.889 | .667/.833/.667 | .889/.944/.889 |
| d_no_stages | .867/.900/.767 | 1.000/1.000/.889 | .333/.500/.333 | .694/.778/.500 |
| （参照）c | .867/.900/.767 | .944/.944/.889 | .333/.500/.333 | .694/.778/.500 |
| （参照）a | .800/.800/.700 | .889/.889/.833 | .333/.333/.333 | .694/.639/.389 |

## 机制归因（对照实验）

- **stages 机制**（d vs d_no_stages）：evolution 组 Task@5 均值 .722 vs .389；AllStages .722→.389；StageCoverage .907→.657；evolution CandidateTask 1.000→.889（h/f）/.667（v）。**注意归因粒度**：该对照同时改变了「分阶段查询、阶段窗口预筛、预算切分、轮转合并」四个环节，证据支持的是这个组合的净收益，不能单独归功于轮转合并。
- **一致性校验**：d_no_stages 的 Task@5/StageCov/AllStages 与 C 逐项相等，验证「关闭 stages 即回到 C/B 行为」；且 d_no_stages 的 current 组 WindowPrimary@5（1.000/1.000/.667）高于 C（.833/.833/.667），即 soft 在 stages 关闭时仍有独立贡献。
- **soft 机制**（d vs d_no_soft）：Task@5 不变（current 题任务定义不硬判窗口），current 组 WindowPrimary@5 均值 .778→.889。**但不是零代价**——逐题退步真实存在：
  - `current-cost` 三路线 Hit@1 1→0、MRR@10 1→0.25、首个相关位 1→4（代价）；同时 WindowPrimary@5 0→1（收益：top1 从窗外主题相关换成了窗内首选）。即 soft 在这题上**用主题首位换了时序正确**。
  - `current-router` hybrid Recall@5 1.0→0.5、fts nDCG@10 1.0→0.877。
  - 净结论：soft 提高"近期首选命中率"（WindowPrimary +.111），但牺牲部分主题排序指标；收益温和、代价真实，权重 0.25 是预设值未调优。
- **调用成本**：d 每路线 39 次调用（30 + 9 次阶段调用），median 耗时约 2×A。预算严格 ≤100/题/路线（requested_limit 实测 3000/路线达标）。

## 剩余失败（按合并后 rank 与阶段内 rank 分列）

| 失败项 | 缺失阶段 | 阶段内 call_rank | 合并后 rank | 性质 |
|---|---|---:|---:|---|
| evolution-memory / hybrid | august | 3 | 8 | 阶段内不浅但合并后出 Top5 |
| evolution-memory / vector | august | 13 | 38 | 阶段内召回深度不足 |
| evolution-cost / hybrid | september | 4 | 12 | 两者兼有 |
| evolution-cost / fts | september | 2 | 6 | **合并名额问题**：阶段第 2 名在 3 阶段轮转下落位 6，刚好出 Top5 |
| evolution-cost / vector | september | 11 | 33 | 阶段内召回深度不足 |

因此剩余失败有两类成因：**(a) 阶段内召回/排序深度**（金标在阶段内已排到 11–13 位）；**(b) Top5 的阶段名额分配**（3 阶段轮转下各阶段第 2 篇落在合并 rank 4–6）。修复方向不限于新增 reranker——例如 Top5 名额分配策略（保证每阶段第 1 名外再留第二名缓冲）也值得评估。

- `evolution-mcp` 本轮三路线全部通过（修正此前"仍缺候选"的过时描述）。
- current/foundation 的 vector 各 1 题失败（current-selfhost、foundation-router、foundation-selfhost）为内容排序问题，与时间机制无关。

## 结论边界

参数为预设实验值（60/30/0.25），未经调优；R 是排序先验而非校准概率。分阶段调用改变 zg 内部召回特征，固定总 limit 是资源控制而非等价计算量——故如实报告调用数与耗时。
