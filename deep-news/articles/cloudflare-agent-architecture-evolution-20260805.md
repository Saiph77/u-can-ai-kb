---
title: "从代码类到共享工作区：Cloudflare 的两次转向与 Agent\n上下文演进"
date: 2026-08-05
source: https://yage.ai/share/cloudflare-agent-architecture-evolution-20260805.html
slug: cloudflare-agent-architecture-evolution-20260805
lang: zh
---
# 从代码类到共享工作区：Cloudflare 的两次转向与 Agent 上下文演进

发布于 2026 年 8 月 5 日 · [查看原网页](https://yage.ai/share/cloudflare-agent-architecture-evolution-20260805.html)

在大多数开发者的观念里，Cloudflare 依然被归类为一家传统的 CDN、DDoS
防护和域名服务商，似乎与最新的 AI Agent
架构没有太多交集。但如果关注它最近在 AI
领域的动作，会发现它连续发布了一系列重要基础设施，包括专注智能体沙盒交互的
Think（`@cloudflare/think`，其原有 Workspace 由
`@cloudflare/shell` 提供）以及最近上线的 [Cloudflare
Computer](https://blog.cloudflare.com/cloudflare-computer/)。这些发布提供了一个绝佳的契机，让我们看到 Cloudflare
正在逐渐意识到一个核心事实：**上下文（Context）是决定 AI
到底好用还是说废话的关键因素。** 纵观 Cloudflare
过去九年的产品探索，它正是在不断朝这个方向靠拢。

*Cloudflare 从 isolate 到 sync 的四步 context 演化*

Cloudflare 从 isolate 到 sync 的四步
context 演化

## 给 Web 边缘盖的房子，成了 Agent 的物理土壤

2017 年 9 月 Cloudflare 发布边缘计算服务 Workers 时，行业普遍采用
Docker 容器或轻量虚拟机作为 Serverless 的载体，但 Cloudflare 选择了基于
Google 开源的 V8 JavaScript
引擎中的隔离区（Isolate）作为服务端计算运行时。一个 V8 Isolate
是引擎内部独立的堆内存与执行上下文，相比启动需要数百毫秒、内存占用几十兆的容器，Isolate
的启动延迟低于 5
毫秒，内存开销只有几兆，可以在单个服务端进程内同时安全运行上万个租户的代码。当时这一选型是为了让开发者在边缘节点免费改写
HTTP 请求，却无意中确立了 Agent
运行时的第一条物理法则，即计算单元应当是极轻量且随时可丢弃的。

然而纯粹无状态的 Isolate 无法承载多轮对话与复杂长任务。2020 年 9 月
Cloudflare 推出了 Durable Objects，每一个 Durable Object
是全局唯一的单线程 JavaScript
对象实例，并且拥有专属于自己的强一致持久化存储。原本为了解决 WebSocket
实时聊天和多人协同编辑的单线程协调机制，意外为未来的 Agent
提供了全局唯一的物理身份与强一致的私有状态。2024 年 9 月起，Durable
Objects 进一步内置了嵌入式 SQLite，让每个对象都拥有一个最高 10GB
的关系型数据库，Agent
的持久状态从此有了原生归宿。九年前为了边缘网页加速盖的房子，在无意间拼好了
Agent
物理底座的两块基石，一个是极低成本的可丢弃计算，另一个是附着在对象身上的持久化状态。

## 第一次转向：把 Agent 写成一个简单的代码类

当大语言模型爆发后，Cloudflare 在 2025 年 2 月正式发布了官方的 Agents
SDK。在这一阶段，团队对 Agent 的认知非常直观：既然 Durable Objects
拥有物理身份与专用的 SQLite
数据库，那开发者只需要写一个普通的代码类（比如继承自 Agent 的
Class），就能轻松造出一个智能体。

这种写法的直觉体验非常好。就像前端开发者写一个网页组件一样，你在这个
Class 里通过 `setState`、`sql` 等 API
写入用户聊过的话，平台会按稳定标识把每个用户或任务路由到独立的 Durable
Object 实例，状态跨重启保留。但在应对真实复杂工程时，这种把 Agent
抽象为代码类的机制暴露出一个明显的缺陷：**原始 Agents SDK
不内建经验提炼、技能晋升或规则回写闭环，需要上层应用或 harness
自行实现。**

一方面，数据虽能以任意结构持久化在对象私有的 SQLite
里，但开发者仍需自行查询、选择、压缩并投影到模型上下文。正如在[Agent
文件系统：从“喂给模型记忆”到“让模型自己翻文件”](https://yage.ai/share/agent-filesystem-survey-20260507.html)中所探讨的，大语言模型在训练时最擅长的是
Shell
命令行和文件系统。面对数据库里的表格，应用层必须手写大量代码去查询并将结果拼接进
Prompt，不仅繁琐，模型也没法按需自查。另一方面，这个代码类运行在受限的边缘环境里。当
Agent 需要编译代码、跑 Python
脚本或运行重型测试时，边缘环境支撑不了；而如果把任务扔给外部 Linux
容器，对话记忆又留在代码类里，两者无法顺畅同步。

## 什么是真正能自我进化的上下文？

面对代码类和数据库表的局限，我们需要厘清真正能让 AI 持续进化的[Context
Infrastructure](https://yage.ai/context-infrastructure.html)到底长什么样。正如在[一个不等你提问的
ChatGPT，会是什么样？](https://yage.ai/share/proactive-ai-context-infrastructure-20260714.html)中所指出的，AI
要从被动的回答工具变成主动解决问题的助手，核心就在于上下文的组织方式。

**首先，文件是 AI 记忆的最自然载体。**
人类程序员是如何积累经验的？不是把所有规则硬背在脑子里，也不是存进复杂的数据库表里，而是把文档、源代码和操作规则整理进文件夹。对于大模型来说，文件系统也是最自然的记忆界面。

**其次，AI 需要通过修改文件来实现自我进化。**
真正能自我进化的上下文，通常由三个清晰的层级构成： 1.
**原始观察与日志（Contexts）**：记录 Agent
在执行任务时的具体动作、工具输出与报错信息； 2.
**模块化的技能指南（Skills）**：按需装载的操作手册，指导
Agent 如何使用具体工具； 3.
**沉淀的原则与规则（Rules）**：当 Agent
遇到错误或收到人类纠正后，将教训提炼成持久的规则文件改写回去。

当下一个任务启动时，Agent
只需要先读取规则文件，就能直接避免重犯同样的错误。这为 Agent
运行时指明了方向：最核心的不是给开发者提供写 Agent
的代码框架，而是提供一个以文件为载体的上下文环境，并让这个环境能在不同机器和容器之间无缝流转。

## 第二次转向：给 Agent 一个跨机器同步的共享文件夹

基于这一认知，Cloudflare 在 2026 年迎来了第二次转向：在 Agents SDK 与
Think 之外增加了一层可组合的共享 Workspace 与多后端执行抽象，给 Agent
分配一个可以在不同机器之间按需同步的共享工作文件夹。

2026 年 4 月推出的 Think
率先作出了改变，它在持久化对象之上建立了虚拟文件系统，让模型可以直接使用
read、write、edit 和 ls 等工具像程序员一样翻看文件。同年 8 月发布的 [Cloudflare
Computer](https://blog.cloudflare.com/cloudflare-computer/)
则进一步把这个文件夹独立出来，实现了跨执行后端的双向增量同步。

具体来说，当你在轻量的边缘 Worker 节点里写入一个 Bug
报告文件时，后台守护进程会在执行命令前后或显式调用时，把文件变更切成 512
KiB 的内容寻址小块，增量同步到重型 Linux
容器里的工作目录。当容器运行代码并产生几十兆的测试日志时，这些日志文件又会在执行结束后按块同步回来。Agent
根本不需要把几十兆的日志全部塞爆 LLM
的上下文窗口，而是直接在共享文件夹里用 grep
搜出报错的那两行。上下文从此不再是 Prompt
里的长文本，而是变成了一个能跨越不同执行后端按需同步的真实文件夹。

## 从基础设施到自我进化：如何真正用好 Computer？

理解了 Cloudflare
的演进历程后，我们需要厘清一个关键迷思：**使用了 Cloudflare
Computer，并不代表你的 AI 就会奇迹般地自我进化。**

Cloudflare Computer 是建立在 Durable Objects、Dynamic Workers 和可选
Containers
之上的开源库，提供虚拟文件系统与多后端执行编排，完成了文件的跨后端同步与挂载。它解决了物理层的储存与流转问题，但并没有解决心智层的进化问题。

要让 Agent
真正走向自我进化，关键在于开发者如何在这个共享文件夹之上构建[Context
Infrastructure](https://yage.ai/context-infrastructure.html)： -
**建立文件层级**：将操作规则、工具技能与历史日志分层组织在共享文件夹中，让模型通过路径按需读取；
- **建立反思回写闭环**：正如在[为什么智能体需要上下文治理](https://yage.ai/share/context-governance-agent-runtime-20260707.html)所警示的，如果只是让文件跨机器同步，而不设计机制让
AI
自动扫描日志、提炼教训并修改规则文件，长期运行的文件夹依然会退化为杂乱的垃圾目录。

对于 Agent
架构师而言，未来的分工非常明确：不用在底层重复造物理同步的轮子，将文件传输与机器同步交给
Cloudflare 这样的物理设施，把核心精力放在设计让 AI
自我进化的上下文治理与规则闭环上。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
