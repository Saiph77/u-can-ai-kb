---
title: "你的 Agent 管线里，最贵的模型可能在最错的位置"
date: 2026-04-09
source: https://yage.ai/share/agentopt-model-selection-pipeline-20260409.html
slug: agentopt-model-selection-pipeline-20260409
lang: zh
---
# 你的 Agent 管线里，最贵的模型可能在最错的位置

发布于 2026 年 4 月 9 日 · [查看原网页](https://yage.ai/share/agentopt-model-selection-pipeline-20260409.html)

## 你的 Agent 管线里，最贵的模型可能在最错的位置

搭 agent
管线时，大多数人的默认直觉是：关键环节用最强模型，次要环节用便宜模型。Planning
用 Opus，执行用 Haiku，收尾用
Sonnet。这个分配方式符合常识，也是目前社区最常见的做法。

AgentOpt（[arXiv:2604.06296](https://arxiv.org/abs/2604.06296)，2026年4月）的实验数据对这个直觉提出了一个尖锐的反例：在
HotpotQA 的 planner-solver 管线中，Claude Opus 放在 planner
位置的准确率是 31.71%，在 81 种模型组合中排名倒数。而把 Ministral 8B
放在 planner、Opus 放在 solver，准确率达到
74.27%。一个参数量小一个数量级的模型做 planning，效果是 Opus 做 planning
的两倍以上。

这组数据的意义在于它指向的判断框架可以迁移到很多场景：模型质量是角色和管线交互的函数，而不是一个可以脱离上下文搬运的属性。

## 论文做了什么

AgentOpt 是微软研究院（Microsoft Research）与 Columbia
DAPLab、Cornell 合作的一项工作。它把 agent
管线中的模型选择当作组合优化问题来处理：给定一个多步管线，在每个角色上分别尝试不同模型，然后用搜索算法找到准确率和成本之间的最优组合。论文测试了
9 个模型、4 个 benchmark、最多 81
种组合。框架开源（`pip install agentopt-py`），通过 httpx
transport interception 实现框架无关的 API 调用拦截。

## 为什么 Opus 做 planner 会失败

Opus 的推理能力没有变化，变化的是角色对能力的需求方式。Planner
的职责是拆解任务并把子任务交给 solver，但 Opus 作为 planner
时会直接自己回答问题，跳过对下游 solver 的工具调用。7/9 次 solver
根本没被调用。结果是 planner
产出的是一个质量不高的直接回答，整条推理链路被破坏。

Ministral 8B 作为 planner
反而表现好，原因恰恰在于它的能力边界更清晰：它知道自己回答不了，于是老老实实地拆解任务、调用工具、把子问题交给下游。

这个机制本身就是一个可复用的判断框架：在多步管线中，每个角色需要的不是最强的模型，而是在该角色的行为约束下表现最好的模型。一个模型的能力越强，它越有可能突破角色边界去”帮忙”，而这种帮忙在管线语境下是破坏性的。

这个判断可以交叉验证。在 MathQA 的 solver-critic 管线中，当 answerer
固定为 Opus 时，9 种 critic 模型的准确率差距仅 2.9 个百分点——critic
角色几乎不影响结果。在 BFCL 上，Opus、Kimi K2.5、Qwen3 Next 并列 70%，但
Qwen3 Next 的成本仅为 Opus 的
1/32。整体来看，优化模型分配可以在保持准确率的同时把成本降低 13 到 32
倍。

## 更大的图景

AgentOpt
的发现并非孤立事件。过去几个月，多项独立研究从不同角度指向同一个方向：agent
系统的性能瓶颈正在从模型本身转移到模型周围的系统设计。

Stanford 的 Meta-Harness（[arXiv:2603.28052](https://arxiv.org/abs/2603.28052)，2026年3月）发现，仅优化模型周围的
harness code，同一个模型的得分就能产生 6
倍差距。模型没换，提示词没换，改变的只是模型被放在什么样的工作环境里。W4S（[Nie
et al., COLM 2025](https://openreview.net/pdf/72966922d815c8f5b1a8ecc362e22fb4ac76e1b5.pdf)）让一个弱模型充当 meta-agent
为强模型设计工作流，结论是工作流设计的质量对最终表现的影响超过了执行模型本身的能力差异。Select-then-Solve（[arXiv:2604.06753](https://arxiv.org/abs/2604.06753)，2026年4月8日）则关注推理范式的选择，同样是把优化重心从”用什么模型”转向”模型在什么条件下工作”。

把这些工作放在一起看，趋势很清晰：当模型足够强时，系统设计层面（角色分配、管线拓扑、harness
工程、工作流设计）对最终表现的边际贡献，开始超过模型本身的能力升级。AgentOpt
的贡献是用受控实验量化了其中一个维度。

## 局限

这是 v0.1，只测了 4 个问答和函数调用类 benchmark，没有 coding
任务，没有长链路 agentic 任务，管线拓扑也限于 2-3 个角色。Opus 做
planner
失败的现象是否在代码生成管线中同样成立，目前没有数据。此外，论文没有测试一个显而易见的工程方案：在
system prompt 里强制要求 planner 输出工具调用而非直接回答。如果一个好的
prompt 就能修复问题，那根源是提示词设计而非模型选择。

## 对 Builder 的实际意义

三个方向。第一，对你的 agent 管线做一次低成本测试：把 planner 或
orchestrator
换成一个更小的模型，看性能是否显著下降。如果没有，你正在为一个不需要的能力等级付费。第二，在需要模型遵守分工协议的角色上，模型的”听话程度”比”聪明程度”更重要。第三，模型选择是持续调优过程，不是一次性采购决策——管线设计变了，最优组合大概率也变了。

核心思维方式的转变是：模型选择的思考单位从”哪个模型最强”变成”角色×管线”。AgentOpt
用数据证实了这一点。即使这组数据的覆盖面还有限，这个思维方式本身已经值得在日常工程实践中采用。

## 引用与资源

- AgentOpt 论文：[arXiv:2604.06296](https://arxiv.org/abs/2604.06296)（Wenyue Hua
  et al., 2026年4月7日）
- AgentOpt 框架：`pip install agentopt-py`
- W4S（Workflows for Strong）：[Nie
  et al., COLM 2025](https://openreview.net/pdf/72966922d815c8f5b1a8ecc362e22fb4ac76e1b5.pdf)
- Meta-Harness：[arXiv:2603.28052](https://arxiv.org/abs/2603.28052)（Lee et
  al., Stanford, 2026年3月）
- Select-then-Solve：[arXiv:2604.06753](https://arxiv.org/abs/2604.06753)（Zhou et
  al., 2026年4月8日）

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
