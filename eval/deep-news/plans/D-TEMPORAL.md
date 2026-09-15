# D：软时间偏好加权与演进阶段覆盖

## 任务与边界

在 C 的硬窗口能力上，为 prefer_recent 和 stages 两种意图增加独立策略。阅读 [统一契约](README.md)。你只写 `experiments/d_temporal/`；A/B/C 的模块只读，禁止复制或改写其公共实现。

D 包含两项机制，必须可分别关闭，不能把它们的收益混成一个无法解释的总分。

## 1. 文件与入口

```text
d_temporal/
  strategy.py          # search(request, runtime)
  recency.py           # rerank_recency(documents, as_of, config)
  stages.py            # allocate_budget / merge_stages
  config.json          # 固定配置，进入每轮快照
  test_recency.py
  test_stages.py
  test_strategy.py
  README.md
  RESULTS.md
```

普通字典接口，不需要依赖新框架库。B 提供 normalize；C 提供 select_paths / execute_plan；A 提供统一 runtime。

## 2. 路由

| QueryPlan | D 行为 |
|---|---|
| status 非 ok | 与 B 一致：原查询一次检索，记录 fallback |
| none | 与 B 完全一致 |
| window | 调 C.execute_plan，保持 C 行为 |
| prefer_recent | B 的单次主题召回后，给全部去重候选时间加分 |
| stages | 按解析出的阶段分别限制日期并检索，再做覆盖选择 |

关闭 soft 时 prefer_recent 回到 B。关闭 stages 时 stages 回到 B 的单次主题检索。硬窗口始终交 C，不能在 D 中再次编写不同的日期逻辑。

## 3. D-soft：先采用可解释的固定排序假设

旧输出没有统一可用的文档相关性分，而且不同路线原始分数尺度不同。v1 不增加 --trace 或新模型 reranker；使用**原文档 rank 作为排序先验**：

```text
r = 原文章 rank，从 1 开始
R = 1 / (60 + r)
age_days = as_of - published_at
F = 2 ** (-age_days / 30)
S = R * (1 + 0.25 * F)
```

默认 config：`enabled=true, rank_constant=60, half_life_days=30, weight=0.25`。

完整配置形状为 `{"soft": {"enabled": true, "rank_constant": 60, "half_life_days": 30, "weight": 0.25}, "stages": {"enabled": true}}`，从 runtime.strategy_config 读取。拒绝未知字段；无外部配置时由 A 加载本目录 config.json。

这些是预先固定的实验参数，不是调优结论。R 不是校准过的语义相关概率，时间加分仍可能把不相关的新文抬高；必须如实观察指标，不能声称保证相关性优先。

实施要求：

1. 只对 prefer_recent 生效；原候选集合不增不减。
2. published_at 来自 runtime metadata，as_of 来自 request；不使用墙上时钟，不使用 gold.time。
3. 对全部去重候选计算 S，再取前十。不能只重排原 Top10。
4. S 降序，平分按原 rank、路径稳定排序；每篇保存 original_rank、R、age_days、F、S、新 rank。
5. weight=0 时直接保留原顺序；half_life<=0、负权重、非法日期配置直接失败。
6. 当前冻结语料不允许未来日期，检测到应报数据错误，不用截 age=0 掩盖。
7. 软偏好窗口不是硬截断。7/15 之前的文档仍可返回；不能把它们标注为失效。

参数搜索不是首轮任务。只跑固定默认与 weight=0 控制；后续若调参，另设独立主题测试集并记录全部尝试。

## 4. D-stages：有预算的分阶段检索

### 4.1 来源

阶段必须来自 B 对用户文本的解析。每个阶段包含共享主题、该阶段子问题、日期窗口。禁止读取 gold.stages 的文章路径、阶段名或数量来构造检索。

例如 MCP 三阶段，从用户文字得到：

```text
stage-1：MCP 确定性编排；六月
stage-2：MCP 工具中途问人；七月
stage-3：MCP 云端 agent 身份；八月
```

### 4.2 总预算固定

m 个有效阶段，总预算 100：

```python
base, extra = divmod(100, m)
budgets = [base + (i < extra) for i in range(m)]
```

三阶段为 34/33/33，二阶段为 50/50。v1 阶段调用顺序执行。

