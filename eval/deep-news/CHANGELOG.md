# Changelog — eval/deep-news

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
