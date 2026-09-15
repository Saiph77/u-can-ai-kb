# Deep News A / B / C / D 实现计划与统一契约

本目录是实现任务书，尚未实现下面描述的新接口和命令。交接时给每个 agent **本文 + 对应方案文件**。本轮不启动 agent、不改算法、不运行新实验。

## 1. 四个版本与责任

| 版本 | 行为 | 负责人独占写入范围 | 任务书 |
|---|---|---|---|
| A | 原查询、原范围、原排名；统一评测与对照工具 | `experiments/common/`、`experiments/a_baseline/`、`experiments/run.py`、`experiments/compare.py`、`experiments/__init__.py`、`experiments/.gitignore` | [A 基线](A-BASELINE.md) |
| B | A + 从查询文本分离时间表达，仅用主题检索 | `experiments/b_normalize/` | [B 查询解析](B-NORMALIZE.md) |
| C | B + 对显式时间窗口在召回前筛选文章 | `experiments/c_window/` | [C 日期筛选](C-WINDOW.md) |
| D | C + 软偏好加权；演进问题分阶段召回与覆盖选择 | `experiments/d_temporal/` | [D 时间与阶段策略](D-TEMPORAL.md) |

表内 `experiments/` 均相对 `eval/deep-news/`。每个目录下的测试、说明、配置属于对应负责人。公共产物写入 `eval/deep-news/runs/experiments/<variant>/<run-id>/`，各轮独立目录，**不写任何共享 latest 文件**。

所有 agent 都不是独自在仓库工作：不得回滚其他人的修改，不得越过上述所有权。方案文件、现有评测、知识库正文、viewer、upstream 子模块和根级文件均只读。若发现共用代码问题，向 A 提交具体接口需求，由 A 修改，其他 agent 不直接补丁。

### 并行与集成

- A/B/C/D 可同时开发。B/C/D 使用本文的普通 dict 契约、注入式依赖和各自本地测试替身，不等待别人文件，也不复制一份“公共实现”。
- 真实依赖：B 依赖 A 的运行环境；C 依赖 B 的解析器与 A 的 transport；D 依赖 B/C/A。
- A 只做自己的基线全量验收。B 等 A/B 就绪后验收 B；C 等 A/B/C 就绪；D 最后验收组合 D。等待集成不等于独立开发被阻塞。
- 需要独立 checkout 时，源码可在不同 worktree 开发；**正式评测回到同一个冻结语料/索引的 checkout**。不要在缺少正文或不同索引的 worktree 上生成可比较结果。
- 先用历史输出离线回放，再按 A→B→C→D 顺序跑正式实验，避免并行进程争用 embedding 设备污染耗时对比。不要为每个 agent 重建或改写索引。

## 2. 固定条件与证据

固定 30 题、431 篇文章、as_of=`2026-09-15`；三路线 hybrid/fts/vector；每个题目每条路线的**所有检索调用预算之和 ≤100 片段**；最终 Top10 文章。

| 文件 / 语料 | 当前 SHA256 |
|---|---|
| `eval/deep-news/queries.json` | `96f0b45c66491f459616520bd37262d0cd467ac4c7469c9c37fcd4a962cff6f1` |
| `eval/deep-news/judgments.json` | `2e0edb23f2695f1d757e8cdad9f4ae317e8c6cc9c2db8acd5df7b7cc15236b46` |
| `eval/deep-news/run.py` | `0d9273f70cd1b8e4686758cde51a8fa3d7df60765dca88fb5a9b7f4bb46120eb` |
| `eval/zg/run.py` | `caa867e0e34d0d4b486cd09344c618e331714ff90da359b0d5b9ed7503962a6a` |
| Deep News 语料整体指纹 | `a8e7f83cbad252dfd9e84a8904f35b188b8f2eb68be528137e02939b6a8acba9` |

历史基线：[完整 JSON](../runs/20260915T091207.064600Z/latest.json)、[结果说明](../RESULTS.md)。模型固定 local/potion-multilingual-128m，zg 0.2.2。发现指纹、版本或模型变化时，保存差异并拒绝标记为同条件实验，不能偷偷重写预期值。

现有代码入口：[日期/语料/时间计分](../run.py)、[输出解析/文章聚合/内容计分](../../zg/run.py)。只通过动态导入或普通模块导入复用纯函数；**不调用两个旧脚本的 main，也不修改其全局 ROOT/RUNS**。

## 3. 统一输入：策略不得获得答案

策略公开入口：

```python
def search(request: dict, runtime) -> dict:
    ...
```

`request` 只允许：

```json
{
  "query": "只找 2026 年六月发布的 MCP 协议演进分析，关注自动执行、用户参与和授权边界。",
  "as_of": "2026-09-15",
  "route": "hybrid",
  "candidate_budget": 100
}
```

不得包含 q.id、kind、topic、time、relevant、stages、evidence_ref 或 judgment。评测主进程单独保存这些字段，仅在检索结束后计分。策略不得读取题集、历史结果、证据文件来决定返回文章；不得按固定查询句子或 id 建答案映射。

允许策略访问 runtime 提供的冻结文章 `path → published_at` 元数据。日期来自 frontmatter，不来自文件名或 mtime。是否读取正文应在策略配置中显式记录；v1 的 B/C/D 均不另加全文/模型 reranker。

这属于代码层的数据隔离，非进程级安全沙箱；验收需检查策略读文件与依赖路径，防止主动读取金标。

## 4. B 提供的 QueryPlan 契约

