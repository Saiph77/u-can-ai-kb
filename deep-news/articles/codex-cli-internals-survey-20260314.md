---
title: "Codex CLI 内部实现解析：一个 Production-Grade Agent\n客户端是怎么造的"
date: 2026-03-14
source: https://yage.ai/share/codex-cli-internals-survey-20260314.html
slug: codex-cli-internals-survey-20260314
lang: zh
---
# Codex CLI 内部实现解析：一个 Production-Grade Agent 客户端是怎么造的

发布于 2026 年 3 月 14 日 · [查看原网页](https://yage.ai/share/codex-cli-internals-survey-20260314.html)

> 日期：2026-03-14 核心来源：OpenAI “Unrolling the Codex agent loop”
> (Michael Bolin, 2026-01), OpenAI “Unlocking the Codex harness” (Celia
> Chen, 2026-02), The Pragmatic Engineer “How Codex is built” (Gergely
> Orosz, 2026-02) 补充来源：Zenn 源码分析系列 (takiko), ZenML 架构案例,
> Blake Crosley 架构对比, Ars Technica 技术报道, InfoQ App Server 报道,
> Morph harness 对比, Reddit 社区观察 关联：[Harness
> Engineering 调研](https://yage.ai/share/harness-engineering-survey-20260312.html)

> Codex CLI 最值得学的不是 Rust 代码本身，而是一整套 production-grade
> agent 客户端的设计取舍。 它把 agent loop、prompt 组装、sandbox 和 app
> server 拆成了清晰分层。 真正有复用价值的是这些
> trade-off，而不是照抄实现。

## 1. 为什么值得拆

2026 年初，三大 coding agent（Codex CLI、Claude Code、Gemini
CLI）呈三足鼎立之势。三者中，Claude Code 完全闭源，Gemini CLI 用
TypeScript 开源但文档较薄，只有 Codex CLI 做到了”核心逻辑全开源 +
官方工程师写技术博客系列解析”。仓库地址
github.com/openai/codex，截至本文写作时有 4,547 commits，Rust
实现，Apache 2.0 协议。

这不仅仅是一个”可以看看代码”的程度。OpenAI 工程师 Michael Bolin 和
Celia Chen 分别撰写了关于 agent loop 和 App Server 协议的深度博客，The
Pragmatic Engineer 对 Codex 团队负责人 Thibault Sottiaux
做了访谈，日本开发者 takiko 在 Zenn
上发表了逐函数的源码分析。这些材料加在一起，使得 Codex CLI
成为目前可考察的、文档化程度最高的 production-grade AI agent
客户端实现。

对于正在构建或定制 AI agent 工具链的团队来说，Codex CLI
的价值不在于直接复用它的代码（Rust 的门槛和 OpenAI API
的绑定都是限制），而在于它暴露了一组具体的、经过生产验证的设计决策。这些决策背后的
tradeoff，比代码本身更值得学习。

## 2. 整体架构：四层堆叠

Codex CLI 的架构可以理解为四层堆叠，每层有明确的职责边界：

**表面层**负责接入。TUI（终端界面）、App Server（供 IDE
和 Web 调用的 JSON-RPC 服务）、MCP Server（供其他 agent 调用）、SDK（供
CI/CD
和脚本调用）都是表面层的不同实现。它们共享同一个核心，只是交互模式不同。

**会话层**负责状态。Thread
的创建、恢复、fork、归档，配置的加载和切换，认证流程（包括 ChatGPT OAuth
登录），都在这一层处理。Celia Chen 的博客称之为 “the full agent
experience beyond the core loop”。

**核心层**是 agent loop 本身，位于
`codex-rs/core/`。这是整个系统的心脏：接收用户输入，组装
prompt，调用模型，处理 tool call，管理 context window。所有 Codex
体验（CLI、Web、VS Code、macOS
App、JetBrains、Xcode）共享这同一个核心。

**执行层**负责实际操作：sandbox 隔离、shell
命令执行、文件编辑、MCP tool 调度。

这个分层的关键特征是**核心层不知道自己在哪种表面层中运行**。`codex-rs/core`
是一个纯 Rust 库，通过 async channel 和事件协议与外界通信。TUI
是它的一个消费者，VS Code 插件也是，Web 也是。这个解耦使得 OpenAI
可以在不改动核心逻辑的情况下，快速为新平台构建 Codex 体验。

## 3. Agent Loop：事件驱动的三层状态机

### 3.1 两条 Channel

根据 takiko 的源码分析，`codex-rs` 的 agent loop
采用了事件驱动架构，两条异步 channel 是它的循环系统。

Submission channel 从客户端流向
session，传递用户操作（`Op`）。当 TUI
收到键盘输入时，它把内容包装成 `Op::UserInput` 发到这条
channel。

Event channel 从 session 流向客户端，分发事件。AI
响应的文本片段、tool call 的执行结果、错误通知，都通过这条 channel 到达
TUI（或其他客户端）进行渲染。

这个双 channel 设计的好处是天然异步：用户可以在 agent
还在执行时继续输入（比如取消操作），session 可以在不阻塞 UI
的情况下执行长时间的 tool call。

### 3.2 三层嵌套循环

Agent loop 本身是三层嵌套结构。

最外层是 `submission_loop`，一个持久运行的无限循环，等待
`Op` 并分发处理。它一直运行直到收到
`Op::Shutdown`。除了 `UserInput`，它还处理
`UserTurn`（用户在 agent
工作结束后继续对话）等其他操作类型。

中间层是 handler 调度。当 `submission_loop` 收到
`Op::UserInput` 或 `Op::UserTurn` 时，调用
`handlers::user_input_or_turn`，启动一轮对话。

最内层是 turn
loop，这是单轮对话的核心循环。它做的事情概括来说是：组装 prompt → 调用
Responses API（流式）→ 处理 stream events。如果模型输出了一个
`function_call` 类型的 event，就执行对应的 tool，把结果拼回
prompt，再次调用 API。如果模型输出了一个纯文本的 assistant message（没有
tool call），就认为这一轮完成，把控制权交还给用户。

一个重要的特征是：**单轮内的 inference ↔︎ tool-execution
循环次数没有硬性上限**。Agent 可以在一轮中执行数十甚至数百次 tool
call，直到它自己决定任务完成。这意味着 context window 管理成为 agent
loop 的核心职责之一。

### 3.3 模型推理：Stateless 设计

Codex CLI 向 Responses API 发送 HTTP
请求来执行推理。一个关键设计决策是：**每次请求都发送完整对话历史，不使用
`previous_response_id` 参数**。

Bolin 在博客中解释了这个选择。Responses API 提供了一个可选的
`previous_response_id`
参数，允许服务端存储对话状态，客户端只需发送增量。Codex
没有使用它，原因有三：简化 API provider 侧的实现复杂度、更容易支持 Zero
Data Retention（不在服务端存储用户数据）、更容易适配非 OpenAI 的
provider（任何实现了 Responses API 的 endpoint 都能用）。

代价显而易见：随着对话增长，每次请求的 token 数持续膨胀。这直接导致了
compaction 机制的必要性。

### 3.4 Context Window 管理与自动 Compaction

当 token 数超过阈值时，Codex 自动触发 compaction。具体实现在
`codex-rs/core/src/context_manager` 模块中。这个模块负责将
tool call 和输出配对、截断过大的 payload，然后调用一个专门的 API
endpoint 来压缩历史。压缩后的内容以 encrypted content item 的形式保留在
prompt 中，模型可以从中恢复对之前工作的”理解”。

早期版本需要用户手动执行 `/compact`
命令。当前版本完全自动化，用户无感。

值得注意的是，Ars Technica 的报道指出这个 compaction 机制依赖 OpenAI
的专用 API endpoint。如果用 `--oss` 模式接
Ollama，这个功能可能不可用。这是 stateless
设计的一个隐含代价：虽然理论上 provider-agnostic，但某些高级功能仍然和
OpenAI 的基础设施耦合。

## 4. Prompt 组装：层叠式指令注入

每次调用模型前，Codex 会组装一个包含多层信息的
prompt。理解这个组装过程是理解 Codex 行为的关键。

ZenML 的案例分析详细梳理了组装顺序。最先注入的是 system
prompt，这是硬编码在客户端中的身份定义，告诉模型”你是 Codex
CLI，一个基于终端的编码助手”。takiko 的源码分析还原了这段 prompt
的内容，包括可用操作列表（接收用户 prompt、流式响应、执行 shell
命令、应用补丁、在 sandbox 中工作等）。

接下来是可选的 developer instructions，来自用户的
`config.toml`。然后是层叠式的用户指令：系统从
`$CODEX_HOME` 目录开始，沿着从 git root
到当前工作目录的路径，依次读取每一层的 `AGENTS.md` 和
`AGENTS.override.md`。更具体的指令覆盖更通用的指令，总量受 32
KiB 默认上限约束。如果配置了 Skills，skill 的内容也在这个阶段注入。

然后是工具列表。Codex 的工具分三类：内置 tools（shell
执行、文件编辑）、API 返回的 tools、MCP servers 暴露的
tools。三类工具统一列在 prompt 的 tools
字段中，模型在推理时自主选择使用哪些。

最后是环境上下文（文件树、git 状态）和完整的对话历史。

这个层叠设计和 harness engineering
调研中的一个核心发现直接对应：“AGENTS.md
应该是目录，不是百科全书。”Codex 的 prompt 组装机制通过 32 KiB
上限和路径层叠，天然地鼓励用户把信息分散到目录结构中，而非堆在一个巨大文件里。这是在系统层面执行了
harness engineering 的最佳实践。

## 5. Sandbox：内核级隔离

Codex 的 sandbox 设计是它和 Claude Code
最根本的架构差异，也是最能体现设计哲学差异的地方。

### 5.1 实现机制

在 macOS 上，Codex 使用 Seatbelt（Apple 的沙箱框架，和 App Store
应用的沙箱技术是同一套）来限制 agent 生成的进程。在 Linux 上，使用
Landlock +
seccomp（内核级的访问控制和系统调用过滤）。这意味着限制发生在操作系统层面，agent
的代码无法通过应用层手段绕过。

`codex-rs/core/src/protocol.rs` 中定义了一套
`SandboxPermission`
枚举：`DiskFullReadAccess`（可以读任何文件）、`DiskWriteTempOnly`（只能写临时目录）、`NetworkFullAccess`（可以访问网络）等。这些权限组合成三个预设模式：`read-only`（只读）、`workspace-write`（可写工作目录）、`danger-full-access`（完全访问）。

### 5.2 和 Claude Code 的对比

Blake Crosley 的架构对比文章对这个差异做了精准总结。Codex 的 sandbox
在内核层面拒绝
syscall，逃逸难度高，但可编程性低（只能选择预设模式，不能写自定义规则）。Claude
Code 用应用层的 hooks（17 种生命周期事件类型），逃逸难度中等（hooks 和
agent 共享进程边界），但可编程性高（hook 里可以跑任意 bash 或
Python）。

这个 tradeoff 反映了两种不同的安全哲学。Pragmatic Engineer
的访谈中，Codex 团队负责人 Tibo 说了一句很直接的话：“We take a stance
with the sandboxing that hurts us in terms of general adoption. However,
we do not want to promote something that could be unsafe by
default.”

换言之，Codex 选择了”安全但不灵活”，Claude Code
选择了”灵活但需要用户自己负责安全”。对于安全敏感的场景（金融、医疗、政府），Codex
的 approach 更有说服力。对于需要高度自定义审批逻辑的场景，Claude Code 的
hooks 更强大。

### 5.3 一个值得注意的安全缺口

OpenCode 社区的一篇分析文章（“Building Sandboxes into
OpenCode”）指出了 Codex sandbox 的一个已知弱点：MCP servers 作为 child
process 在 sandbox 外启动。这意味着如果恶意的 MCP server
被配置进来，它可以绕过 sandbox 限制。Codex 的文档也承认了这一点：只有
Codex 内置的 tools 受 sandbox 保护，MCP tools 必须自行保证安全。

## 6. App Server：从 CLI 工具到平台的关键一跳

如果 agent loop 是 Codex 的心脏，App Server 就是它的血管系统。Celia
Chen 的博客讲述了这个组件的诞生背景。

### 6.1 为什么需要 App Server

Codex 最初只有 TUI。当团队要做 VS Code
插件时，面临一个选择：重新实现一遍 agent 逻辑，还是找一个方法复用 TUI
的核心。他们先尝试把 Codex 包装成 MCP server，但发现 MCP 的
request/response 语义不适合 agent 的复杂交互模式。Agent
需要流式推送进度、请求用户审批、展示 diff、中途被取消。这些都不是 MCP
协议设计时考虑的场景。

于是团队设计了一个专门的 JSON-RPC 双向协议，最初只是一个”unofficial
first version”给 VS Code 用。随着 macOS App、JetBrains、Xcode
陆续接入，这个协议逐渐成熟为正式的 App Server。

### 6.2 三个核心原语

App Server 的协议围绕三个原语构建。

**Thread**
是一次完整对话。它可以被创建、恢复、fork（从某个时间点分叉出新对话）、归档。Thread
的事件历史被持久化，客户端断线重连后可以从断点恢复渲染。

**Turn** 是一次用户请求及随后的 agent 工作。一个 Thread
包含多个 Turn。每个 Turn
在进行中会流式推送增量更新，客户端可以实时渲染进度。

**Item** 是最小的输入/输出单元。用户消息、agent
消息、命令执行、文件修改、tool call、审批请求，都是不同类型的 Item。每个
Item 有明确的生命周期（started → in-progress → completed/failed）。

这个三层原语设计的好处是：不同的客户端可以根据自己的 UI
能力选择不同的渲染粒度。VS Code 可以为每个 Item 渲染一个独立的 UI
卡片。TUI 可以把所有 Item 流式拼接成终端输出。Web 可以把每个 Turn
展示为一个可折叠的任务面板。协议相同，表现不同。

### 6.3 协议的开放性

App Server 的全部源码在 `codex-rs/app-server/`
中开源，文档包含了 TypeScript 和 JSON Schema 的 schema
生成工具。这意味着任何人都可以用任何语言构建 Codex 客户端。协议支持
STDIO 和 Streaming HTTP
两种传输方式，前者适合本地进程通信，后者适合远程部署。

这是 Codex 开源战略中最有价值的部分。IDE
插件闭源没关系，因为协议是开放的。你可以为 Emacs 写一个 Codex
客户端，为自研 IDE 写一个，甚至为 Slack bot 写一个。

## 7. 和 Harness Engineering 的关联

这篇调研和之前的 [harness
engineering 调研](https://yage.ai/share/harness-engineering-survey-20260312.html) 有直接的关联。Harness engineering
回答的是”人类如何为 agent 设计工作环境”，这篇回答的是”agent
客户端内部如何实现”。两者是同一个问题的两个视角。

### 7.1 Agent Loop 是 Harness 的运行时

Harness engineering 调研中，OpenAI 的 Ryan Lopopolo
描述的”环境设计”（文档体系、架构约束、反馈循环、验证工具），最终都要通过
agent loop 的 prompt 组装阶段进入模型的感知。AGENTS.md
在磁盘上只是一个文件，真正起作用的时刻是 Codex 的 context\_manager
把它读出来、拼进 prompt、送到 Responses API 的那一刻。理解 agent loop
的实现细节，能帮助 harness engineer 更精准地设计他们的环境。

比如知道了 32 KiB 的默认上限和路径层叠的优先级规则，harness engineer
就能做出更好的信息架构决策：把全局不变量放在 git root 的 AGENTS.md
中，把模块级细节放在子目录的 AGENTS.md 中，让 agent
自动获取最相关的上下文，而不是被一个巨大的全局文件淹没。

### 7.2 Sandbox 是 Harness 的信任边界

Harness engineering 调研中提到的 A04（可靠性是管理问题），在 sandbox
的设计中有最直接的工程对应。Tibo 的那句”we take a stance that hurts us
in terms of general
adoption”，本质上是在说：可靠性的代价是灵活性，但这个代价值得付出。

Codex 的三档 sandbox 模式（read-only / workspace-write /
full-access）和 Codex 的 profile 系统组合，让 harness engineer
可以为不同的任务类型定义不同的信任级别。一个 `careful`
profile 搭配 read-only sandbox，适合让 agent 做代码审查。一个
`fast` profile 搭配 workspace-write sandbox，适合让 agent
快速迭代。这就是 A04 中”信任光谱”的具体工程实现。

### 7.3 App Server 是 Harness 的可扩展性基础

Harness engineering 调研中提到的”可观测性作为杠杆”（OpenAI 接入
Chrome DevTools 和可观测性栈让 Codex
能自主检查产出质量），这类能力的底层依赖就是 App Server
协议的扩展性。因为协议支持任意类型的 Item
和自定义事件，新的可观测性工具可以作为 MCP server 或自定义 tool 接入
agent loop，而不需要修改核心代码。

这也解释了为什么 OpenAI 选择开源 App Server 协议而闭源 IDE
插件：协议层的开放能吸引社区构建更多 harness 工具（lint 集成、metrics
集成、custom reviewer），而 IDE 插件只是众多可能的 UI 表面之一。

## 8. 对定制者的实用评估

基于以上分析，对想要基于 Codex CLI
构建自定义工具链的团队，做以下评估。

**高度可定制的部分：**

AGENTS.md 和 Skills
的内容层面，定制空间接近无限。你可以把团队的编码规范、架构决策、安全策略、审查标准全部编码进去。Skills
的实现本质上就是在 prompt assembly 阶段拼入 markdown
文本，没有复杂的运行时机制，理解成本很低。

MCP
集成可以连接几乎任何外部系统。JIRA、Linear、Figma、Datadog、自研内部工具，只要有
MCP server 实现，就能接入 Codex 的 tool 体系。Codex 自身也可以作为 MCP
server 暴露给其他 agent，这让它可以被嵌入更大的编排系统。

App Server 协议的开放使得构建自定义客户端完全可行。如果你的团队有自研
IDE 或内部开发平台，可以直接对接这个协议，获得完整的 Codex agent
能力。

Config profile
系统允许为不同场景预设完整的配置快照（模型选择、sandbox
级别、审批策略），一行命令切换。

**中度可定制的部分：**

模型可以通过 `--oss` 参数切换到本地
Ollama，但实际效果高度依赖所选模型的 tool-calling
能力。截至目前，没有任何开源模型能接近 gpt-5.3-codex 或 codex-1
在编码任务上的表现。这意味着”换模型”在理论上可行，在实践中体验会有明显下降。

Agent loop 的核心逻辑可以通过 fork 仓库来修改，但 Rust
的学习曲线和编译复杂度是门槛。修改 system prompt、调整 compaction
阈值、添加自定义 tool handler 都是可行的，但需要深入理解
`codex-rs/core` 的异步架构。

**低度可定制的部分：**

Sandbox 的规则是内核级的，添加自定义 sandbox 策略需要理解
Seatbelt（macOS）或 Landlock/seccomp（Linux）的配置语法，门槛很高。

Compaction 机制依赖 OpenAI 的专用 API endpoint，换 provider
时可能失效。这是当前实现中 provider-agnostic
理想和实际依赖之间最明显的缝隙。

多 agent 编排在 CLI 层面仍是实验性的。真正的生产级并行 agent 协调需要
Codex Cloud 的能力，而那部分完全闭源。

## 9. Provider 兼容性：Codex CLI vs OpenCode 的 Harness 差异

### 9.1 同一个模型，不同的 Harness，不同的体验

“Harness
重要吗？同一个模型在不同的客户端里跑，结果会有多大差异？”这个问题已经有了来自社区的实证回答。

Reddit 上 r/opencodeCLI 有一个帖子标题是 “Opencode vs Codex CLI: Same
Prompt, Clearer Output”。作者用同一个 GPT-5.2 模型分别在 Codex CLI 和
OpenCode 中运行相同的 prompt，发现 OpenCode
的输出”解释得更清楚”，对话感觉”像在和 Claude 或 Gemini 聊天”，而 Codex
CLI 感觉”像在和机器人说话”。作者第二天补充说，用 OpenCode +
GPT-5.2-medium 做规划和讨论，体验”genuinely feels like working with
Opus, and sometimes even better”，他”不完全理解 OpenCode
是怎么做到的”。

Morph 的基准测试提供了更量化的数据。在相同任务上，Codex
CLI（GPT-5）完成跨文件重构用 2 分 45 秒，OpenCode（Claude）用 4 分 20
秒。但在测试生成任务上，OpenCode 产出了 94 个测试，Codex 只有 73
个。速度和深度之间存在 tradeoff。

更广泛的行业数据也支持”harness 影响结果”这个结论。SWE-bench Verified
的评测中，Augment 的 Auggie、Cursor、Claude Code 三个产品都跑的 Opus
4.5，但 Auggie 比 Claude Code 多解决了 17 个问题（总共 731
个）。同一个模型，不同的 scaffolding，可测量的差异。

### 9.2 差异的根源：System Prompt 和 Tool Schema

差异来自哪里？核心在于两者的 system prompt 和 tool
定义的设计哲学不同。

Codex CLI 的 system prompt 是**针对 GPT-5.x
系列专门调优的**。它告诉模型”你是 Codex
CLI”，列出了精确的可用操作，定义了输出格式的约束。tool schema
的参数定义、描述文本、错误处理指引，都是围绕 GPT
模型的行为模式设计的。Morph 的分析称之为”vertical integration
play”：系统提示、工具定义和上下文策略针对 GPT-5.3
的行为特征做了专项优化。这在用 OpenAI 模型时表现最优，但当你换到其他
provider 时，这些优化变成了不匹配。

OpenCode 的 system prompt
是**通用的**。它不假设底层是哪个模型，用更宽泛的描述来定义
agent 行为。tool schema
的设计也更标准化。这意味着它在任何模型上都能”及格”，但在任何特定模型上都不如专门优化的方案。HN
上有一条评论精准地总结了这个取舍：“The great thing about basing a
workflow on a tool like OpenCode is that if OpenAI enshittifies Codex, I
don’t have to worry about being trapped and can easily pivot to an open
source model, or Anthropic via the API.”

### 9.3 Provider 兼容性的工程实现对比

两者在”怎么接第三方 provider”上的工程方案差异很大。

| 维度 | Codex CLI | OpenCode |
| --- | --- | --- |
| 支持的 provider 数 | 1 个原生（OpenAI）+ 自定义 | 75+ 原生 |
| 模型切换方式 | `config.toml` 里定义 `model_providers`，指定 `base_url` 和 `wire_api` | `opencode.json` 里配置 provider，或首次启动时交互式选择 |
| Wire API | `responses`（默认）或 `chat`（OpenAI-compatible） | 通过 AI SDK 的 provider 适配器自动处理 |
| 本地模型 | `--oss` 模式，需手动配置 Ollama/LM Studio 的 URL | Ollama 原生支持，配置更简单 |
| OAuth 集成 | ChatGPT 账号登录、GitHub Copilot token | ChatGPT Plus、GitHub Copilot、Google 等多种 OAuth |
| Claude 接入 | 需要 LiteLLM 代理做格式翻译 | 原生支持 Anthropic API key |
| Compaction | 依赖 OpenAI 专有 API，换 provider 后失效 | 不依赖特定 provider |

关键差异在 wire\_api 这个概念上。Codex CLI 有两种 wire
格式：`responses`（OpenAI 的 Responses API，功能完整但只有
OpenAI 支持）和 `chat`（标准的 OpenAI Chat Completions
API，兼容大量第三方 provider）。当你用 `chat` wire\_api
时，compaction、部分流式事件、某些 tool-calling 特性会降级。而 OpenCode
从设计上就用的是通用的 Chat Completions 协议，所以它在不同 provider
之间切换时不存在功能降级的问题。

换言之，Codex CLI 是”在 OpenAI 上体验最好，切换 provider
时功能会丢失”。OpenCode 是”在所有 provider
上体验一致，但没有针对任何一个做深度优化”。这和 Codex
的整体设计哲学一致：生产级、深度集成、为特定场景极致优化。OpenCode
的设计哲学则是：社区驱动、provider-agnostic、宁可均匀也不愿偏科。

### 9.4 架构上的根本差异

在更深的架构层面，两者的差异同样显著。

Codex CLI 是纯客户端架构：一个 Rust
二进制文件直接运行在你的机器上，直接调用模型
API。没有中间服务器。这意味着性能极好（启动快、内存占用低），但也意味着所有逻辑必须在客户端实现。

OpenCode 是 client-server 架构：一个 Go 后端（Hono HTTP
Server）运行在本地或远程，iOS/Web/桌面客户端通过 REST + SSE
连接。这个架构天然支持远程 session（在服务器上跑
agent，手机上看结果）、session
共享（生成链接给别人看你的对话）、多设备同步。

这个架构差异也解释了为什么 OpenCode 在第三方 provider
切换时”降级更小”：因为 provider
的适配逻辑在服务端，客户端完全不关心底层用的是什么模型。而 Codex CLI 的
provider 适配逻辑在客户端 Rust 代码里（`wire_api`
的选择、请求格式的组装、流式事件的解析），换 provider
时客户端必须正确处理格式差异。

从代码质量角度看，r/codereview 上的一项静态分析显示 Codex 的 Rust
代码每行 issue 数比 TypeScript 项目低 8 倍，但 OpenCode
作为一个更小团队的产品，在没有 linter
配置的情况下也保持了不错的基础质量。

## 10. 三个值得带走的设计模式

从 Codex CLI 的实现中，提炼三个可以迁移到其他 agent
系统的设计模式。

**模式一：核心逻辑和 UI 表面的严格解耦。**
`codex-rs/core` 作为纯库存在，不关心自己在哪种 UI
中运行。这让 OpenAI 能用同一个核心支撑 TUI、VS Code、Web、macOS
App、JetBrains、Xcode 六种表面。如果你在构建 agent 系统，从第一天就把
agent loop 做成库而非应用，后续扩展的成本会低很多。

**模式二：Stateless API 调用 + 客户端 compaction。**
放弃服务端状态意味着更简洁的 provider
依赖和更好的隐私合规，代价是更大的请求体积。用客户端侧的自动 compaction
来弥补。这个 tradeoff 对于想做 provider-agnostic
的工具特别有参考价值。

**模式三：三层原语的协议设计（Thread / Turn / Item）。**
这比 MCP 的 request/response 语义更适合 agent
的交互模式。如果你需要在多个客户端之间共享 agent
状态，这三层原语是一个经过生产验证的抽象层级。

## 11. 设计张力：五个值得追问的 Tradeoff

前面十节试图如实还原 Codex CLI
的内部实现。这一节换一个角度：把这些事实放到更大的设计决策语境里重新审视。以下每一个
tradeoff 都不是”Codex 做错了”，而是”Codex
做了一个押注，这个押注有成立的条件，也有失效的条件”。理解这些条件，比知道实现细节更有长期价值。

### 11.1 深度绑定 vs 水平兼容

第 9 节描述了一个事实：Codex 的 system prompt 和 tool schema 是针对
GPT-5.x 专门调优的，切换 provider
时会出现功能降级和”对话干涩感”。技术层面的解释是 wire\_api 和 compaction
的依赖。但这背后有一个更根本的设计押注：**OpenAI
相信深度绑定一个顶级模型比浅层兼容所有模型更有价值。**

这个押注在 OpenAI 模型保持领先时是对的。GPT-5.3-Codex 在
Terminal-Bench 上领先 Claude Code 近 12 个百分点，Codex
的垂直优化确实在自家模型上兑现了。但 AI
领域的竞争格局每半年就会重新洗牌。如果你选择了 Codex 并且围绕它的
AGENTS.md 格式、Skills 系统、App Server
协议构建了整套工作流，那么当需要切换 provider
的那一天到来时，你丢失的不仅是技术兼容性，还有和 GPT
之间积累的隐性默契：prompt 的措辞方式、tool call 的触发模式、context
管理的心智模型。这些东西很难量化，但切换时的”不顺手感”是真实的。

反观 OpenCode 的通用 prompt
设计。它在任何特定模型上都不如专门优化的方案，但它的”及格线”在所有模型上都差不多。更重要的是，用户在
OpenCode 里积累的工作习惯是 provider-agnostic
的，切换模型时几乎没有认知迁移成本。在一个领域的基础假设还在快速变化的阶段，这种灵活性本身可能就是最重要的能力。

### 11.2 过程安全 vs 结果验证

第 5 节详细拆解了 Codex 的内核级
sandbox：Seatbelt、Landlock、seccomp，三档权限模式。这是”过程安全”的极致实现，在操作系统层面限制
agent 能做什么。对比之下，Claude Code 的 hooks 系统和 OpenCode
更灵活的权限模型更偏向”结果验证”：不限制你怎么做，但验证你做完之后的产出是否满足标准。

这两种路径的差异比看起来更深。过程安全的优势是确定性：如果 sandbox
禁止了网络访问，那 agent 就绝对无法泄露数据，无论它的 prompt
被怎么注入。但代价是你必须提前枚举所有合法的操作模式。agent 需要做一件
sandbox 没预见到的事情时（比如临时访问一个新的 API endpoint 来验证一个
bug），你只能修改 sandbox 策略，而内核级策略的修改门槛远高于应用层
hooks。

从实际编码工作的角度看，大多数质量问题的检测靠的不是”agent
被阻止做了什么”，而是”agent 做完之后代码是否通过了
lint、测试、类型检查”。sandbox
能防止灾难性失败（删库、泄露密钥），但无法防止逻辑错误、性能退化、风格不一致。后者恰恰是日常编码中更频繁的问题。Codex
在过程安全上投入了重工程，但在结果验证上（相比之下）依赖的是模型自身的判断力和用户写在
AGENTS.md
里的验收标准。这个投资分配是否最优，取决于你的威胁模型里什么排第一。

### 11.3 生产级工程 vs 可修改性

第 2 节提到 Codex 从 TypeScript 重写为 Rust，动机是性能、安全、去
Node.js
依赖。这些收益是真实的。但每一项收益都同时引入了一个新的约束。

Rust 让启动速度和内存占用更优，但也让社区参与的门槛从”会写
TypeScript”变成”会写异步 Rust + 理解 Seatbelt/Landlock
的内核接口”。GitHub 上 Codex 的 contributor 数量远少于
OpenCode，部分原因就是语言门槛。内核级 sandbox 比应用层 hooks
更难逃逸，但也更难定制。App Server 协议的 Thread/Turn/Item 三层原语比
MCP 更适合 agent
交互，但任何想接入的客户端都必须理解并实现这三层语义，而 OpenCode 的
REST + SSE 接口几乎任何 HTTP 客户端都能直接调。

这是一个经典的张力：**让系统更强、更快、更安全的改进，往往同时让系统更难被外部修改。**
如果你的角色是 Codex
的使用者（按它设计的方式使用），这些改进全是好事。如果你的角色是构建者（想从
Codex
的设计中提取模式、做自己的系统），这些改进反而增加了理解和迁移的成本。

一个实用的应对策略是：不需要 fork 整个 Codex 来获取它的好设计。prompt
assembly 的层叠逻辑（32 KiB 上限 +
路径优先级）用几十行代码就能复刻。Stateless + compaction
的模式可以用任何语言实现。Thread/Turn/Item
的协议设计可以作为参考来设计你自己的更简单的版本。Codex
的价值作为学习材料，可能比作为可 fork 的代码库更大。

### 11.4 瓶颈在哪里

第 9.1 节引用了 Reddit 上的观察和 SWE-bench
的数据，证明同一个模型在不同 harness
里表现不同。这个事实已经确立。但一个更深的问题是：在一个编码 agent
系统中，**真正限制输出质量的瓶颈到底在哪里？**

如果瓶颈在模型智能，那 harness
的差异应该很小。但社区观察（同模型不同结果）和 SWE-bench 数据（同模型
Auggie 比 Claude Code 多解 17 题）都指向相反的结论：harness
对结果的影响比大多数人意识到的更大。

如果瓶颈在 harness，那具体在 harness 的哪个环节？Codex 在
sandbox、协议、性能上做了重度投资，但这些是 harness
的”基础设施层”。Reddit 用户感受到的差异（“对话干涩” vs “像和 Opus
合作”）指向的是 harness 的”交互层”：system prompt 的措辞、tool schema
的设计、context 的组装方式。

这引出一个假设：**coding agent
系统的当前瓶颈可能不在安全性、不在性能、不在协议设计，而在 prompt 和
tool schema 与底层模型之间的适配质量。** 如果这个假设成立，那
Codex
在基础设施层的投资虽然工程上令人敬佩，但对输出质量的边际贡献可能不如在交互层多做一些模型适配工作。

当然，这只是一个假设。验证它需要一个受控实验：同一个模型，分别通过
Codex 和 OpenCode 的 harness 执行同一组编码任务（理想情况下用 SWE-bench
这样的标准化任务集），对比通过率和代码质量。如果差异显著且集中在特定类型的任务上，就能更精准地定位瓶颈的位置。目前公开的数据还不足以做出定论，但方向值得关注。

### 11.5 认知资产的可迁移性

第 8 节评估了 Codex
的定制空间。但定制越深入，一个隐含的问题就越重要：**当你需要换工具时，投入的认知能带走多少？**

AGENTS.md 的格式是跨工具可迁移的。Linux Foundation 的 Agentic AI
Foundation 已经在推动它成为行业标准，OpenCode、Cursor、Copilot、Gemini
CLI 都支持读取。你在 AGENTS.md
里编码的项目规范、架构约束、代码风格，换到任何工具都能用。这部分投资是安全的。

但 Skills（Codex 专有的 markdown + 脚本格式）、config.toml 的 profile
系统、App Server 协议的客户端集成，这些都是 Codex
生态专属的。你在这些层面投入越多，迁移成本越高。特别是
Skills，它的内容本身（“如何跑 linter”、“如何部署到
staging”）是通用的认知，但它的格式和注入机制是 Codex
专有的。如果你把同样的知识写成一个通用的 markdown 文件而不是 Codex
Skills 格式，它的可迁移性会好得多，只是在 Codex
里少了自动注入的便利。

更深层的观点是：在一个工具生态还在快速演变的阶段，**值得长期投资的是认知本身（对项目的理解、对代码质量的定义、对架构的判断），而不是认知的载体（某个工具的专有配置格式）。**
AGENTS.md 之所以是好的投资，不仅因为它跨工具可用，更因为写 AGENTS.md
的过程本身就是在逼你把隐性知识显式化。即使有一天 AGENTS.md
这个格式消失了，显式化的过程中你获得的理解不会消失。这才是真正的复利资产。

## 参考来源

1. Michael Bolin, “Unrolling the Codex agent loop”, OpenAI, 2026-01.
   https://openai.com/index/unrolling-the-codex-agent-loop/
2. Celia Chen, “Unlocking the Codex harness: how we built the App
   Server”, OpenAI, 2026-02.
   https://openai.com/index/unlocking-the-codex-harness/
3. Gergely Orosz, “How Codex is built”, The Pragmatic Engineer,
   2026-02.
   https://newsletter.pragmaticengineer.com/p/how-codex-is-built
4. takiko, “Exploring the OpenAI Codex CLI Source Code”, Zenn, 2025.
   https://zenn.dev/takiko/articles/e2b8065158c8d0
5. takiko, “How Codex CLI Implements Agent Skills”, Zenn, 2025.
   https://zenn.dev/takiko/articles/codex-cli-agent-skills-implementation
6. Blake Crosley, “Codex CLI vs Claude Code in 2026: Architecture Deep
   Dive”, 2026.
   https://blakecrosley.com/blog/codex-vs-claude-code-2026
7. ZenML, “OpenAI Codex CLI Architecture and Agent Loop Design”, 2026.
   https://www.zenml.io/llmops-database/building-production-ready-ai-agents-openai-codex-cli-architecture-and-agent-loop-design
8. Ars Technica, “OpenAI spills technical details about how its AI
   coding agent works”, 2026-01.
   https://arstechnica.com/ai/2026/01/openai-spills-technical-details-about-how-its-ai-coding-agent-works/
9. InfoQ, “OpenAI Publishes Codex App Server Architecture”, 2026-02.
   https://www.infoq.com/news/2026/02/opanai-codex-app-server/
10. OpenAI, “Open Source Components”,
    developers.openai.com/codex/open-source/.
    https://developers.openai.com/codex/open-source/
11. Morph, “OpenCode vs Codex CLI: Harness Architecture Deep Dive”,
    2026-02. https://morphllm.com/comparisons/opencode-vs-codex
12. Reddit r/opencodeCLI, “Opencode vs Codex CLI: Same Prompt, Clearer
    Output — Why?”.
    https://www.reddit.com/r/opencodeCLI/comments/1qdujsl/
13. OpenAI, “Advanced Configuration: Custom model providers”,
    developers.openai.com/codex/config-advanced/.
    https://developers.openai.com/codex/config-advanced/
14. Reddit r/codereview, “We analyzed the code quality of 3 open-source
    AI coding agents”.
    https://www.reddit.com/r/codereview/comments/1rs3skb/
15. Morph, “We Tested 15 AI Coding Agents (2026). Only 3 Changed How We
    Work”. https://morphllm.com/ai-coding-agent

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
