---
title: "MSA 调研：长期记忆开始进入新的分工阶段"
date: 2026-03-20
source: https://yage.ai/share/msa-memory-sparse-attention-survey-20260320.html
slug: msa-memory-sparse-attention-survey-20260320
lang: zh
---
# MSA 调研：长期记忆开始进入新的分工阶段

发布于 2026 年 3 月 20 日 · [查看原网页](https://yage.ai/share/msa-memory-sparse-attention-survey-20260320.html)

> MSA 还不是长期记忆的终局方案，但它清楚地指向了下一阶段分工。
> 长期记忆不会只靠外部 RAG，也不会全塞进模型内部。
> 更可能的未来是模型内稀疏访问和外部上下文引擎各自承担不同职责。

**调研日期**：2026-03-20  
**调研对象**：EverMind 发布的 MSA（Memory Sparse
Attention）及相关路线  
**定位**：external-facing，高层技术直觉报告

---

## 核心判断

MSA
值得关注，但关注点不在于它是否已经解决了长期记忆问题，而在于它让一个变化开始变得清晰：长期记忆这件事，正在从纯外部系统能力，转向模型内部机制与外部系统协同分工的问题。

过去两年，行业里比较稳定的分工是这样的：模型负责推理，外部系统负责记忆。外部系统的具体形式可以是
RAG、向量数据库、知识图谱、agent memory
layer，也可以是更简单的文档和索引系统。MSA
提出的方向，是把其中一部分访问能力向模型内部移动，让模型自己学会在极长历史中进行稀疏选择和多跳访问。

这件事为什么重要。因为它改变的不是某个 benchmark
上多拿了几分，而是我们对 AI 系统边界的理解。问题开始从
模型有多大窗口，转向
模型内部该保留什么能力，外部系统又该保留什么能力。

同时，这篇工作当前还处在比较早的阶段。公开材料主要是 README
和论文，代码和模型没有完整开放，第三方复现也还没有出现。所以更准确的态度是：把它当成一个技术地图上的重要节点，而不是一份已经可以直接照着落地的架构手册。

---

## 为什么它会在现在出现

MSA 不像一个突然冒出来的新想法，它更像几条路线发展到 2026
年之后，自然汇合出来的结果。

第一条路线，是长上下文能力的持续扩张。行业已经证明 context window
可以扩到 1M 甚至更高，但 benchmark
也已经很清楚地告诉我们，大窗口和高质量访问不是同一件事。真正稀缺的能力，是在极长上下文里稳定定位相关信息，并把这些信息持续转化为推理质量。我们在
[Long
Context 横评：三家都到了 1M，然后呢？](https://yage.ai/share/long-context-benchmark-20260315.html)
里已经看到这个差异：容量扩展很快，访问可靠性提升得慢得多。

第二条路线，是 RAG 的成熟。今天的 RAG 已经不是最早那种
embed、top-k、拼 prompt 的轻量流程。它正在演化成更完整的 context
engine，负责状态、来源、权限、规划和多跳检索。[RAGFlow
对 RAG→Context Engine 的复盘](https://ragflow.io/blog/rag-review-2025-from-rag-to-context) MSA
的价值，在于它试图把这套能力里的某一部分，从外部系统拉回模型内部。

第三条路线，是稀疏化成为主流工程方向。无论是 sparse attention、KV
cache eviction，还是 DeepSeek 今年几条与 memory
相关的工作，处理的都是同一个约束：全量保留和全量访问的成本太高，系统需要在极大信息空间里只保留少量高价值连接。[Ben
Dickson 对 sparse attention 的分析](https://bdtechtalks.substack.com/p/how-sparse-attention-is-solving-ais)

把这三条线放在一起，MSA 的 timing
就比较容易理解了。它回答的不是一个新问题，而是一个已经越来越尖锐的老问题：当上下文继续变长之后，模型到底应该如何访问历史。

---

## 如果把长期记忆画成一张技术地图

理解
MSA，最有效的方法不是直接拆论文，而是先看它在整张地图上的位置。

今天围绕长期记忆，大致可以分成五条路线。

第一条路线，是继续扩大上下文窗口。这条路线最直接，产品改动小，默认使用成本也低。问题也很明确：上下文越长，噪声、定位成本和注意力衰减都会同步上升。这条路线适合中等规模任务，适合作为基础能力层，不适合作为长期记忆的完整答案。

第二条路线，是把记忆放在模型外部，用 RAG 或外部 memory system
管理。这是今天最成熟的路线。它支持更新、审计、权限控制、结构化过滤，也容易和真实产品的数据层对接。它的成本主要在系统边界更多，多跳推理和状态一致性需要额外设计。

第三条路线，是把历史压缩成 recurrent 或 fixed-size
memory。这类方法的优点是计算边界清晰，成本更可控。问题在于，一旦压缩过程丢失了关键信息，后续过程就很难恢复。这条路线更像模型内部的
summary memory，适合连续状态维护，不适合对事实可追溯性要求高的任务。

第四条路线，是把记忆做成模型内部可访问的稀疏检索层。MSA
就位于这里。它的目标是让模型自己学习如何选择性访问历史信息，从而缩短
retrieval 与 reasoning
之间的距离。它的优势在于多跳链路更有机会保持连续，问题在于 memory
更新、来源追踪、可验证性和系统成本都还没有成熟答案。

第五条路线，是混合架构：模型内部稀疏记忆，加上外部上下文引擎。从产品约束出发，这条路线目前最合理。模型内部记忆适合处理超长、多跳、需要保持推理连续性的部分。外部上下文引擎负责动态更新、权限、审计、来源和结构化查询。

这也是我现在对这类工作的基本判断。长期记忆不会收敛成单一路线。更可能出现的，是不同层级的记忆能力分别落在模型内部和外部系统里，各自承担不同职责。

---

## MSA 在这张地图上的位置

把地图放在前面之后，MSA 的定位就容易看清楚了。

MSA 试图做的事情，是把大规模历史内容编码成可路由的 latent
memory，然后通过稀疏选择只取出与当前问题高度相关的部分，再与当前上下文结合进入后续生成过程。[MSA GitHub](https://github.com/EverMind-AI/MSA)

从系统视角看，它更接近模型内部的稀疏访问层。它推进的是长上下文访问能力和检索增强之间的融合，而不是完整意义上的长期记忆系统。这个区分非常关键。长上下文访问、检索增强、长期记忆的写入与维护，分别对应不同层级的问题。MSA
当前主要推进的是前两层。

如果只保留最少量的技术细节，它的骨架大致可以压缩成四点。第一，历史内容先被编码成可检索的
latent states，再做 top-k 选择，而不是对全部历史 token 做 dense
attention。第二，它使用 document-wise RoPE
等位置设计，试图缓解训练长度与推理长度之间的漂移问题。第三，它把 KV
cache 做成分层存储，一部分在 GPU，一部分在
CPU/DRAM，用系统工程方式支持超长 memory。第四，它引入多轮
retrieval-generation interleave，用于提升多跳任务里的上下文扩展能力。[MSA GitHub README](https://github.com/EverMind-AI/MSA)

这四个选择放在一起，决定了它的角色：它是一种把检索、稀疏访问和系统扩展放到同一层里处理的方案。

---

## 它和之前工作的关系

从历史脉络看，MSA 很清楚地属于组合式推进。

最接近的前史，是 2022 年的 [Memorizing Transformers](https://arxiv.org/abs/2203.08913) 和
2023 年的 [LongMem](https://arxiv.org/abs/2306.07174)。这两篇都已经在做相近的事情：缓存历史表示，按需检索相关内容，再与本地上下文融合。MSA
和它们的差别，主要体现在端到端训练方式、检索粒度和系统扩展规模上。

从预训练系统视角看，2022 年的 [RETRO](https://proceedings.mlr.press/v162/borgeaud22a/borgeaud22a.pdf)
同样关键。RETRO
早就说明，模型可以在生成过程中与外部块做稀疏交互，而不必把所有知识压进参数。MSA
与 RETRO 的差别，更多是具体架构与工程实现的差异。

从压缩式 memory 的路线看，2024 年的 [Infini-attention](https://arxiv.org/abs/2404.07143) 和更早的 [Recurrent
Memory Transformer](https://papers.neurips.cc/paper_files/paper/2022/file/47e288629a6996a17ce50b90a056a0e1-Paper-Conference.pdf) 代表另一种解法。它们通过 recurrent 或 compressive
memory 把远距离信息压成有限状态。MSA 所在的位置更靠近检索式
memory，但它面对的是同一个核心问题：如何在有限计算下处理超长历史。

从系统工程层面看，[H2O](https://arxiv.org/abs/2306.14027)
和 [StreamingLLM](https://arxiv.org/abs/2309.17439)
这类工作已经说明，KV cache 需要稀疏化管理。MSA
延续了这个判断，把保留下来的内容进一步组织成可路由的 memory tier。

所以，MSA
的价值主要来自已有思想的重组与规模推进，而不是来自完全独立的新原理。这个判断并不会削弱它的重要性。很多真正有影响力的系统工作，本来就是在已有方向之间重新划分边界，把原本分散的能力整合成可用架构。

---

## 这类架构什么时候有价值

MSA 这类方案真正可能改变产品设计的场景，主要集中在四类任务。

第一类，是单一巨大语料内部的多跳推理。例如法规、合同、研究文献之间的跨文档链式归纳。这里的关键难点，是连续地连接多段证据，而不是只检索一段局部答案。MSA
的价值，在于把这条链路更紧密地放进模型访问过程里。[MSA README](https://github.com/EverMind-AI/MSA)

第二类，是长周期 agent
记忆。例如长期项目协作、客户成功系统、跨会话研究助手。这里的核心问题，是如何把分散在长时间范围内的事件重新组织成当前推理需要的上下文。EverMind
在记忆 benchmark 上持续推进这件事，也说明他们把 MSA 放在长期 agent
memory 的大框架里理解。[EverMemBench](https://arxiv.org/html/2602.01313v3)

第三类，是规模极大但变化较慢的知识底座。如果一部分知识相对静态，同时调用频率很高，把部分访问能力向模型内部移动，的确有可能改变成本结构。这也是
DeepSeek Engram 会被频繁拿来一起讨论的原因。[DeepSeek Engram](https://github.com/deepseek-ai/Engram)

第四类，是长程 agent workflow。coding agent、research agent
这类系统会在单次任务中产生大量中间状态。此时成本瓶颈往往来自历史状态的保存与访问，稀疏注意力与内部
memory 机制在这里的意义会更直接。[Sebastian
Raschka 对 DeepSeek 技术栈的梳理](https://magazine.sebastianraschka.com/p/technical-deepseek)

这些场景有一个共同点：问题不只是信息多，而是信息之间存在分散、多跳、跨时间的依赖关系。

---

## 这类架构什么时候价值有限

价值有限的场景也很清楚。

第一类，是动态数据场景。知识库持续变化时，外部 RAG
仍然具备明显优势，因为它可以直接更新索引。MSA 当前公开材料几乎没有解释
memory write 与热更新机制。

第二类，是审计和责任边界清晰的系统。法律、金融、医疗、企业知识管理，通常要求答案附带明确出处。外部检索系统天然支持来源追踪，模型内部
memory 机制在这一点上还没有成熟接口。[Redis
对 RAG 与大窗口的比较](https://redis.io/blog/rag-vs-large-context-window-ai-apps/)

第三类，是多租户与权限控制场景。企业数据访问通常依赖用户身份、组织边界和策略规则。RAG
更容易把权限控制放在查询层实现，模型内生 memory
方案在这方面还缺乏明确设计。

第四类，是简单任务。语料规模小、更新频率低、来源追踪要求弱时，直接使用现有大窗口模型，或构建简单
RAG，通常具备更好的落地效率和调试成本。

把这些场景放在一起，可以得到一个更一般的判断：这类架构更适合处理访问质量问题，不适合直接替代更新、审计和权限问题。

---

## 当前最缺的证据

MSA 当前最缺的不是更多宣传，而是更扎实的验证。

第一，缺生产数据。现有公开材料主要是 README
和论文，代码与模型尚未完整开放，也没有第三方线上部署数据。延迟、吞吐、成本曲线和失败模式都还没有出现。

第二，缺 memory write
机制。很多论文都在证明如何更好地读取历史信息，但真实系统同样依赖写入、更新、版本化和遗忘。只有读取路径的
memory architecture，无法覆盖长期记忆系统的完整需求。

第三，缺贴近产品环境的 benchmark。needle-in-a-haystack、长文档
QA、RULER
这类评测有价值，但它们和真实世界中的权限、时间更新、来源审计、跨系统查询仍然有明显距离。

第四，缺独立复现。只要关键结论仍然主要来自作者自己，这篇工作就更适合作为强信号，而不是稳定共识。

这些缺口决定了我们今天应该如何使用这篇论文。它更适合用来更新架构直觉，而不是直接替代现有设计。

---

## 最后的判断

MSA
真正提醒我们的，不是某个模型终于拥有了长期记忆，而是长期记忆问题本身开始进入新的分工阶段。

未来几年里，更可能出现的不是单一路线收敛，而是多层分工逐渐清晰。模型内部稀疏记忆负责超长、多跳、需要保持推理连续性的访问问题。外部上下文引擎负责动态更新、权限、审计、来源和结构化查询。文档、索引、RAG、memory
layer 和模型内部机制，会逐步落在同一套架构里，但承担不同职责。

对于 AI
builder，更值得持续追问的问题是：哪些记忆必须保持外部、可审计、可更新；哪些记忆值得被内生化，直接进入模型推理过程。这个问题会比
MSA 本身活得更久，也会持续影响 agent 架构的设计方式。

---

## 参考资料

- MSA 官方仓库与论文入口：https://github.com/EverMind-AI/MSA
- Memorizing Transformers：https://arxiv.org/abs/2203.08913
- RETRO：https://proceedings.mlr.press/v162/borgeaud22a/borgeaud22a.pdf
- LongMem：https://arxiv.org/abs/2306.07174
- MemLong：https://arxiv.org/abs/2408.16967
- Infini-attention：https://arxiv.org/abs/2404.07143
- Recurrent Memory
  Transformer：https://papers.neurips.cc/paper\_files/paper/2022/file/47e288629a6996a17ce50b90a056a0e1-Paper-Conference.pdf
- H2O：https://arxiv.org/abs/2306.14027
- StreamingLLM：https://arxiv.org/abs/2309.17439
- EverMemBench：https://arxiv.org/html/2602.01313v3
- DeepSeek Engram：https://github.com/deepseek-ai/Engram
- RAGFlow 对 RAG→Context Engine
  的复盘：https://ragflow.io/blog/rag-review-2025-from-rag-to-context
- Redis 对 RAG
  与大窗口的比较：https://redis.io/blog/rag-vs-large-context-window-ai-apps/
- Ben Dickson 对 sparse attention
  的分析：https://bdtechtalks.substack.com/p/how-sparse-attention-is-solving-ais
- Sebastian Raschka 对 DeepSeek
  技术栈的梳理：https://magazine.sebastianraschka.com/p/technical-deepseek

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
