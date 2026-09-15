# A：冻结基线与统一实验入口

## 任务

复现现有原始查询检索，建立 B/C/D 共用的运行和比较框架。开始前阅读 [统一契约](README.md)，沿用全部字段、预算和所有权规则。

你负责公共实验框架与 `a_baseline/`；其他 agent 正在开发策略目录，不得改动或回滚其文件。

## 1. 文件与接口

在 `eval/deep-news/experiments/` 中创建：

```text
__init__.py
.gitignore
run.py                  # CLI，按 variant 延迟加载策略
compare.py              # 验证可比条件并输出逐题差值
common/
  runtime.py            # 冻结元数据、transport、预算、日志
  evaluation.py         # 调用现有纯计分函数、归档与汇总
  test_runtime.py
  test_evaluation.py
a_baseline/
  strategy.py           # search(request, runtime)
  test_strategy.py
  README.md
  RESULTS.md
```

只在 variant 被请求时加载对应策略，B/C/D 文件尚不存在时 A 仍能运行；请求不存在的 variant 则给出明确错误。

CLI 同时支持 `--routes`、`--ids` 和 `--strategy-config`。配置通过 runtime.strategy_config 传给策略，归档原文与指纹；D 默认读自己的 config.json。子集结果保存实际 qid 集，不写成全量报告。配置字段由对应策略校验，未知字段报错。

Python 模块加载采用一个确定的 package 或 importlib 方案，写进公共 README，避免多个同名 run.py 相互覆盖。不得通过修改旧模块全局变量切换输出路径。

## 2. A 的精确行为

1. strategy 收到经过字段白名单隔离的 request。
2. 调一次 runtime.retrieve，使用 original query、request.route、100、allowed_paths=None。
3. 按首次片段命中合并相同路径，保持文章顺序，不按时间排序。
4. 返回全部唯一候选、连续 rank、来源记录。plan 表示原样传递，不推断时间。
5. 评分端再把完整 gold query 交给既有 metrics_for。

这里的“基线复现”包括重复片段占原始候选预算的行为，不能顺手扩大 limit 或改成 100 篇文章。

## 3. 公共 transport 的实现

无约束调用保持现有命令参数：

```text
zg query [--fts|--vector] <query>
  --limit 100 --preview none --refresh off
  -g deep-news/articles/*.md -g !eval/**
```

不要加入 --trace 或改输出模式后声称逐项复现。记录单调时钟耗时、完整 stdout/stderr、命令数组、返回码和 raw_hits。

同时实现 C/D 需要的 allowed_paths 参数。只能选 metadata 中存在的文章；空集合短路；建议保留文章正 glob，再依次排除所有不允许路径。详见 [C 的 glob 约束](C-WINDOW.md)。缺失、越界或预算超额均作为错误，不静默降级到全库。

每次调用计入 budget，空范围短路记录 limit_requested=0。策略看不到 subprocess 以外的任意召回接口，所有真实检索经这个入口计账。

## 4. 先离线回放，后真实运行

### 离线回放

用现有历史 JSON 中每题每路线的 raw_hits 作为 fake transport 返回值，运行聚合和原指标。

验收：30×3 的最终文章顺序、每条指标、summary、by_kind 与历史结果一致，浮点比较绝对误差 ≤1e-12。不要要求新增元数据与时间字段一致。

### 真实运行

运行全部三路线。相同条件下如与历史结果不同，列出变化的 qid、路径和 rank；不把实时检索的不同结果硬编码成历史顺序，也不将重复运行挑最好的一次。

如果索引/语料指纹改变，则生成不可比较的诊断，不覆盖旧报告。

## 5. compare.py

输入显式 run 文件列表，不自动猜 latest；先校验统一契约的可比条件。

输出：

- 总体和 kind 分组的内容指标、Task、WindowPrimary、AllStages、CandidateTask、metric_n。
- 每种对照的逐题 win/tie/loss 与绝对差值。
- 从成功变失败的查询，展示前五路径/日期变化。
- 实际调用次数、总 requested_limit、候选数、耗时 median/p95；标明单轮顺序运行，性能值仅诊断。
- 解析 fallback/error 比例；不丢弃 fallback 题。

错误 run 不做有效排名。不同版本候选列表可不同，但查询、预算及评分定义必须相同。

## 6. 必测

- request 不携带 id/kind/time/relevant/stages；只传白名单。
- 改动金标不影响 fake transport 收到的 query/filters，仅影响评分。
- 两个片段同文件去重，全文档序列保留；Top10 后仍能正确计算 CandidateTask。
- timeout、非零退出、坏输出、越界路径让整轮无效，分母仍 30。
- allowed_paths=[] 不执行 zg；不存在路径拒绝；连续调用 34+33+33 合法，34+34+33 拒绝。
- 并行策略的产物目录不会覆盖；动态源码哈希覆盖实际加载的 B/C/D 文件。
- compare 拒绝不同题集、as_of、索引条件、预算或失败 run。
- 历史原始结果回放逐项一致。

## 7. 完成标准

A 可独立运行，历史回放通过，全量基线结果归档；公共接口足够 B/C/D 注入替身开发，文档列清入口。没有修改旧 runner、金标或语料。

RESULTS 中区分“离线复现一致”和“真实运行分数”，不要混为一次实验。

## 可直接交给 agent 的任务

> 请阅读本文件与同目录 README.md，实施方案 A。你只负责 experiments 公共框架及 a_baseline 目录；其他 agent 会写 B/C/D，不得修改或回滚他们的文件。先实现并测试公共接口及历史回放，再执行全量基线，保存独立产物和 RESULTS。不要改旧评测、题集、知识库正文或模型，不要启动其他 agent。
