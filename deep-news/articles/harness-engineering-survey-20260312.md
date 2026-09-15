---
title: "Harness Engineering：当人类从写代码转向设计 Agent\n的工作环境"
date: 2026-03-12
source: https://yage.ai/share/harness-engineering-survey-20260312.html
slug: harness-engineering-survey-20260312
lang: zh
---
# Harness Engineering：当人类从写代码转向设计 Agent 的工作环境

发布于 2026 年 3 月 12 日 · [查看原网页](https://yage.ai/share/harness-engineering-survey-20260312.html)

> AI 编程的杠杆点已经从写代码转向设计 agent 的工作环境。 OpenAI 和
> Cursor 的共同结论是，文档、约束、反馈回路和验证基础设施比提示词更重要。
> 人类工程师正在从代码生产者变成 harness 设计者。

> 日期：2026-03-12

## 1. 概述

2026 年初，OpenAI 和 Cursor 几乎同时发布了各自在 agent-first
软件开发上的实践报告。OpenAI 的 Ryan Lopopolo
描述了一个三人团队如何用五个月时间、零行手写代码，让 Codex
生成了约一百万行代码的内部产品。Cursor 的 Wilson Lin
描述了如何用数千个并行 agent 自主运行一周，从零构建出一个 web
浏览器引擎。

两篇文章来自不同的公司、不同的产品、不同的技术栈，但它们收敛到了同一个结论：当
AI agent
成为主要的代码生产者时，人类工程师的核心工作发生了本质转变。这个转变不是”用
AI 辅助编程”的渐进升级，而是一个范式跳跃。OpenAI 把这个新范式命名为
harness engineering。

Harness
这个词在工程语境里通常指”线束”或”测试夹具”，在这里它指的是围绕 agent
构建的整个工作环境：文档体系、架构约束、反馈循环、验证工具、可观测性基础设施。人类工程师的产出不再是代码，而是这个
harness。代码由 agent 生产，人类负责让 agent 能可靠地生产代码。

这篇调研的目标是厘清 harness engineering 的核心概念，对比 OpenAI 和
Cursor 两条路径的异同，以及这些发现对软件工程实践的启示。

## 2. OpenAI：从零开始的 Agent-First 产品

### 2.1 实验设计

OpenAI 的实验有一个极端约束：**零行手写代码**。从第一个
commit 开始，所有代码（包括 CI
配置、内部工具、设计文档、评估框架、发布脚本）都由 Codex
生成。三名工程师后来扩展到七名，五个月内合并了约 1500 个
PR，平均每人每天 3.5 个。

这个约束不是为了证明 AI
能写代码（这已经不需要证明），而是为了逼出一个问题：当你被迫只通过设计环境来影响代码质量时，什么才是真正重要的？

### 2.2 六个核心发现

**发现一：AGENTS.md 应该是目录，不是百科全书。**
他们最初尝试把所有规则塞进一个大文件，失败了。上下文窗口是稀缺资源，太多信息等于没有信息。最终方案是一个约
100 行的 AGENTS.md 作为导航，指向 `docs/`
下的结构化知识库。这个知识库包括设计文档、执行计划、架构决策、质量评分。Vercel
后来的实证研究验证了这一点：一个压缩的 8KB AGENTS.md 在 eval 中达到 100%
通过率，而 skills 机制最多只达到 79%。被动上下文优于主动检索。

**发现二：Codex 看不到的东西等于不存在。**
这是引发本次调研的那句话的出处。Google Docs 里的讨论、Slack
上的对齐、团队成员脑子里的隐含知识，对 agent
来说统统不存在。解决方案是把所有知识推入 repo：Slack
上达成的架构共识要变成 markdown，设计决策要变成执行计划（execution
plans），技术债要变成可追踪的文档。这和培训新员工的逻辑一样，三个月后入职的人看不到当时的
Slack 讨论，只能看 repo 里留下的东西。

**发现三：Agent review 可以替代大部分人类 review。**
人类可以审查 PR，但不再是必需的。他们让 Codex 先自我审查，再请求其他
agent 审查，在循环中迭代直到所有 agent reviewer
满意。人类的角色从逐行审查代码转向了定义审查标准、在 AGENTS.md
中编码品味偏好。OpenAI 后来的 scaling code verification
文章提到，他们的系统每天处理超过 10 万个外部 PR，80%
以上的评论反应是正面的。

**发现四：强制约束比微管理实现更有效。** 他们为 agent
建立了严格的分层架构（Types → Config → Repo → Service → Runtime →
UI），通过 Codex 生成的自定义 linter
强制执行依赖方向。关键区别在于：他们要求 Codex
在边界处解析数据类型（parse, don’t validate），但不规定用什么库（Codex
自己选了 Zod）。这种”定义边界、放手实现”的模式，让 agent
在约束内保持了充分的自由度。

**发现五：吞吐量改变了合并哲学。** 当 agent 的 PR
产出速度远超人类的注意力时，传统的阻塞式合并门控变得适得其反。等待比纠错更昂贵。他们采用了最小阻塞的合并策略：PR
生命周期短，测试 flake
用后续运行处理而非阻塞进度。文章坦言这在低吞吐量环境中不负责任，但在
agent 吞吐量远超人类注意力的场景下是正确的权衡。

**发现六：熵会积累，需要”垃圾回收”。** Codex 会复制 repo
中已有的模式，包括不理想的模式。起初团队每周五花 20% 的时间手动清理”AI
slop”，很快意识到这不可持续。他们转向了自动化方式：把”黄金原则”编码进
repo，定期运行后台 Codex 任务扫描偏离、更新质量评分、开修复 PR。这些 PR
大多可以在一分钟内审阅并自动合并。技术债像高息贷款，持续小额偿还比累积后一次性处理更经济。

### 2.3 可观测性作为杠杆

OpenAI 的一个重要投入是把应用本身变得对 Codex 可观测。他们接入了
Chrome DevTools Protocol，让 Codex 能截屏、操作 DOM、驱动 UI
流程。他们为每个 git worktree
建立了独立的可观测性栈（日志、指标、追踪），Codex 可以用 LogQL 和 PromQL
查询。这意味着像”确保关键用户路径中没有超过两秒的 span”这样的 prompt
变得可执行。

单次 Codex 运行经常持续六小时以上，通常在人类睡觉的时候执行。

## 3. Cursor：Multi-Agent 协调的演化史

### 3.1 问题的不同侧面

如果说 OpenAI 的文章回答的是”人类应该做什么”，Cursor
的两篇文章回答的是”如何协调大量 agent 一起工作”。Cursor
的目标是验证一个基本问题：能否通过投入 10 倍的计算来获得 10
倍的有意义吞吐量？

他们选择了从零构建一个 web 浏览器引擎作为基准任务（用 Rust），数百个
agent 并行运行一周，生成了超过一百万行代码和一千个文件。

### 3.2 四次架构迭代

Cursor
的文章真正有价值的地方在于，它坦诚地记录了四次架构迭代的失败和教训，而非只展示最终方案。

**第一次：平等自协调（失败）。** 所有 agent
地位平等，通过共享状态文件协调。每个 agent
查看其他人在做什么，认领任务，更新状态。这在分布式系统中是经典方案，但在
agent 场景下迅速失败。Agent 持锁太久、忘记释放、非法操作锁。20 个 agent
的吞吐量退化到 1-3 个。更深层的问题是：没有层级结构时，agent
变得风险厌恶，回避困难任务，只做安全的小改动。没有人为困难问题负责。

**第二次：Planner-Executor-Worker-Judge
流水线（部分成功）。** 分离角色带来了明显改善：Planner
制定计划，Executor 监督执行，Worker 专注具体任务，Judge
决定是否继续。但这个结构太刚性，被最慢的 Worker
瓶颈。前置规划也让系统难以在发现新问题时动态调整。

**第三次：Continuous Executor（部分成功后退化）。**
去掉独立的 Planner，让 Executor 同时承担规划和执行。系统变得更灵活，但
Executor
开始出现病理行为：随机休眠、停止生成任务、自己动手写代码、声称过早完成。原因是给它太多角色（规划、探索、研究、生成任务、检查
Worker、审查代码、合并输出、判断是否完成），它被压垮了。

**第四次：递归 Planner + 独立 Worker（最终方案）。** 根
Planner 拥有整个项目范围，当它认为自己的范围可以细分时，生成子
Planner，递归进行。Worker 从 Planner 接收任务，在自己的 repo
副本上工作，完成后写一份
handoff（包含做了什么、发现了什么、有什么担忧）提交给请求任务的
Planner。Worker 之间互不感知，也不与其他 Planner 通信。

### 3.3 关键洞察

**允许一定的错误率，换取整体吞吐量。** 当他们要求每次
commit 100% 正确时，系统陷入了严重的序列化和减速。一个小错误（API
变更、拼写错误）会导致整个系统停滞，Worker
跑到自己的范围之外去修不相干的东西。他们发现接受一个小而稳定的错误率是更好的策略：错误产生后很快被其他
agent
修复，系统维持在一个”不完美但稳定”的状态。最终可能需要一个独立的”绿色分支”做发布前的修复遍历。

**指令比 harness 更重要。**
一个反直觉的发现：系统行为中最重要的因素不是架构设计，而是给 agent 的
prompt。指令中的模糊措辞会被无限放大。“spec implementation”导致 agent
去实现冷门特性而非优先处理核心功能。“generate many
tasks”只产生少量任务，而”generate 20-100
tasks”才能传达出真正的意图。约束比指令更有效：“no TODOs, no partial
implementations”比”remember to finish implementations”更好用。

**项目架构影响 token 吞吐量。** 数百个 agent
同时编译会导致巨大的磁盘 I/O，成为真正的瓶颈。后来一次运行将 repo
重构为多个独立的 crate（从 monolith
迁移），编译等待时间大幅缩短，吞吐量成倍提升。这意味着项目结构的选择不仅影响人类开发者体验，也影响
agent 的工作效率。

**简单系统胜过复杂系统。**
他们最初尝试了分布式系统和组织设计中的各种方案，最终的系统出人意料地简单。他们试图加入一个
Integrator 角色做中央质量控制，结果它变成了瓶颈：数百个 Worker
都要通过一个门才能合并代码。最终移除了 Integrator，让系统自然收敛。

## 4. 交叉分析：两条路径的收敛与分歧

### 4.1 共同的结论

OpenAI 和 Cursor 从不同方向出发，收敛到了几个共同结论。

第一，**人类的核心工作是环境设计，不是代码编写**。OpenAI
把这表述为”设计环境、指定意图、构建反馈循环”，Cursor
把这表述为”架构和指令比 harness
更重要”。两者都发现人类的杠杆点不在于直接产出代码，而在于创造让 agent
能可靠工作的条件。

第二，**知识必须版本化、可发现、结构化**。OpenAI
强调”Codex 看不到的等于不存在”，Cursor
发现”指令中的模糊措辞会被无限放大”。两者的解决方案都是把知识推入
repo，用 markdown 和结构化文档取代口头沟通和外部工具。

第三，**完美主义是吞吐量的敌人**。OpenAI
采用最小阻塞合并、后续修复的策略。Cursor 发现要求 100%
正确性会导致系统停滞，接受小而稳定的错误率反而更高效。两者都接受了”纠错比等待便宜”的权衡。

第四，**角色分离和架构约束是规模化的前提**。OpenAI
通过分层架构和自定义 linter 强制约束。Cursor 通过递归 Planner-Worker
分离实现线性扩展。两者都发现，没有结构的 agent
群体会退化为风险厌恶的、低效的状态。

### 4.2 路径差异

两者的核心差异在于人类参与的模式。

OpenAI
的模式是**人类持续参与的协作**。三到七名工程师每天与 Codex
交互，通过 prompt 描述任务，审查（或不审查）PR，持续将品味和判断编码进
repo。人类的注意力是稀缺资源，但人类始终在循环中。这更接近现实中的团队使用场景。

Cursor
的模式是**人类设定目标后的自主运行**。给出一个初始指令（“构建一个
web
浏览器引擎”），然后系统自主运行一周，无需人类干预。人类的参与集中在实验开始前（编写指令、设计架构）和结束后（评估结果）。这更接近一个研究实验，测试
agent 自主性的上限。

Cursor 的实验也揭示了一个 OpenAI
文章中提到但没有深入的问题：**模型选择对角色的影响**。Cursor
发现 GPT-5.2 在长时间自主运行中表现优于 Opus
4.5（后者倾向于提前停止、走捷径）。不同模型适合不同角色：GPT-5.2
是更好的 Planner，即使 GPT-5.1-Codex 是专门训练用来写代码的。这意味着
harness engineering 的一部分工作是为不同角色匹配不同模型。

## 5. 业界更广泛的响应

Harness engineering 不是孤立的概念。2026
年初，多家公司从不同角度论述了类似的主题。

**Vercel** 通过 AGENTS.md 的实证研究（2026-01-27）验证了
OpenAI 的理论。他们发现被动上下文（AGENTS.md
自动注入）的表现系统性地优于主动检索（skills 机制），因为前者消除了
agent 的决策负担。Vercel 还提出了”self-driving infrastructure”的概念，把
harness engineering 从代码层扩展到了基础设施层：agent
不仅写代码，还监控生产环境并自动生成改进 PR。

**Anthropic** 通过大规模实证研究（2026-02-18）提供了
agent 自主性的量化数据。他们发现 Claude Code 的 99.9 百分位数 turn
时长在六个月内从 25 分钟增长到 45 分钟，说明 agent
承担的任务复杂度在持续上升。一个反直觉的发现是：经验丰富的用户的中断率反而更高（从
5% 升至 9%），因为他们采用的是主动监控而非被动审批。

Anthropic 在 2025 年 12 月对 132 名内部工程师的调查还揭示了 harness
engineering 的人力侧面：工程师自报生产力提升了
50%，但同时对自己几年后的角色感到不确定。27% 的 Claude
辅助工作是原本不会做的（修复”papercuts”、探索性工作），说明 AI
不仅放大了已有能力，还扩展了工作的边界。

**OpenAI Agents SDK**
团队的实践（2026-03-09）提供了一个更接地气的案例。他们用 Codex 维护
Python 和 TypeScript 两个 SDK repo，通过 repo-local skills、AGENTS.md 和
GitHub Actions 把重复工作（验证、发布准备、集成测试、PR
审查）编码为可重复的工作流。三个月内合并的 PR 从 316 增加到
457。他们的经验是：对于常规程序错误、回归和缺失测试，Codex
作为必需的审查路径已经”足够安全”（safe enough in practice）。

## 6. 实践启示

### 6.1 核心原则的总结

从 OpenAI 和 Cursor
的实践中，可以提炼出几条适用于大多数团队的原则：

**文档驱动开发**：把知识从口头沟通和外部工具推入
repo，用结构化文档取代隐含知识。这不仅帮助
agent，也帮助新成员入职和长期维护。

**约束优于指令**：用 linter、架构规则、不变量来约束
agent
行为，比用自然语言描述”应该怎么做”更有效。约束是可执行的，指令是可解释的。

**角色分离**：无论是 OpenAI 的分层架构还是 Cursor 的
Planner-Worker 模式，核心思想都是让每个 agent
有明确的职责范围，避免风险厌恶和责任模糊。

**容错优先**：在高吞吐量环境中，纠错比预防更经济。接受小而稳定的错误率，用后续修复替代阻塞式门控。

**指令精确性**：prompt
中的模糊措辞会被无限放大。用约束替代指令（“no TODOs”优于”remember to
finish”），用具体数字替代模糊描述（“20-100 tasks”优于”many
tasks”）。

### 6.2 可以借鉴的方向

从这些实践中，有几个值得借鉴的方向：

**结构化的质量评分体系**。OpenAI 维护一个 quality
document
对每个产品域和架构层打分，追踪质量随时间的变化。这种持续量化追踪能帮助识别技术债积累的早期信号。

**自动化的知识库维护**。OpenAI 有定期的 doc-gardening
agent 扫描过期文档，用 CI
验证文档的时效性和交叉引用。文档更新不再依赖人工触发。

**可观测性作为 agent 反馈回路**。OpenAI 为 Codex 接入了
Chrome DevTools
和完整的可观测性栈（日志、指标、追踪）。这让像”确保启动时间低于
800ms”这样的高层目标变得对 agent 可执行。

**约束的机械化执行**。OpenAI 用自定义 linter
强制执行架构不变量，linter 的错误信息本身就是给 agent
的修复指引。常见的工程约束（命名规范、文件组织、依赖方向）可以建立类似的自动化检查。

### 6.3 需要警惕的

Harness engineering
的叙事可能给人一种”一切皆可自动化”的印象，但两篇文章中都有重要的限定。OpenAI
坦言”我们还不知道在完全由 agent
生成的系统中，架构一致性如何在多年尺度上演化”。Cursor 坦言”multi-agent
coordination remains a hard problem”，他们的系统还远没有达到最优。

更根本的一点是：OpenAI 的实验是在一个从零开始的绿地项目上进行的，repo
从第一天起就针对 agent
可理解性优化。现实世界中的大多数代码库是遗留系统，充满了隐含知识、非正式约定、技术债。把这些代码库改造为
agent-legible 的成本和路径，两篇文章都没有讨论。

Anthropic 的工程师调查中另一个值得注意的信号是：随着 AI
使用率上升，同事间的协作和导师制在减少。Claude
变成了第一个被问的对象。如果深层技能因为缺乏练习而萎缩，而”监督 agent
恰恰需要这些正在萎缩的技能”，这就形成了一个悖论。Harness engineering
让人类的工作变得更高层，但也让人类更难在低层保持手感。这个张力尚未解决。

## 参考来源

1. Ryan Lopopolo, “Harness engineering: leveraging Codex in an
   agent-first world”, OpenAI, 2026-02-11.
   https://openai.com/index/harness-engineering/
2. Wilson Lin, “Towards self-driving codebases”, Cursor, 2026-02-05.
   https://cursor.com/blog/self-driving-codebases
3. Wilson Lin, “Scaling long-running autonomous coding”, Cursor,
   2026-01-14. https://cursor.com/blog/scaling-agents
4. Vercel, “AGENTS.md outperforms skills in our agent evals”,
   2026-01-27.
5. Anthropic, “Measuring AI agent autonomy in practice”,
   2026-02-18.
6. Anthropic, “How AI is transforming work at Anthropic”,
   2025-12-02.
7. Kazuhiro Sera, “Using skills to accelerate OSS maintenance”, OpenAI
   Agents SDK, 2026-03-09.
8. OpenAI, “A Practical Approach to Verifying Code at Scale”,
   2025-10.

## 相关阅读

- [Harness
  Engineering 在讨论什么：三个 Scaling 维度的统一框架](https://yage.ai/share/harness-engineering-scalability-20260330.html) —
  本调研的概念演化：为 Harness Engineering 建立时间、空间、交互三个
  Scaling 维度的统一框架
- [Everybody
  Talks About It, Nobody Knows What It Is — Harness Engineering
  到底是什么](https://yage.ai/share/harness-demand-side-analysis-20260420.html) — 从需求侧重新审视 Harness Engineering
  的定义边界与实际落地挑战
- [Harness
  的标准化：一个不会到来的标准](https://yage.ai/share/harness-canonical-form-20260418.html) — Harness Engineering
  标准化的可能性与局限：为什么统一标准难以形成

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