```json
{
  "schema_version": 1,
  "original_query": "只找 2026 年六月发布的 MCP 协议演进分析……",
  "topical_query": "MCP 协议演进分析，关注自动执行、用户参与和授权边界。",
  "mode": "window",
  "window": {"start": "2026-06-01", "end": "2026-06-30"},
  "stages": [],
  "status": "ok",
  "warnings": [],
  "trace": [{"rule": "year_month", "text": "2026 年六月", "start": 3, "end": 11}]
}
```

示例中的 span 数字仅示意，实际代码必须准确记录原字符串位置；区间 `[start,end)`。

- `mode`：`none | window | prefer_recent | stages`。
- `status`：`ok | ambiguous | unsupported`。后两者必须原样查询、禁用日期策略，并保存原因；不猜窗口、不读取 gold 补全。
- `window` 不适用时为 null。日期均 YYYY-MM-DD，包含起止日。
- `stages` 每项：`{id, topical_query, window, source_span}`；id 是解析顺序的 `stage-1` 等，不来自金标。
- 时间约束从 `query + as_of` 推出。`kind/time/stages` 只能在评分端用来检查解析准确性。
- 无时间题原样保留；不能因遇到文章中的产品年份、版本号或数字就删词。

## 5. Runtime 契约（A 实现）

```python
runtime.documents  # dict[path, {"published_at": "YYYY-MM-DD"}]
runtime.strategy_config  # 当前策略的只读配置 dict；无配置时为空
runtime.retrieve(query: str, route: str, budget: int,
                 allowed_paths: list[str] | None = None) -> dict
```

返回：`{call_id, command, stdout, stderr, returncode, elapsed_ms, raw_hits, documents}`。

- `documents` 是该调用完整的去重文章序列，包含 path、published_at、call_rank、raw_rank、matched_by；不是截取后的 Top10。
- `allowed_paths=None` 表示全部 Deep News 文章；`[]` 表示合法空范围，返回空结果、不得调用无约束检索。
- A 在每次调用前检查预算，累计 `requested_limit`，超过 request.candidate_budget 直接报配置错误。重试同样计入预算，v1 默认不自动重试。
- A 负责日志、计时、zg stdout 解析、路径范围校验和预算计账。C 负责提供路径集合并验证其日期正确。
- 公共 CLI 支持 `--strategy-config <path>`，将配置经字段校验后放入 runtime.strategy_config，并归档配置原文与哈希。D 未指定时加载其目录下的 config.json；A/B/C 默认空配置。控制实验仍使用 variant=d，通过配置指纹和报告标签区分。
- allowed_paths 如何编码为 zg globs 属于 A 的 transport 责任，具体建议见 C 方案。只允许 `subprocess.run(list, shell=False)`，拒绝注入式拼接。
- A/B/C 每题每路线通常一次调用、limit=100。D 分阶段调用共享总预算，不复用前面其他版本的召回当作免费的额外候选。

## 6. SearchResult 与计分

```json
{
  "plan": {},
  "ranked_documents": [
    {"path": "deep-news/articles/example.md", "rank": 1,
     "published_at": "2026-09-04", "score": null,
     "provenance": [{"call_id": "call-1", "call_rank": 47, "raw_rank": 88}],
     "reason": "original_order"}
  ],
  "diagnostics": {"fallback": false, "policy": "baseline"}
}
```

- `ranked_documents` 保留策略处理后的**全部唯一候选文档**，顺序决定前十；rank 从 1 连续增长。没有召回来源的文档不许凭空加入，发布日期必须由冻结 metadata 回填。
- 调用原 `metrics_for(ranked_documents, gold_query, corpus)`；该函数自己截取前十/前五，并在完整列表计算 CandidateTask。不得先截 Top10 导致候选成功率失真。
- 整轮保留原 summary/by_kind/items/metric_n；额外写 variant、strategy config/hash、QueryPlan、所有实际调用、预算、候选数、总耗时、版本和源文件快照。
- 所有运行写独立目录，前后检查 corpus、manifest、题集、证据、加载的全部策略源码和配置没有变化。有错误不缩小分母；整轮 valid=false、退出非 0。无结果本身是合法 0 分。
- 比较前必须匹配 corpus/model/zg/queries/judgments/scorer 指纹、qid 集、路线、总预算。策略源码可不同，正是比较对象。解析错误/回退率也要报告，不能只展示成功解析的题。

## 7. 统一验收与交付

每个 agent 交付其目录内实现、测试、README、RESULTS；结果引用本策略独立 run 路径。不要在仓库根目录补文档、commit/push 或接入 viewer，除非用户另行要求。

预期公共命令（由 A 实现，当前不存在）：

```bash
python3 eval/deep-news/experiments/run.py --variant a --routes hybrid,fts,vector
python3 eval/deep-news/experiments/run.py --variant b --routes hybrid,fts,vector
python3 eval/deep-news/experiments/run.py --variant c --routes hybrid,fts,vector
python3 eval/deep-news/experiments/run.py --variant d --routes hybrid,fts,vector
python3 eval/deep-news/experiments/compare.py --runs <A.json> <B.json> <C.json> <D.json>
```

每个版本运行全部 30 题 × 3 路线；D 可能多次调用，但每题每路线预算相同。正确实现、数据可追溯是硬验收；**分数提升不是必须达成的验收门槛**。出现退步应解释，不能通过改金标、删失败题或定向补召回来达标。

现有六主题作为开发集，不宣称泛化。新增盲标、独立主题测试集是后续工作，不让四个 agent 各自修改一份“更适合自己”的题集。
