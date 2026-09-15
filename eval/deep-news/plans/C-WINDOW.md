# C：明确日期要求的召回前筛选

## 任务与边界

验证在 B 主题查询基础上，将用户明确的日期范围用于**召回前限制语料**，能否改善近期与历史题。先读 [统一契约](README.md)。你只写 `experiments/c_window/`；B 负责解析，A 负责 transport，禁止修改他们的文件。

C 不做时间加权，不拆分演进检索，不改相同允许集合内的原始排名。

## 1. 文件与接口

```text
c_window/
  strategy.py       # select_paths(window, documents) -> list[str]
                    # execute_plan(request, plan, runtime) -> SearchResult
                    # search(request, runtime) -> SearchResult
  test_window.py
  test_strategy.py
  README.md
  RESULTS.md
```

- `select_paths` 只依赖窗口与日期元数据，纯函数。D 可直接复用。
- `execute_plan` 接受已解析 plan，不再解析；便于 D 对硬窗口复用同一行为。
- `search` 调 B.normalize，然后 execute_plan。独立测试时注入 normalizer 替身或直接测 execute_plan；不要复制 B 解析代码。

## 2. 路由规则

```text
plan.status != ok      → 原查询、全范围，与 B fallback 一致
plan.mode == window    → 筛出窗口内路径，再执行 B 的 topical_query
其他 mode              → B 行为，不筛选、不加权、不拆阶段
```

按 `start <= published_at <= end` 筛选完整冻结 metadata。只有 `window` 是硬约束；不能把 current 的 prefer_recent 也当硬筛选。

当允许集合为空：合法空结果，记录 eligible_count=0，任务得分为 0；不得自动放宽日期或回到全库。窗口内不足十篇时返回多少算多少，不用窗口外文章凑数。

## 3. 与 zg 对接：最容易出错的地方

A 的 runtime.retrieve 接受 `allowed_paths`，C 只计算和传递集合。A 实现 transport 时优先采用以下模式：

```text
-g deep-news/articles/*.md
-g !<每个不在 allowed_paths 中的文章路径>
-g !eval/**
```

先纳入全部文章，再按稳定路径顺序追加补集的排除规则。不能在 broad include 后再追加 allowed 的正向规则，误以为它们会取交集。

本地源码 [matchesOrderedGlobs](../../../upstream/zvec-grep/src/engine/utils/file-selection.ts) 表明规则按顺序覆盖；[resolveFilteredFileIds](../../../upstream/zvec-grep/src/engine/pipeline/search/index.ts) 会把文件范围传给 storage filter。日期在召回前生效，而不是调用完后才过滤 Top100。

其他约束：

- 使用 frontmatter 日期。禁用 `--modified-after/before` 代替发布日期。
- 路径必须属于 metadata；不能由 query 直接拼接 glob。
- 当前文章 slug 适合逐路径排除。若路径含 glob 元字符 `* ? [ ] { }` 等，v1 先明确拒绝该输入并报错，不能静默错误匹配；若实现转义，必须与 zg 真实匹配语义测试一致。
- 命令参数使用数组，空格路径也是一个参数；不 shell=True。
- 431 篇规模按补集传参可先做命令长度检查。超过平台参数上限时明确失败；不改为多批次免费召回，也不重建临时索引来绕过。
- 返回结果逐条断言属于 allowed_paths 且日期在窗口内。若越界，这是 transport 错误而非低质量结果，整轮无效。
- 不得把日期过滤放在 raw_hits 之后作为唯一实现；结果校验不能替代召回前过滤。

## 4. 可观测字段

每题记录：topical_query、解析窗口、eligible_count、allowed_paths 的内容与指纹、excluded_count、调用参数、实际返回文档数、空范围原因。

允许集合只能由 query 解析出的日期和 metadata 构造。测试应证明修改 gold.relevant 不改变这个集合。

## 5. 必测

- 精确包含窗口两端；月底、闰日正确；日期倒置或缺失拒绝。
- mtime 更新或文件名日期变化不影响筛选；真正 frontmatter 日期变化触发快照校验。
- 空集合不执行全库调用；只有 3 篇合格文档时不补窗口外结果。
- none/prefer_recent/stages 与 B 使用同样参数、一次调用、同样顺序。
- 假 transport 返回窗口外文章时报错；不是简单丢掉继续出分。
- 基于未见过的文档 metadata 构造筛选，不根据 qid 选路径。
- 与 A 联合验证真实 zg glob：挑选一个小日期范围，原始输出所有路径都属于预先算出的集合。该验证属于运行校验，不改金标。

## 6. 实验与验收

跑完整 30×3 与 B 比较。主要观察 latest/historical 的 WindowPrimary、Window nDCG 与 Task；同样报告内容指标，防止“日期都对但找错文章”。

非硬窗口题的算法输出应与 B 在同一 fake/raw 响应下严格一致。真实检索有漂移时单列，不允许用新增变化解释为 C 的收益。

所有硬窗口输出日期合规是实现验收；WindowPrimary 不要求达到 100%，因为仍可能找不到相关文档。诚实保留退步和空结果。

特别核查 latest-selfhost 与 historical-mcp，但不为这两题增加特殊规则。不得使用题集中的 `time` 字段作为解析捷径。

## 可直接交给 agent 的任务

> 阅读本文件与统一契约，实施方案 C，只写 c_window 目录。使用 B 的 QueryPlan 和 A 的 allowed_paths transport，在召回前按元数据发布日期筛选显式窗口；其他查询严格保持 B 行为。先完成注入式单测，再联合验证真实 glob 范围并跑全量 C vs B。不要改模型、金标、其他 agent 文件或增加无预算的检索。
