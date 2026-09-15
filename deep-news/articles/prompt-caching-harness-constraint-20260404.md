---
title: "Prompt Caching 作为 Harness 工程的一等约束"
date: 2026-04-04
source: https://yage.ai/share/prompt-caching-harness-constraint-20260404.html
slug: prompt-caching-harness-constraint-20260404
lang: zh
---
# Prompt Caching 作为 Harness 工程的一等约束

发布于 2026 年 4 月 4 日 · [查看原网页](https://yage.ai/share/prompt-caching-harness-constraint-20260404.html)

## 一个反直觉的 PR

2026 年初，Anthropic 取消了 Pro 订阅用户对第三方 harness
的登录支持，所有第三方工具必须走 API 付费。在这个背景下，Claude Code
的核心作者之一给 OpenClaw 提交了一个看起来违背常理的 [PR（OpenClaw
#58036）](https://github.com/openclaw/openclaw/pull/58036)：在对话历史需要压缩（compaction）时，优先删除最新的 tool
results，而非最旧的。

按朴素的直觉，最新的上下文应该最有价值。用户刚刚读取的文件内容、刚刚执行的命令输出，对下一步决策的相关性最高。为什么要优先丢弃它们？

这类 PR 的价值在于它提供了一个观察窗口，让我们看见成熟 harness
在实践中形成的价值排序。当 prefix stability 和 context recency
冲突时，这个 PR
选择了前者。理解这个选择背后的原因，需要先回答两个更根本的问题。

## 为什么 Prompt Caching 是可行性条件

Agent 场景下的 token 经济有一个容易被忽略的特征：input 远大于
output。[Manus
团队在他们的 context engineering 博文](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)中给出过一个数据，他们的平均
input/output token 比约为
100:1。几乎所有计算成本都花在反复处理长上下文上，生成回复本身的开销相比之下微不足道。Manus
是较早在公开场景下系统性阐述 agent 缓存策略的团队，他们提出的 keep
prefix stable、make context append-only、mask tools don’t remove them
三原则，与本文从多个来源中观察到的模式高度吻合。

在 100:1 的 input/output
比例下，缓存是否命中直接决定了系统的成本基线。[Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
的 cache hit 与 miss 之间有 10
倍的成本差距（缓存读取价格为基准输入价格的 10%）。[OpenAI](https://platform.openai.com/docs/guides/prompt-caching)
的 GPT-5 系列达到 90% 的折扣。[DeepSeek](https://api-docs.deepseek.com/news/news0802)
的缓存命中价格同样是 miss 价格的十分之一。这些数字的含义很直接：如果一个
harness 长期 cache miss rate 在 50% 以上，其实际成本是同等规模下
cache-aware 系统的三到五倍。对于正在 scale
的产品，这个差距足以决定商业模式是否成立。

成本只是一半。更具决定性的因素是延迟。DeepSeek 报告过一个数据：128K
token 的 prompt 在高缓存命中场景下，首 token 延迟从 13 秒降到 500
毫秒。这个差距意味着什么？13 秒的首 token 延迟会让
speculation（推测执行）、background agents、sub-agent
并行这些交互模式失去可行性，因为没有用户愿意等一个 sub-agent 冷启动 13
秒再返回结果。500 毫秒的延迟则让这些模式变得可用。换句话说，prompt
caching 的 hit rate
决定的是哪些系统架构能够存在，而非已有架构运行得多快。

所以第一个核心判断：**Prompt caching 在成熟 harness 中是
viability constraint。**
它同时决定了系统的成本基线和交互延迟，这两者共同划定了 sub-agent
架构、speculation 模式、background agent
等设计方案的可行边界。一旦系统开始
scale，这些因素会压过局部功能直觉，反过来塑造设计决策。

## 为什么 Cache Discipline 会反向塑造 Harness Design

一旦 cache reuse 成为可行性条件，一个连锁效应随之启动：发送到 API 的
messages 数组、tool definitions、system prompt
不再是可以随意改动的数据，它们成为前部尽量稳定、尾部允许增长的半不可变序列。

这个约束来自 [prompt
caching 的核心机制](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)：缓存匹配基于严格的前缀比对，精确到 token
级别。哪怕只改了一个空格，从改动位置往后的所有内容都无法命中。这个机制跨供应商一致：[OpenAI](https://platform.openai.com/docs/guides/prompt-caching)
以 128 token 为粒度做自动前缀匹配，[DeepSeek](https://api-docs.deepseek.com/news/news0802)
默认开启全自动缓存，[Google Gemini](https://ai.google.dev/gemini-api/docs/caching)
需要显式创建 `CachedContent`
对象。实现细节各异，底层约束相同：前缀的任何变动都会导致缓存失效。这个约束源自
KV-cache 的工作原理，只要 Transformer 架构不变，它就会持续存在。

这意味着 prefix stability 会渗透到 harness
多个子系统的设计中。它连锁影响了 compaction
的顺序（从尾部删而非从头部删）、tool definitions
的排列（必须确定性排序，动态加载的抖动会导致 cache
break）、图片和大型内容的裁剪时机（延迟裁剪优于激进裁剪）、sub-agent
的参数传递方式（必须共享与父进程一致的 cache
key）。这些子系统看起来互不相关，却因为共享同一个底层约束而产生了耦合。

所以第二个核心判断：**Cache discipline 会反向塑造 harness
design。** 那些看起来反直觉的实现，是全局 cache economics
覆盖局部功能直觉后的自然结果。

## Cache Discipline 改写了哪些设计决策

回到开头的那个 PR。以下几个案例来自 OpenClaw 的公开 PR
记录。它们是对已有系统的修补，揭示的是开发过程中逐步形成的 cache
discipline，而非一开始就设计好的蓝图。这正是它们的价值所在：它们让我们看见成熟
harness 的价值排序是如何在实践中被迫形成的。

**Compaction 顺序。** [#58036](https://github.com/openclaw/openclaw/pull/58036) 将
compaction 策略从删最旧的改为从尾部开始删。对话的早期内容（system
prompt、初始工具定义、前几轮对话）构成了缓存前缀的核心，删除它们等于摧毁缓存基础。尾部的
tool results 虽然信息密度高，但位于 cache
计算的末端，删除后对前缀命中率的影响最小。更关键的一点：被删除的 tool
result 在后续需要时可以重新获取（比如重新读一次文件），被破坏的 cache
prefix 只能以全价重建。这个不对称性是整条逻辑的支点。

**工具列表的确定性排序。** 工具定义通常作为 system
message 的一部分发送，位于 messages
数组的最前端。如果每次请求时工具列表的顺序发生变化（比如因为动态加载的
MCP server 响应时序不同），整个缓存都会失效。[#58037](https://github.com/openclaw/openclaw/pull/58037)
修复的正是这类问题：确保 tool definitions
在多次请求之间保持相同的序列化顺序。[Manus
团队](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus)提出了一个更激进的策略：即使某些工具在当前状态下不可用，也保留它们在工具列表中的位置，通过
logit masking
而非列表增删来控制工具的可用性，专门为了避免工具列表变动导致的 cache
break。

**图片和大型内容的裁剪时机。** 图片 token 在 messages
中占据大量空间。如果在对话中途移除一张早期图片来腾出 context
window，效果和从头部删除内容一样：前缀被破坏。[#58038](https://github.com/openclaw/openclaw/pull/58038)
选择延迟 history image
pruning，尽量把对早期前缀的改写往后推。更好的策略是在图片首次出现时就决定是否保留，或者只裁剪位于消息尾部的图片。Manus
的做法更彻底：把大型内容（PDF、网页等）写入文件系统，context
中只保留文件路径作为指针，从源头上避免大型内容膨胀 context
后又需要裁剪的问题。

**Cache control 断点的放置。**
缓存断点的位置划定了稳定区和活跃区的边界。成熟的 harness 会在 system
prompt 末尾和最近一条用户消息上设置 `cache_control`
标记。system prompt 部分被稳定缓存，用户消息之后的 assistant response 和
tool results 属于活跃区域，允许自然增长和变化。对于使用 [OpenAI
API](https://platform.openai.com/docs/guides/prompt-caching) 的
harness，虽然缓存是自动的、无需显式断点，同样的分区思维仍然适用：把稳定内容放前面、变化内容放后面。

这些子系统之间的耦合，是对底层 API 特性的忠实映射。忽视这个约束的
harness 会在不知不觉中付出数倍的成本。

## Sub-agent 边界：缓存约束的传播盲区

当 harness 引入 sub-agent 架构（主 agent 派发任务给子 agent
执行），prompt caching 的约束会以一种不易察觉的方式传播。

每个 sub-agent 启动时都会建立自己的 API 会话，拥有独立的缓存前缀。主
agent 精心维护的缓存对 sub-agent 完全无效，sub-agent
从零开始构建自己的缓存。如果 sub-agent
的任务很短（比如只做一次工具调用就返回结果），它的缓存根本来不及被复用就过期了。这是一个隐性的成本放大器：每一个短生命周期的
sub-agent 都意味着一次缓存冷启动。

一个具体的例子是 `reasoning_effort` 参数。某些 harness
在派发简单子任务时会将推理力度设为 low，期望减少 output token
从而降低成本。但在实践中，`reasoning_effort` 的变化可能改变
API
请求的参数签名，导致与正常请求的缓存无法共享。看似在节省成本，实际上因为
cache miss 反而付出了更多。

更微妙的问题在于 sub-agent 的 system prompt 设计。如果主 agent 和
sub-agent 共享一部分 system
prompt（比如通用的安全规则和行为准则），这部分内容应该放在 sub-agent
messages 的最前面，并且保持与主 agent
完全一致。任何差异，哪怕是为了简化而删除了几行，都意味着这个 sub-agent
无法复用主 agent 的缓存，也无法与其他 sub-agent 共享缓存。

设计 sub-agent
策略时，需要权衡任务拆分的粒度和缓存复用的可能性。过于细碎的子任务拆分可能让每个
sub-agent 都在为首次缓存付全价。但这个权衡的前提是有数据支撑：sub-agent
的实际 cache hit rate
是多少？冷启动的成本占总成本的比例是多少？缺少这些度量，任何 sub-agent
策略的调整都是盲飞。

## 先度量，再优化

第三个核心判断：**无法度量的东西无法改进。**

Prompt caching
的棘手之处在于它的影响难以直接观察。缓存未命中不会触发报错，多付的成本静默地累积在账单里。API
返回的 response 中包含 `cache_creation_input_tokens` 和
`cache_read_input_tokens` 字段（[Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
如此，[DeepSeek](https://api-docs.deepseek.com/news/news0802)
类似地返回 `prompt_cache_hit_tokens` 和
`prompt_cache_miss_tokens`），但如果 harness
没有主动收集和展示这些指标，开发者对自己的缓存表现是没有感知的。

Claude Code 泄露源码中的 `promptCacheBreakDetection.ts`
展示了一个值得学习的思路。这个模块系统性地追踪缓存断裂的来源：是 system
prompt
变了？是工具列表的顺序变了？还是某条历史消息被修改或删除了？它把每一类
cache break
都归因到具体的变更类型上，形成可观测的指标。这个文件值得作为学习材料仔细阅读，它展示了一个工程团队如何将模糊的成本问题转化为可归因的工程问题。

对于构建自己 harness
的开发者，可观测性至少需要覆盖三个维度。首先是每次 API 调用的 cache hit
/ miss / creation tokens 的记录和聚合，这是最基础的指标。其次是按 cache
break 来源分类的计数器：system prompt 变更、tool list
变更、历史消息修改、compaction 触发等。最后是分别追踪主 agent 和
sub-agent 的缓存表现，因为两者的模式通常差异显著。

有了这些数据，优化才有方向。否则你可能花大力气优化了一个只贡献 5%
cache miss 的来源，而忽略了贡献 80% 的那个。这个方法论的适用范围也超出了
prompt caching 本身：token 用量、延迟分布、tool call 成功率，所有
harness 的关键指标都遵循同样的逻辑。先建立度量基线，再做针对性优化。

## 结语

回到 [#58036](https://github.com/openclaw/openclaw/pull/58036) 那个
PR。它的 diff
很小，改动的代码行数可能不超过几十行。但它代表了一种认知转变：prompt
caching 从一个后置的优化措施，成为了塑造系统行为的一等约束。

本文的三个核心观察：**prompt caching 是可行性条件，cache
discipline 会反向塑造 harness design，无法度量的东西无法改进。**
三者之间有递进关系：第一个判断解释了为什么 prompt caching
值得被认真对待，第二个判断解释了认真对待之后系统会发生什么变化，第三个判断解释了如何正确地推进这种变化。

这些观察跨供应商成立。无论使用 [Anthropic](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)、[OpenAI](https://platform.openai.com/docs/guides/prompt-caching)、[DeepSeek](https://api-docs.deepseek.com/news/news0802) 还是 [Gemini](https://ai.google.dev/gemini-api/docs/caching)，底层约束一致：前缀变动导致缓存失效，cache
hit 和 miss 之间存在数倍到十倍的成本差距。它们共同指向的结论是，prompt
caching 应该被纳入 harness
的架构设计阶段，而非作为上线后的成本优化手段去补救。

对于正在构建自己 harness 的工程师，Claude Code 源码中的
`promptCacheBreakDetection.ts`
是一个值得仔细阅读的起点。从那里开始，建立自己的度量体系，然后让数据告诉你该优化什么。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
