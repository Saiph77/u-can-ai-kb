# A/B/C/D 实验总报告

- 第二轮（修正审查发现的问题后重跑）：2026-09-17 UTC；语料 431 篇（sha256 `a8e7f83c…` 未变）、30 题、as_of=2026-09-15、zg 0.2.2、potion-multilingual-128m（metal）、每题每路线预算 100 片段。
- 七轮运行全部 `valid=true`、`snapshot_unchanged=true`、零错误：a_replay、a、b、c、d、d_no_soft、d_no_stages。
- 产物：`runs/experiments/<label>/<run-id>/run.json|run.md`；对比表 [COMPARE-ABCD.md](COMPARE-ABCD.md)、[COMPARE-D-CONTROLS.md](COMPARE-D-CONTROLS.md)。

## 与第一轮的区别（见 [CHANGELOG](../CHANGELOG.md)）

1. B 恢复契约：`不限发布时间` 题逐字保留原查询（冻结控制组），B/C/D 的 foundation 结果与 A 完全一致。
2. 快照覆盖传递依赖（C→B，D→B+C）；run.json 记录 zg 版本、索引 manifest 与 embedding 指纹；运行前后校验全部策略源码与配置。
3. `compare.py` 增加 zg 版本/索引指纹/embedding/`snapshot_unchanged` 可比性门禁。
4. B 解析器补齐错误分支（非法月份→unsupported、多 `YYYY年M月`→ambiguous、阶段月越界回退、trace 坐标修正）；D 修复 >5 阶段回退崩溃。
5. 测试 50→55，新增阶段边界核对与 trace 不变量。

## 总览（hybrid/fts/vector；全体均值为跨路线均值，见 COMPARE 文件）

| variant | Task@5 | WindowPrimary@5 | AllStages@5 | CandidateTask |
|---|---|---|---|---|
| a 基线 | .800/.800/.700 | .889/.889/.833 | .333/.333/.333 | .967/.967/.933 |
| b 归一化 | .767/.767/.533 | .778/.722/.500 | .333/.500/.333 | 1.000/1.000/.933 |
| c 硬窗口 | .867/.900/.767 | .944/.944/.889 | .333/.500/.333 | 1.000/1.000/.933 |
| d 全量 | .933/.967/.833 | 1.000/1.000/.889 | .667/.833/.667 | 1.000/1.000/1.000 |

**结论**：末态 D 显著优于基线（Task@5 全体均值 .767→.911），但**过程非单调**——B 在三条路线均下降（其消融目的即证明需要显式时间机制）。

1. **B（剥离时间词）**：主题检索改善（Hit@1 .689→.756、CandidateTask h/f 满格），但 WindowPrimary@5 .870→.667、Task@5 全体下降——时间词不是有益隐式信号。
2. **C（硬窗口预筛）**：最大单步收益。latest/historical 两组 Task@5 与 WindowPrimary@5 三路线全部 1.000。
3. **D-stages（分阶段查询+窗口+预算切分+轮转合并的组合）**：演进题主要增量（AllStages .389→.722，evolution CandidateTask 1.000）；归因粒度为该组合整体，非轮转合并单独贡献。
4. **D-soft（近期软加权）**：current 组 WindowPrimary@5 +.111（.778→.889），Task@5 不变；但有真实逐题退步（current-cost Hit@1 1→0 三路线、current-router 部分相关性指标下降）——用少量主题首位换取时序正确，非零代价。

## 已知限制

- evolution 剩余失败混合两类成因：阶段内召回深度（金标 call_rank 11–13）与 Top5 阶段名额分配（3 阶段轮转下阶段第 2 名落在合并 rank 4–6）。见 d_temporal/RESULTS.md。
- C/D 的 recall@5、nDCG@10 低于 A/B 含口径效应（窗外 grade-2 文档被筛除后不再计分），但不能完全排除排序损失——本设计无法分离两者。
- `WindowPrimary@5` = Top5 命中窗内首选的成功率，非窗口内 precision。
- 6 个主题簇 × 5 类意图 ≠ 30 个独立样本；B 解析器与题集措辞存在共设计，泛化需独立盲测集。
- D 每路线 39 次调用 vs A 30 次，耗时 ~2×——预算相同但计算量不等价。

## 复现

```bash
python3 eval/deep-news/experiments/run.py --variant a   # b / c / d 同理
python3 eval/deep-news/experiments/run.py --variant d \
    --strategy-config eval/deep-news/experiments/d_temporal/config.no_soft.json --label d_no_soft
python3 eval/deep-news/experiments/compare.py <runs...>
python3 -m unittest discover -s eval/deep-news/experiments -p 'test_*.py'   # 55 tests
```
