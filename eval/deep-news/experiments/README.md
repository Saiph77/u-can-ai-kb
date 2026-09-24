# Deep News 时间感知检索实验（A/B/C/D）

按 [plans/README.md](../plans/README.md) 统一契约实现并已跑完全量实验。四个变体严格递进，每步只加一个机制以便归因；策略端经 request 白名单隔离，不可见 gold。

## 运行

```bash
cd <repo root>
python3 eval/deep-news/experiments/run.py --variant a   # 冻结基线
python3 eval/deep-news/experiments/run.py --variant b   # 查询归一化
python3 eval/deep-news/experiments/run.py --variant c   # 硬窗口预筛
python3 eval/deep-news/experiments/run.py --variant d   # 软时间+分阶段（默认读 d_temporal/config.json）
# 机制关闭对照
python3 eval/deep-news/experiments/run.py --variant d --strategy-config <cfg> --label d_no_soft
# 对比（显式 run 文件，不猜 latest）
python3 eval/deep-news/experiments/compare.py <runA.json> <runB.json> ...
# 离线回放（历史 raw_hits 做 fake transport）
python3 eval/deep-news/experiments/run.py --variant a --replay <history.json> --label a_replay
```

## 结构

```
experiments/
  run.py              # CLI：--variant/--routes/--ids/--strategy-config/--label/--replay
  compare.py          # 可比性校验 + 逐题 win/tie/loss
  common/
    loader.py         # importlib 按路径加载，模块名唯一
    runtime.py        # Runtime 契约、zg/Replay transport、预算计账、补集 glob
    evaluation.py     # 复用旧 metrics_for/aggregate 的计分与归档
  a_baseline/  b_normalize/  c_window/  d_temporal/
    strategy.py (+ normalize/recency/stages)  test_*.py  README.md  RESULTS.md
```

## 契约要点（实现侧）

- `runtime.retrieve(query, route, budget, allowed_paths=None)`：累计 `requested_limit` 超过 `candidate_budget` 抛 `BudgetError`；`allowed_paths=[]` 短路不调用、不耗预算；返回文档全部在 scope 内否则 `TransportError`。
- `allowed_paths` 编码为补集排除 glob：`-g deep-news/articles/*.md` 后按稳定序追加 `!path`，再接 `!eval/**`（依赖 zg 规则顺序覆盖语义，见 C-WINDOW §3）。
- `ranked_documents` 保留全部去重候选，rank 连续；评分端自行切 Top10 并在全量上算 CandidateTask。
- 产物目录 `runs/experiments/<label>/<run-id>/`：`run.json`、`run.md`、`checkpoint.json`、`src/` 源码快照、`strategy-config.json`、题集与金标副本。**不写共享 latest 文件**。
- 源码快照覆盖**传递依赖闭包**（C→B，D→B+C，见 `run.py` 的 `STRATEGY_DEPS`）；run.json 另记录 `zg_version`、`index_manifest_sha256`、`embedding`、`embedding_runtime`。`valid=true` 要求运行前后语料、题集、金标、评分脚本、**全部策略源码与配置**逐字节未变。
- `compare.py` 在比分数前先校验：as_of、预算、题集/金标/评分指纹、语料指纹、zg 版本、索引 manifest 指纹、embedding 配置、qid 集合、路线集合、`valid` 与 `snapshot_unchanged`。
- ReplayTransport 按 `(query, route)` 顺序回放记录的 raw_hits，`allowed_paths` 做前置过滤；找不到记录即报错，不允许凭空召回。

## 测试

```bash
python3 -m unittest discover -s eval/deep-news/experiments -p 'test_*.py' -v
# 55 tests: runtime 预算/范围、A 透传、B 30 题一致性（含阶段窗口↔金标月份核对、
# trace 坐标不变量）+语法边界（非法月份、多年月歧义、不限发布控制组逐字保留）、
# C 窗口路由、D 数学/预算/合并/超阶段回退
```
