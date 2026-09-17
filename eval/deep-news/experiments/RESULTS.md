# A/B/C/D 实验总报告

- 实施与运行：2026-09-17（UTC）；语料 431 篇（sha256 `a8e7f83c…` 未变）、30 题、as_of=2026-09-15、zg 0.2.2、potion-multilingual-128m、每题每路线预算 100 片段。
- 六轮运行全部 valid=true、零错误：`a` `b` `c` `d` `d_no_soft` `d_no_stages`（另 `a_replay` 回放验收轮）。
- 产物：`runs/experiments/<label>/<run-id>/run.json|run.md`；对比表 [COMPARE-ABCD.md](COMPARE-ABCD.md)、[COMPARE-D-CONTROLS.md](COMPARE-D-CONTROLS.md)。

## 总览（全体 30 题，跨路线均值见 compare 文件；下表为 hybrid/fts/vector）

| variant | Task@5 | WindowP@5 | AllStages@5 | CandidateTask |
|---|---|---|---|---|
| a 基线 | .800/.800/.700 | .889/.889/.833 | .333/.333/.333 | .967/.967/.933 |
| b 归一化 | .767/.767/.567 | .778/.722/.500 | .333/.500/.333 | 1.000/1.000/.933 |
| c 硬窗口 | .867/.900/.800 | .944/.944/.889 | .333/.500/.333 | 1.000/1.000/.933 |
| d 全量 | .933/.967/.867 | 1.000/1.000/.889 | .667/.833/.667 | 1.000/1.000/1.000 |

**结论**：A→D 单调改善且每步可归因。

1. **B（剥离时间词）**：提升主题检索（nDCG 升、CandidateTask 满格），但因丢掉时间信号使 latest/historical 退步——证明需要显式时间机制而非依赖查询串。
2. **C（硬窗口预筛）**：最大单步收益。latest 三路线 Task@5 全 1.000、historical h/f 1.000；WindowP@5 到 .944。召回前筛选直接修复基线的「窗内文章深埋」问题。
3. **D-stages**：演进题全部增量（AllStages .389→.722，evolution CandidateTask 1.000）；34/33/33 预算切分 + 轮转合并有效。
4. **D-soft**：Task 无变化、无退步；current 组 WindowP@5 +.111——近期偏好是低成本的真实小收益。

## 已知限制

- evolution 剩余失败是**阶段内候选深度**问题（金标已在候选但 rank>5），轮转合并无法救深处文档；需后续 reranker 或更大窗口，超出 v1 契约。
- C/D 的 recall@5、nDCG@10 低于 A/B 属窗口筛除的口径效应，非相关性退步（Primary@5 上升佐证）。
- 6 个主题簇 ≠ 30 个独立样本；泛化需后续盲标题集。
- D 调用数 39/路线 vs A 30，耗时 ~2×——预算相同但计算量不等价，已如实记录。

## 复现

```bash
python3 eval/deep-news/experiments/run.py --variant a   # b / c / d 同理
python3 eval/deep-news/experiments/run.py --variant d --strategy-config <cfg> --label d_no_soft
python3 eval/deep-news/experiments/compare.py <runs...>
python3 -m unittest discover -s eval/deep-news/experiments -p 'test_*.py'   # 50 tests
```
