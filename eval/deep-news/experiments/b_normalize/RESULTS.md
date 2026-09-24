# B RESULTS — 查询归一化

- run：`runs/experiments/b/20260917T065729.714963Z/`；valid=true；snapshot_unchanged=true；30 题 × 3 路线 × 1 调用。
- 解析一致性（评分端复核）：30/30 题 mode、window 与题集声明一致；6 道演进题阶段数一致，且每阶段的 frontmatter 月份均落在对应 stage window 内；trace 坐标不变量全量通过。
- **控制组**：6 道 foundation（不限发布时间）题 topical_query 与原查询逐字一致，结果与 A 完全相同——本轮修正后不再含控制组污染。
- 对照 A（`compare.py`；逐题 win/tie/loss 见 COMPARE-ABCD.md）：

| route | Hit@1 | Primary@5 | nDCG@10 | Task@5 | WindowPrimary@5 | StageCov@5 | AllStages@5 | CandidateTask |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid | 0.933 | 1.000 | 0.804 | 0.767 | 0.778 | 0.694 | 0.333 | 1.000 |
| fts | 0.833 | 1.000 | 0.757 | 0.767 | 0.722 | 0.778 | 0.500 | 1.000 |
| vector | 0.500 | 0.767 | 0.506 | 0.533 | 0.500 | 0.500 | 0.333 | 0.933 |

## 解读

- **剥离时间词提升主题检索**：Hit@1 全体均值 0.689→0.756（hybrid .833→.933）；nDCG@10 hybrid .748→.804、fts .729→.757 上升，**vector .528→.506 反而下降**（修正此前"全线上升"的错误表述）。CandidateTask hybrid/fts 达 1.000。
- **代价是丢掉唯一的时间信号**：WindowPrimary@5 全体 0.870→0.667，Task@5 全体 0.767→0.689（hybrid/fts .800→.767，vector .700→.533）。这证明时间词混入查询不是有益的隐式过滤，需要显式机制——B 作为消融臂达到预期目的。
- evolution 有小幅改善（fts StageCov .639→.778、AllStages .333→.500）：合并后的主题查询把多阶段意图压进单次检索，但无阶段窗口保证。

## 结论边界

B 的改善只能归因于查询规范化；不能声称时间筛选或重排的收益。30 题属 6 个主题簇，非独立随机样本。