- 不先做一次全局 100，再做每阶段 100。
- 某阶段允许集合为空，记录零调用，不把它未用的预算转给其他阶段。
- 某阶段只返回少量候选也不追加查询、不重分配预算。
- 不给失败阶段自动第二次检索。命令错误使本题失败；空候选是合法检索结果。
- v1 支持 2–5 阶段。超出或缺少可确定的时间窗口，按 B 单次查询 fallback，记录原因，不悄悄截掉后面的阶段。

分次检索会改变 zg 的内部召回特征；固定总 limit 是资源控制，不表示与单次 100 具有相同内部计算量。因此实际调用数、耗时也必须报告。

### 4.3 每阶段召回

复用 C.select_paths，根据每阶段日期计算 allowed_paths。用该阶段主题、当前 route、分配预算调用 runtime.retrieve；范围异常由 C/A 同样拒绝。

每篇候选记录来自哪些 stage/call、各自 call_rank/raw_rank。阶段的时间区间允许重叠，文档可能在多次召回中出现，最终只展示一次。

### 4.4 合并与选择

先采用确定性的轮转合并，不跨阶段比较原始分数：

1. 各阶段保留自身原始文档顺序。
2. 按用户提及的阶段顺序轮转，每次从一个阶段取下一篇尚未输出的文章。
3. 遇到重复路径，保留已有位置并补 provenance，继续在该阶段找下一篇。
4. 某阶段耗尽则跳过，直到全部候选消费完；最终 rank 连续，前十用于展示。
5. 不删掉第十名之后候选，评分端仍要计算 CandidateTask。

这会为不同阶段提供展示机会，但“有候选”不等于“该阶段已正确回答”。diagnostics 只能记录 `has_candidates/empty`、路径和来源；是否满足阶段金标由评分端决定。不得把任意窗口内 Top1 自动描述为可靠证据。

不额外对阶段内结果进行新鲜度加权；否则无法区分分阶段召回、覆盖选择和日期偏好的作用。

## 5. 对照运行

A 的 runner 应支持 `--strategy-config <path>`，只接受对应 D 配置，不改 request/gold。首轮至少保存三组：

- `d`：soft=true、stages=true。
- `d_no_soft`：soft=false、stages=true。
- `d_no_stages`：soft=true、stages=false。

以上是报告标签；三个控制均调用公共 runner 的 `--variant d`，由 `--strategy-config` 指定各自配置文件，而不是要求 A 注册三个不同插件。

为节约验证成本，关闭机制的控制可回放同一批原始响应；必须标记 replay，不能声称是额外真实检索。对 stage=false 需要 B 的单次召回数据，不能拿分阶段响应假装是 B。

正式 d 完整跑 30×3；控制如只跑受影响的六题，必须标明 subset，只与同一 qid 子集比较。A/B/C/D 总表只放全量且预算一致的 run。

分组解读：

- current：D vs B/C 观察 WindowPrimary、内容 nDCG 和退步；Task 本来不含软日期，不能仅凭 Task 不变就说新鲜度没改善。
- evolution：D vs B/C 观察 AllStages、StageCoverage、CandidateTask、调用数与耗时。
- foundation：与 B 同响应下逐项一致。
- latest/historical：与 C 同响应下逐项一致。

## 6. 必测与验收

D-soft：weight=0 顺序不变；30 天 F=0.5；同日期保持原序；参考日固定可重放；候选集合完全相同；第十名后候选可前移；其他 mode 不调用 recency。

D-stages：34/33/33、50/50 分配；总预算不超；空阶段无全库 fallback；重复文档去重且保留多来源；轮转覆盖；所有阶段耗尽终止；超过五阶段回退一次；不读取 gold；中途命令失败不出有效平均。

综合：D-window 与 C、D-none 与 B 在相同响应下完全一致。结果不要求一定优于旧版；若更差，说明是否来自阶段解析、阶段候选不足、轮转选择不相关或时间加分过强。

## 交付与可直接使用的任务

RESULTS 记录默认参数、控制结果、所有退步以及两类机制各自作用。不要以“最新文章出现了”替代相关性验收。

> 阅读本文件与统一契约，实施方案 D，只写 d_temporal 目录。复用 B 的解析和 C 的硬窗口筛选，分别实现可关闭的软时间加权与分阶段预算检索。总预算仍为每题每路线 100，策略不读取金标。先做注入式测试，再完成全量 D 与机制关闭对照，保存独立结果并说明局限。不要改其他 agent 的文件，不调题集凑分。
