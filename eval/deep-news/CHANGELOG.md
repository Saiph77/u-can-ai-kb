# Changelog — eval/deep-news

## 2026-09-17（第二轮）— 外部审查修复 + 全量重跑

审查发现 2 个 P1（契约偏离、valid 校验不足）与若干 P2（解析器错误分支、报告表述），全部修复并重跑。

### 修复

- **B 恢复冻结控制组**（P1）：`不限发布时间` 题此前被删除该 span，现按 plans/B §2 逐字保留原查询（mode=none，topical=original）。foundation 组结果回到与 A 完全一致；B/C/D 整体分数相应变化（B 全体 Task@5 均值 0.700→0.689）。
- **快照与校验闭环**（P1）：`run.py` 快照改为传递依赖闭包 `STRATEGY_DEPS`（C 含 B，D 含 B+C），修正多目录 `__init__.py` 同名冲突；run.json 新增 `index_manifest_sha256`、`embedding`、`embedding_runtime`；`snapshot_unchanged` 现覆盖全部策略源码与策略配置的前后比对。
- **compare.py 门禁**（P1）：新增 `zg_version`、`index_manifest_sha256`、`embedding`、`embedding_runtime`、`snapshot_unchanged` 一致性检查——此前改内存副本的 zg 版本/模型字段不会被发现。
- **B 解析器错误分支**（P2）：未被消费的第二个 `YYYY年M月` → ambiguous（原静默取第一个）；非法月份（十三月/13 月）→ unsupported（原抛 `IllegalMonthError`）；阶段月份越界 → 回退非阶段（原传播异常）；`stage_trailer` trace 文本坐标切片修正（`colon.end()+e0`）。
- **D 回退崩溃**（P2）：>5 阶段调用 `_single_call` 漏传 `fallback` 参数 → TypeError，已修复并标记 fallback=true。
- **测试 50→55**：30 题阶段窗口 ↔ 金标 frontmatter 月份核对（不再只数个数）、trace 不变量全量断言、非法月份/多年月/超阶段回退用例。

### 第二轮 run-id（全部 valid、snapshot_unchanged）

`a_replay/20260917T065546.517536Z`（回放 0 差异）、`a/065548.152941Z`、`b/065729.714963Z`、`c/065912.691820Z`、`d/070149.215353Z`、`d_no_soft/070610.803868Z`、`d_no_stages/071019.628457Z`（前缀 `20260917T`）。

### 报告表述修正

- 撤下"D-soft 零退步/零代价"：current-cost Hit@1 三路线 1→0 等真实退步已记录（soft 用主题首位换时序正确）。
- 撤下"A→D 单调改善"：B 三路线 Task@5 均下降；改为"末态最优、过程非单调"。
- 修正 B 的 nDCG"全线上升"：vector 实际下降。
- C 的 recall/nDCG 下降改为"口径效应与排序损失无法完全分离"。
- WindowP@5 统一正名 `WindowPrimary@5`（窗内首选成功率）。
- stages 消融归因粒度改为组合机制；演进失败分析区分阶段内 rank 与合并 rank。
- 第一轮 run 目录保留于 `runs/experiments/` 供追溯，不作为结论依据。

## 2026-09-17 — A/B/C/D 实验实施与全量运行

### 新增（`experiments/`）

- 公共框架：`common/runtime.py`（Runtime 契约、预算计账、zg/Replay transport、补集排除 glob）、`common/evaluation.py`（计分与独立 run 归档）、`common/loader.py`（importlib 路径加载）。
- `run.py`：`--variant a|b|c|d`、`--routes`、`--ids`、`--strategy-config`、`--label`、`--replay`；request 白名单隔离 gold；语料/清单/源码前后指纹校验。
- `compare.py`：可比条件校验（语料/题集/金标/计分指纹、qid 集、路线、预算、as_of、valid）→ 指标差值表 + 逐题 win/tie/loss + 调用/耗时诊断。
- 策略：`a_baseline`（原样基线）、`b_normalize`（确定性 QueryPlan 解析器，30/30 题解析与题集一致）、`c_window`（frontmatter 日期硬窗口预筛）、`d_temporal`（`recency.py` 软偏好 S=R(1+wF) + `stages.py` 预算切分/轮转合并 + `config.json`）。
- 测试：50 个单测全过（预算边界、空集合短路、越界拒绝、回放保真、语法边界、数学性质、合并语义、配置校验）。

### 实验产物（`runs/experiments/`）

| label | run-id 目录 | valid | 说明 |
|---|---|---|---|
| a_replay | `a_replay/20260917T040315.049343Z` | ✓ | 历史 90 调用回放，与 0915 基线逐项一致 |
| a | `a/20260917T040329.995225Z` | ✓ | 真实基线，复现历史分数 |
| b | `b/20260917T040508.025918Z` | ✓ | 归一化臂 |
| c | `c/20260917T040657.705333Z` | ✓ | 硬窗口臂 |
| d | `d/20260917T040928.829509Z` | ✓ | 全机制 |
| d_no_soft | `d_no_soft/20260917T041327.867044Z` | ✓ | stages-only 对照 |
| d_no_stages | `d_no_stages/20260917T041724.999736Z` | ✓ | soft-only 对照 |

### 结果摘要

Task@5：A .800 → B .767 → C .900（fts 峰值）→ **D .967（fts）/.933（hybrid）**；latest/historical 在 C/D 全部修复；evolution AllStages .333→.722。详见 `experiments/RESULTS.md`。

### 文档

`experiments/README.md`（运行与契约）、四个 variant 各自 `README.md`/`RESULTS.md`、`experiments/RESULTS.md` 总报告、`COMPARE-ABCD.md`、`COMPARE-D-CONTROLS.md`。

### 未改动

旧评测脚本、题集、金标、语料、索引、viewer、upstream 均未触碰；分数提升不构成验收门槛，退步（B 的时间题、C 的 recall/nDCG 口径）已如实记录于各 RESULTS。
