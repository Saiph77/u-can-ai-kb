---
title: "Long Context 横评：三家都到了 1M，然后呢？"
date: 2026-03-15
source: https://yage.ai/share/long-context-benchmark-20260315.html
slug: long-context-benchmark-20260315
lang: zh
---
# Long Context 横评：三家都到了 1M，然后呢？

发布于 2026 年 3 月 15 日 · [查看原网页](https://yage.ai/share/long-context-benchmark-20260315.html)

**调研日期**: 2026-03-15

> 1M context 已经不稀奇，稀缺的是在 1M 里还能稳定找到对的信息。 Claude
> Opus 4.6 目前是唯一在 1M 上保持高可靠性的模型，Gemini 和 GPT
> 的衰减更明显。 长上下文竞争已经从容量竞赛转向可用性竞赛。

2026 年 3 月，三大前沿模型厂商终于都站到了 1M context window
的门槛上。Google 是最早的，Gemini 1.5 Pro 从 2024 年 2 月起就支持
1M。Anthropic 保守了整整两年，直到 2026 年 2 月才在 Claude Opus 4.6
上开放 1M beta，3 月 13 日刚转为正式版。OpenAI 这边更曲折：GPT-4.1 作为
API-only 模型短暂进入过 1M，但后续的 GPT-5.2 又收缩回 256K，直到
GPT-5.4（2026 年 3 月）才以 premium 模式重新支持 1M，算是第一次在面向
ChatGPT 用户的 production model 上进入 1M 俱乐部。

context window 的军备竞赛至此告一段落。但我们把各家的 long context
benchmark 数据拉出来一比，发现了一个值得写下来的事实：同样标称
1M，各家的实际可靠性差异极大。在 MRCR v2 8-needle（目前最严格的 long
context 检索测试）上，Claude Opus 4.6 在 1M 处得分 76%，GPT-5.4 在
512K-1M 区间是 36.6%，Gemini 3 Pro 在 1M 处只有 24.5%。

![MRCR v2 Performance Curve](imgs/mrcr_v2_performance_curve.png)

MRCR v2 Performance Curve

这张图可能是最直观的解释。GPT-5.2 之前在 needle-in-haystack
测试里的成绩看起来近乎完美（4K-8K 范围
98.2%），我一度以为它在这方面是无敌的。后来仔细看了一下才意识到，它的
context window 只有 256K，曲线在那里就截止了。GPT-5.4 扩展到 1M
之后，256K 以外的衰减才暴露出来。红色阴影区就是 GPT-5.2
从未被测试过的领域。

这篇调研整理了 MRCR v2、Graphwalks、LongBench 等多个 benchmark
的横评数据，试图回答一个问题：1M context window
从”有”到”能用”，各家走到了哪一步。

## 数据与方法

### 主要 Benchmark：MRCR v2（Multi-Round Coreference Resolution）

MRCR v2 是目前 long context 横评的核心 benchmark，由 OpenAI
开发并开源（[GitHub](https://github.com/openai/openai-mrcr)）。测试方法是在大量干扰文本（haystack）中插入多个相同格式的”needle”用户请求和回复，要求模型准确检索第
n 个 needle 的内容。

8-needle 变体是最难的配置：模型需要同时追踪和区分 8
个不同的目标信息。相比 2-needle 或
4-needle，这对模型的多注意力跨度和精确检索能力要求高得多。所有前沿模型厂商（OpenAI、Anthropic、Google）都采用
8-needle 作为 long context 能力的核心评估标准。

### 数据来源

本报告的数据来自三类来源，按可信度排序：

- **厂商官方 benchmark**：OpenAI 官方博客（[GPT-5.2](https://openai.com/index/introducing-gpt-5-2/)、[GPT-5.4](https://openai.com/index/introducing-gpt-5-4/)）、Anthropic
  系统卡（[Sonnet 4.6
  System Card](https://anthropic.com/claude-sonnet-4-6-system-card)）、Google Gemini 技术报告（[arxiv 2507.06261](https://arxiv.org/html/2507.06261v1)）
- **独立第三方评测**：[contextarena.ai](https://contextarena.ai/)（统一环境下测试各模型）、[Artificial Analysis](https://artificialanalysis.ai/)
- **综合分析文章**：[The
  March 2026 Frontier](https://medium.com/@Micheal-Lanham/the-march-2026-frontier-gpt-5-4-vs-gemini-3-1-vs-claude-4-6-daebf22e672e)、[Awesome
  Agents Long Context Leaderboard](https://awesomeagents.ai/leaderboards/long-context-benchmarks-leaderboard/)

需要特别注意的是：不同来源的 MRCR v2
分数**不可直接对比**。OpenAI 官方数据使用 xhigh reasoning
effort，Anthropic 使用 max thinking，而 contextarena.ai
有自己的标准化设置。本报告在对比时会注明数据来源和评测条件。

## 拆解”无敌”假象：GPT-5.2 的 256K 边界

开头那张图值得再仔细看一遍。两条曲线在 0-256K 范围内几乎重合，说明
GPT-5.2 和 GPT-5.4
在这个区间的能力没有本质差异。真正的信息在红色阴影区：GPT-5.4 进入 256K
以上后，256K-512K 从 79.3% 骤降到 57.5%，512K-1M 进一步跌至
36.6%。这不是 GPT-5.4 的退步，而是 GPT-5.2 从未面对过的挑战。

### GPT-5.2 与 GPT-5.4 逐区间对比

| Context 区间 | GPT-5.2 | GPT-5.4 | 差异 |
| --- | --- | --- | --- |
| 4K-8K | 98.2% | 97.3% | -0.9 |
| 8K-16K | 89.3% | 91.4% | +2.1 |
| 16K-32K | 95.3% | 97.2% | +1.9 |
| 32K-64K | 92.0% | 90.5% | -1.5 |
| 64K-128K | 85.6% | 86.0% | +0.4 |
| 128K-256K | 77.0% | 79.3% | +2.3 |
| 256K-512K | N/A | 57.5% | — |
| 512K-1M | N/A | 36.6% | — |

来源：[OpenAI
GPT-5.2 Blog](https://openai.com/index/introducing-gpt-5-2/)、[OpenAI GPT-5.4
Blog](https://openai.com/index/introducing-gpt-5-4/)

在重叠区间（4K-256K），两个模型的性能差异极小（±2%），说明这不是代际能力退步，而是
GPT-5.2 根本没有被测试过 256K 以上的场景。GPT-5.4 在 256K 以内几乎与
GPT-5.2 持平，但延展到 1M 后揭示了所有模型都面临的长 context
衰减问题。

## 跨模型横评：谁在 1M 真正能用？

![Cross-model Comparison](imgs/mrcr_v2_cross_model.png)

Cross-model Comparison

上图来自 Anthropic Sonnet 4.6 系统卡中的 Table 2.16.A 数据（Claude
模型使用内部评测 + max thinking，Gemini 和 GPT 数据来自 contextarena.ai
第三方评测），以及 OpenAI GPT-5.4 官方数据和 Google Gemini 2.5
技术报告。

### 256K 聚合分数

| 模型 | 分数 | 来源 |
| --- | --- | --- |
| Claude Opus 4.6 | 93.0% | Anthropic 系统卡（max thinking） |
| Claude Sonnet 4.6 | 90.3% | Anthropic 系统卡（max thinking） |
| GPT-5.2 | 70.0% | OpenAI 自报（xhigh reasoning） |
| Gemini 3 Flash | 58.5% | contextarena.ai |
| Gemini 3 Pro | 45.4% | contextarena.ai |
| Claude Sonnet 4.5 | 10.8% | Anthropic 系统卡 |

### 1M 聚合分数

| 模型 | 分数 | 来源 |
| --- | --- | --- |
| Claude Opus 4.6 | 76.0% | Anthropic 系统卡（max thinking） |
| Claude Sonnet 4.6 | 65.8% | Anthropic 系统卡（max thinking） |
| GPT-5.4 | 36.6% | OpenAI 官方（512K-1M 区间） |
| Gemini 3 Flash | 32.6% | contextarena.ai |
| Gemini 3 Pro | 24.5% | contextarena.ai |
| Claude Sonnet 4.5 | 18.5% | Anthropic 系统卡 |
| Gemini 2.5 Pro | 16.4% | Google 技术报告（[PDF](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf)） |

Claude Opus 4.6 在 1M 处的 76.0% 是一个质变。对比前代 Sonnet 4.5 的
18.5%，提升了 4 倍。Anthropic 在 Opus 4.6 的[发布公告](https://www.anthropic.com/news/claude-opus-4-6)中称这是”a
qualitative shift in how much context a model can actually use while
maintaining peak performance”。

## Context Window ≠ Context Reliability

![Context Window vs Reliability](imgs/context_window_vs_reliability.png)

Context Window vs
Reliability

这张散点图直观展示了一个反直觉的现实：context window
越大，未必性能越好。

GPT-5.2 只有 256K 的 context
window，但在该范围内的最远测试点（128K-256K）仍然有 77%。而 Gemini 2.5
Pro 虽然标称 1M context window，在 1M 处只有 16.4%。Gemini 3 Pro
虽然持续改善，但 1M 处也只有 24.5%。相比之下，Claude Opus 4.6 是唯一在
1M 处保持 70%+ 的模型。

这个现象在学术研究中也有系统性验证。[arXiv 2409.12640](https://arxiv.org/html/2409.12640v2) 的
Michelangelo 评估发现：GPT 和 Claude 模型在短 context（8K
以下）上表现更好，但衰减速率更快。Gemini 模型在短 context
上起点较低，但衰减更平缓，在超长
context（1M）处反而可能反超。这个”交叉效应”说明短 context 性能和长
context 性能之间存在内在张力，模型很难两者兼得。

## 各家 Long Context 策略复盘

### Anthropic：保守但有效的”晚发先至”

Anthropic 的 context window 扩展时间线：

| 时间 | 模型 | Context Window | 备注 |
| --- | --- | --- | --- |
| 2024.3 | Claude 3 Opus/Sonnet | 200K | 技术上已支持 1M 但不开放 |
| 2024.6 | Claude 3.5 Sonnet | 200K | 仍为 200K |
| 2025.8 | Claude Sonnet 4 | 200K + 1M beta | 首次开放 1M beta，仅限 Tier 4 用户 |
| 2025.9 | Claude Sonnet 4.5 | 200K + 1M beta | 1M 性能差（MRCR 18.5%） |
| 2025.11 | Claude Opus 4.5 | 200K | Opus 级别仍未提供 1M |
| 2026.2.5 | Claude Opus 4.6 | 200K + 1M beta | 首个 Opus 级 1M，MRCR 76% |
| 2026.2.17 | Claude Sonnet 4.6 | 200K + 1M beta | MRCR 65.8% at 1M |
| 2026.3.13 | Opus 4.6 + Sonnet 4.6 | 1M GA | 1M 正式发布，标准定价（[来源](https://forum.cursor.com/t/anthropic-just-announced-1m-context-ga-at-standard-pricing-for-opus-4-6-sonnet-4-6-when-will-cursor-reflect-this/154701)） |

来源：[Anthropic
Release Notes](https://support.claude.com/en/articles/12138966-release-notes)、[Claude Opus 4.6
发布](https://www.anthropic.com/news/claude-opus-4-6)

从 2024 年 3 月到 2026 年 3 月，整整两年 Anthropic 都在
200K。Anthropic 工程博客在 2025 年 9 月的一篇[文章](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)中明确阐述了他们的哲学：

> “Waiting for larger context windows might seem like an obvious
> tactic. But it’s likely that for the foreseeable future, context windows
> of all sizes will be subject to context pollution and information
> relevance concerns. The solution isn’t more capacity; it’s better
> management of existing capacity.”

这段话暗示 Anthropic 认为 context window 扩张不是解决方案，context
管理才是。回头看数据，这个策略确实有效：当他们最终推出 1M
时，性能（76%）远超早年就提供 1M 的 Gemini（24.5%）。

### Google Gemini：先行者的困境

| 时间 | 模型 | Context Window | MRCR v2 8-needle |
| --- | --- | --- | --- |
| 2024.2 | Gemini 1.5 Pro | 1M (后扩至 2M) | 未公布 8-needle |
| 2025.2 | Gemini 2.0 Flash | 1M | ≤128K: 18.4%, >1M: 10.2% |
| 2025.6 | Gemini 2.5 Pro | 1M (2M 规划中) | ≤128K: 58.0%, >1M: 16.4% |
| 2025.11 | Gemini 3 Pro | 1M | 128K: 77.0%, 1M: 26.3% |
| 2026.2 | Gemini 3.1 Pro | 1M | 128K: 84.9%, 1M: 26.3% |

来源：[Google
Gemini Blog](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/gemini-model-thinking-updates-march-2025/)、[Gemini
2.5 Tech Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf)、[Gemini
3.1 Pro Model Card](https://deepmind.google/models/model-cards/gemini-3-1-pro/)

Google 从 2024 年初就率先提供了 1M context
window，一度是行业唯一。但在 8-needle MRCR v2 上的表现一直不理想。Gemini
2.0 Flash 在 1M 处只有 10.2%，到 Gemini 3 Pro 提升到 26.3%，但与 Claude
Opus 4.6 的 76% 相比差距仍然巨大。

有意思的是 Gemini 在 128K 处的改善速度很快：从 2.5 Pro 的 58.0% 到
3.1 Pro 的 84.9%。在 128K 处，Gemini 3.1 Pro 与 Claude Sonnet 4.6
并列（84.9%），说明中等 context 下各家已经趋同（[来源](https://medium.com/@Micheal-Lanham/the-march-2026-frontier-gpt-5-4-vs-gemini-3-1-vs-claude-4-6-daebf22e672e)）。但
1M 处的鸿沟还在。

开发者社区对 Gemini 的 long context 可靠性也有不少抱怨。Reddit
上有用户反映 Gemini 3 Pro 在使用 15-20% 的标称 context window
后就出现明显性能退化（[来源](https://www.rdworldonline.com/claude-opus-4-6-targets-research-workflows-with-1m-token-context-window-improved-scientific-reasoning/)）。

值得注意的是 Latenode 声称 Gemini 2.5 Pro 在 53 万 tokens 内达到 100%
recall，1M 处 99.7%（[来源](https://latenode.com/blog/ai-technology-language-models/google-gemini-gemini-2-0-2-5-pro-flash/gemini-25-pros-long-context-window-real-world-impact)）。但这个数据**未能在
Google 官方技术报告中找到验证**，可能来自不同的测试方法（如
2-needle 而非 8-needle，或简单的 passkey retrieval 而非 MRCR）。

### OpenAI：精度优先的区间制

OpenAI 的策略与 Anthropic 类似，都是偏保守的。GPT-5.2 选择了 256K 的
context window（部分配置
400K），把精力集中在让这个范围内的性能尽可能完美。GPT-5.4 扩展到 1.1M
时，272K 是标准模式，1M 是付费 premium 模式（2 倍计费）（[来源](https://openai.com/index/introducing-gpt-5-4/)）。

GPT-5.4 在 Codex 中支持 1M context window（实验性），需要通过
`model_context_window` 和
`model_auto_compact_token_limit` 配置启用。

## 其他 Long Context Benchmark 补充

MRCR v2 是当前最重要的 long context 横评
benchmark，但不是唯一的。以下是其他 benchmark 的关键发现：

**Graphwalks**（多跳图推理）：Claude Opus 4.6 和 GPT-5.2
在 Parents 任务上几乎打平（71.1% vs 72.0% at 1M），但 BFS
任务上都很挣扎（~40% at 1M）。来源：[Sonnet 4.6
System Card](https://anthropic.com/claude-sonnet-4-6-system-card)

**LongBench v2**（长文档理解，503 题）：Gemini 2.5 Pro
以 63.3% 领先，超过人类基线（53.7%）。GPT-4o 46.0%，Claude 3.5 Sonnet
41.0%。来源：[LongBench v2
Leaderboard](https://longbench2.github.io/)

**RULER**（检索/聚合/推理，13 项任务）：在 128K 处，仅
Gemini 1.5 Pro（94.4%）和 Jamba-1.5-large（95.1%）能维持 90% 以上。GPT-4
降至 81.2%。来源：[NVIDIA
RULER](https://github.com/NVIDIA/RULER)

**LongBench Pro**（更新的长文档评测）：排名前三为 Gemini
2.5 Pro（73.42）、GPT-5（72.61）、Claude-4-Sonnet（69.87）。Gemini 2.5
Pro 展现了对 context 长度的”钝感”：256K 得分（71.77）与 8K
得分（74.50）几乎持平。来源：[arXiv 2601.02872](https://arxiv.org/html/2601.02872v1)

## 方法论注意事项

### 评测条件差异

同一个 benchmark 在不同评测条件下的分数差异很大。以 GPT-5.2 的 MRCR
v2 256K 8-needle 为例：

- OpenAI 官方（xhigh reasoning, 128K-256K
  区间）：**77.0%**
- Anthropic 系统卡引用 contextarena.ai 数据（256K
  聚合）：**63.9%**
- OpenAI 自报（xhigh reasoning, 256K
  聚合）：**70.0%**

同一模型、同一
benchmark，三个来源给出三个不同数字。原因包括：reasoning effort
设置不同、聚合方式不同（按区间平均 vs
按样本加权平均）、温度参数差异等。

### 8-needle vs 其他变体

Google 在 Gemini 博客中经常引用的”MRCR 91.5% at 128K”数字可能是
4-needle 变体或 MRCR v1 的结果，而非 8-needle。Gemini 2.5 Pro 在 Google
自己的技术报告中，8-needle ≤128K 得分只有 54.3-58.0%。这个差异说明
needle 数量对难度影响极大，在比较不同来源的 MRCR
数据时必须确认是否为同一变体。

## 结论

“context window 军备竞赛”这个叙事框架已经过时了。The March 2026
Frontier 文章（[来源](https://medium.com/@Micheal-Lanham/the-march-2026-frontier-gpt-5-4-vs-gemini-3-1-vs-claude-4-6-daebf22e672e)）总结得很好：

> “The context-window arms race is over. The context-reliability race
> is the real story now. And it’s a harder problem. Stuffing a million
> tokens into a window is engineering. Getting the model to actually
> *use* what’s buried at token 600,000 is science.”

行业研究也支持这个判断：Awesome Agents 的分析（[来源](https://awesomeagents.ai/leaderboards/long-context-benchmarks-leaderboard/)）指出，模型的有效
context 容量通常只有标称值的
60-70%，超过这个范围后性能衰减就不可忽视。

对于实际使用者来说，关键的几个 takeaway：

- 如果你的 context 在 128K 以内，各家前沿模型差异不大，Gemini 3.1 Pro
  和 Claude Sonnet 4.6 都在 85% 左右。
- 如果你需要可靠地使用 256K-1M 的 context，Claude Opus 4.6
  目前是唯一维持 70%+ 性能的选择。
- 不要被标称的 context window 大小误导。Gemini 的 1M 和 Claude 的 1M
  在 MRCR v2 8-needle 上的表现差距是 3 倍（24.5% vs 76.0%）。
- GPT-5.2 在 256K 内确实很强，但它之所以”看起来完美”，部分原因是从未在
  256K 以上接受过考验。

---

**可视化文件**：`imgs/mrcr_v2_performance_curve.png`、`imgs/mrcr_v2_cross_model.png`、`imgs/context_window_vs_reliability.png`

**可视化脚本**：`assets/long_context_benchmark_viz.py`

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
