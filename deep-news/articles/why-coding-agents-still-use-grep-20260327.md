---
title: "为什么 Coding Agent 的搜索主干仍然是 grep"
date: 2026-03-27
source: https://yage.ai/share/why-coding-agents-still-use-grep-20260327.html
slug: why-coding-agents-still-use-grep-20260327
lang: zh
---
# 为什么 Coding Agent 的搜索主干仍然是 grep

发布于 2026 年 3 月 27 日 · [查看原网页](https://yage.ai/share/why-coding-agents-still-use-grep-20260327.html)

*一份关于 AI-native
开发工具中文本搜索、符号导航与语义检索之间关系的调研报告*

---

## 核心判断

在 LSP 已经成为 IDE 基础设施标准的今天，几乎所有主流 agentic coding
产品仍然将 grep/ripgrep 作为代码搜索的默认主干。Claude Code、Codex
CLI、OpenCode、Cursor、Continue、Aider
都做了同样的选择。这看起来像是技术倒退，但实际上反映了 agent
运行时与人类 IDE 交互之间的根本差异。

更准确地说，这个问题本身包含一个隐含假设：grep 和 LSP
是同一类工具的不同版本，更强的那个应该替代更弱的那个。这个假设不成立。grep
和 LSP 解决的是 agent
工作流中两个不同层面的问题。行业收敛出来的做法是分层检索：grep/rg
负责广覆盖、低成本的探索性搜索，LSP
负责高精度的符号级确认操作。两者并存不是冗余，而是因为它们服务于 agent
loop 中不同的认知阶段和不同的成本约束。

---

## 现实样本：谁在用什么

在讨论机制之前，先看行业事实。以下六个产品覆盖了当前 agentic coding
的主要形态，它们在搜索工具选型上呈现高度一致的 pattern。

### Claude Code

Boris Cherny 在 Pragmatic Engineer 的访谈中明确说明了 Claude Code
的搜索架构：

> Claude Code’s agentic search is really just glob and grep, and it
> outperformed RAG.

Anthropic 团队尝试过 local vector DB、recursive model-based indexing
等方案，最终 plain glob and grep 效果最好。Boris 引用 Meta/Instagram
的经验作为佐证：当工程师的 click-to-definition
失效时，他们会回到文本搜索。([Pragmatic
Engineer](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny))

值得注意的是，Claude Code 在 v2.0.74（2025 年 12 月）中加入了原生 LSP
支持，提供
goToDefinition、findReferences、hover、documentSymbol、incomingCalls、outgoingCalls
六类操作，覆盖 11 种主要语言。([GitHub Issue #858 on
Serena](https://github.com/oraios/serena/issues/858)) 但从 HN 上的用户反馈来看，实际触发频率很低。一位用户说：

> I haven’t come across a case where it has used the LSP yet. Opus 4.5
> is fairly consistent in running QA at proper times… the agent usually
> finds what it needs.

([HN: Claude
Code gets native LSP support](https://news.ycombinator.com/item?id=46355165))

这恰好印证了分层模型：LSP 作为增强能力存在，但 grep/glob 仍然是 agent
在绝大多数场景下的第一选择。

### Codex CLI

OpenAI 的 Codex CLI 把 ripgrep 偏好写进了核心 prompt：

> When searching for text or files, prefer `rg` /
> `rg --files` since `rg` is faster than grep.

([Codex
prompt.md](https://github.com/openai/codex/blob/6a0c4709ca2154e9f3ebb07e58fb156386630188/codex-rs/core/prompt.md#L264))

这个偏好不是 prompt 里的偶然设定。在 orchestrator
模板、安全模块的自动批准白名单中，`rg`
都被列为标准操作。OpenAI 官方 Codex Prompting Guide 也将 `rg`
列为默认 solver tool。([Codex
orchestrator template](https://github.com/openai/codex/blob/6a0c4709ca2154e9f3ebb07e58fb156386630188/codex-rs/core/templates/agents/orchestrator.md), [Codex
Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide), [Safety
whitelist](https://github.com/openai/codex/blob/6a0c4709ca2154e9f3ebb07e58fb156386630188/codex-rs/shell-command/src/command_safety/is_safe_command.rs#L113-L134))

### OpenCode

OpenCode 的处理方式提供了最清晰的分层证据。它直接在产品里内嵌了
ripgrep 的安装与分发逻辑，覆盖 macOS/Linux/Windows，将 rg
视为产品级基础依赖。([OpenCode
ripgrep.ts](https://github.com/sst/opencode/blob/d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3/packages/opencode/src/file/ripgrep.ts))

同时，OpenCode 也提供了 LSP
tool，但它的描述里明确写出了限制条件：

> LSP server must be configured for this file type, otherwise it will
> report an error.

([OpenCode
lsp.txt](https://github.com/sst/opencode/blob/d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3/packages/opencode/src/tool/lsp.txt))

这一设计等于告诉模型：grep 是你随时可以调用的无条件工具，LSP
是在条件满足时才可用的增强能力。

### Cursor

Cursor 的工程博客提供了整个行业里最透明的搜索架构阐述。Vicent Marti
写道：

> Most Agent harnesses, including ours, default to using ripgrep when
> providing a search tool.

当 ripgrep 在超大 monorepo 里变慢（Cursor 看到过超过 15 秒的单次 rg
调用），Cursor 的优化方向不是切向量检索或 LSP，而是给 regex search
本身建本地索引。他们开发了基于 sparse n-gram 的本地索引方案，用 mmap
提供毫秒级查询。([Cursor: Fast regex
search](https://cursor.com/blog/fast-regex-search))

Cursor 还指出了 text search 索引与 semantic index
之间的一个关键差异：semantic index 对新鲜度要求低（因为 embedding
的微调不会导致最近邻搜索大幅偏移），而 text search
对新鲜度要求极高，尤其是 agent 读取自己刚写入的内容时。如果 text search
索引过期，agent 会陷入无谓的搜索循环，浪费大量 token。

### Aider

Aider 用 tree-sitter + PageRank 构建 repo map，通过 AST
解析提取函数签名和类定义，构建依赖图，按 token
预算动态裁剪最相关的符号上下文。([Aider
repomap.py](https://github.com/paul-gauthier/aider/blob/bdb4d9ff8ef88c3015a9845119bff37f49c93d7b/aider/repomap.py#L525)) 这是一种位于 grep 和 LSP
之间的方案：比纯文本搜索更懂代码结构，但比 LSP 轻量得多，不需要 language
server 进程常驻。

### Continue

Continue 的内置搜索工具 grepSearch 基于
ripgrep，实现里对结果数和字符数做了硬截断，明确是在服务 token
economy。([Continue
grepSearch.ts](https://github.com/continuedev/continue/blob/d220a2e3702994bc1a6e0a4daed84da67cb1277e/core/tools/implementations/grepSearch.ts))

---

## 为什么 grep 仍然是搜索主干

从六个产品样本可以看到，grep/rg 作为 agent
搜索主干不是个别团队的偶然选择，而是 de facto industry
practice。原因不在于 LSP 不够好，而在于 agent loop 的运行时约束与人类
IDE 交互的运行时约束有本质区别。

### 零预热、零配置的启动成本

Agent 需要在任意代码库、任意时间点立即开始工作。ripgrep
是一个无状态的可执行文件，给它一个目录和一个
pattern，它就返回结果。不需要安装 language
server，不需要等待初始索引完成，不需要检查项目配置文件是否存在且合法。

LSP 的启动流程则完全不同。它需要一个 language server
进程为每种语言配置和启动，需要完成初始化握手（`initialize` →
`initialized`），需要等待项目索引完成。在大型项目上，初始索引可能消耗大量
CPU 和内存，诊断结果可能要等数十秒才就绪。对于需要快速迭代的 agent loop
来说，这个启动成本是不可接受的。

### 覆盖范围：代码库是混合体

一个真实的代码仓库不只包含单语言源代码。它包含配置文件（YAML、TOML、JSON）、Shell
脚本、Dockerfile、Makefile、Markdown
文档、模板文件、生成代码、锁文件、迁移脚本。LSP 只覆盖它有 language
server 的文件类型，而 agent 的搜索需求覆盖仓库中的所有文本内容。

grep 天然不区分文件类型。它搜索所有文本文件，而这恰恰是 agent
在理解一个陌生代码库时需要的：先找到与任务相关的所有文本证据，不管它们出现在
`.py`、`.yaml`、`.env.example` 还是
`README.md` 中。

### 失败模式的不对称性

grep
的失败模式是假阳性：它可能返回名字恰好匹配但语义无关的结果。这是温和的失败，因为
LLM 擅长从混杂结果中筛选相关信息。

LSP 的失败模式更严重。当 language server
未安装、项目配置不合法、依赖未安装、环境不一致，或者代码本身处于半损坏状态时，LSP
可能报错（`ServerNotInitialized`、`E/NOT FOUND`、`E/LS CRASH`）、返回空结果或完全不可用。对
agent 来说，一个返回 false negative
或直接挂掉的工具比一个返回多余结果的工具危险得多。Princeton 的
Lanser-CLI 研究专门为此设计了详细的错误分类体系，覆盖了超过 15 种 LSP
特有的失败模式。([Lanser-CLI,
arXiv:2510.22907](https://arxiv.org/pdf/2510.22907))

### Shell composability 和 agent 编排

Agent 的控制平面是 shell-native 的。Agent loop
的基本操作单元是：发出一个 shell 命令，读取
stdout，根据结果决定下一步。ripgrep
完美适配这个模式：一行命令，一段文本输出，可以直接拼接进
prompt，可以管道连接其他工具。

LSP 是 JSON-RPC 协议，需要维护一个有状态的双向通信通道。它天然适合
IDE 这种长时间运行的客户端，但与 agent
的无状态、按需调用的执行模型存在摩擦。把 LSP 接入 agent loop
需要额外的封装层（类似 Lanser-CLI
所做的那样），而这层封装本身就引入了新的复杂度和失败点。

### Token 经济性

Agent 的每一次搜索结果都要被序列化成文本，送进 LLM 的 context
window。grep 的输出天然是人类可读的文本行，可以直接作为 context
消费。LSP 的返回值（类型签名、文件路径、位置对象）需要额外处理才能变成对
LLM 有意义的上下文。

更重要的是，agent
在探索阶段需要的是广覆盖的假设生成，而不是精确的符号定位。grep
返回的是一个概念聚落（concept
cluster），模型可以从中推断代码库的组织方式、命名惯例、相关文件的分布。LSP
的 findReferences
返回的是一组精确坐标，适合确认和操作，但在探索阶段提供的认知价值有限。

---

## LSP 的真实位置：精确操作层

以上分析可能给人一种 LSP 无用的印象。事实恰恰相反。LSP 在 agent
工作流中有明确的、不可替代的位置，但它的角色是精确操作层，而不是通用搜索层。

Claude Code 的 lsp-tools 插件提供了一个清晰的决策矩阵：

| 需求 | 工具 |
| --- | --- |
| 函数定义在哪里 | LSP: goToDefinition |
| 谁调用了这个函数 | LSP: findReferences |
| 这个类型的签名是什么 | LSP: hover |
| 找 TODO/FIXME 注释 | Grep |
| 搜索配置值 | Grep |
| 按文件名模式查找文件 | Glob |

([zircote.com:
LSP Tools Plugin for Claude Code](https://zircote.com/blog/2025/12/lsp-tools-plugin-for-claude-code/))

这个矩阵的核心逻辑是：LSP
用于语义操作（理解代码结构、类型、关系），grep
用于文本操作（搜索字面内容）。两者不是同一维度上的竞品。

LSP 在 agent 工作流中最有价值的场景包括：

1. **精确重命名**：grep 搜索 `getUserById`
   会匹配注释、字符串、类似名称的函数。LSP 的 rename
   操作只修改真正的符号引用。
2. **类型检查和诊断**：agent 修改代码后，LSP
   可以在不运行完整构建的情况下报告类型错误。
3. **调用链追踪**：incomingCalls/outgoingCalls
   提供的调用图信息是 grep 无法推断的。
4. **跨文件跳转**：当 agent
   已经定位到一个具体符号并需要追踪它的定义或用法时，goToDefinition 和
   findReferences 比 grep 精确得多。

换句话说，grep 用于 hypothesis
generation（生成关于代码库的假设），LSP 用于 hypothesis
verification（验证假设并执行精确操作）。

---

## 中间层：AST-aware 搜索

在纯文本搜索和完整 LSP
之间，存在一个实际运行中越来越重要的中间层：基于 tree-sitter
的结构感知搜索。

ast-grep 是这个层面的代表工具。它使用 tree-sitter 将代码解析成
CST（Concrete Syntax Tree），然后用看起来像普通代码的 pattern 在 AST
上做结构化匹配。相比 grep，它理解代码的语法结构；相比 LSP，它不需要
language server 进程，启动成本极低。([ast-grep GitHub](https://github.com/ast-grep/ast-grep))

Aider 的 repo map 方案也属于这个层面：用 tree-sitter
解析函数签名和类定义，用 PageRank 排序符号重要性，按 token
预算动态裁剪。这让模型在不需要完整 LSP
的情况下获得代码库的结构概览。

这个中间层的价值在于：它提供了比 grep
更高的精度（能区分函数调用和注释中的同名字符串），但保持了 grep
类工具的部署便利性（无状态、无需 language
server、可以在任意代码库上立即使用）。在 agent 编排中，它常被放在 grep
之后、LSP 之前，用于对 grep 结果做结构约束，或者在不具备 LSP
条件的场景下提供准语义能力。

---

## 真正的问题：为什么 agent runtime 是 text-native 的

到这里，表面问题（为什么 agent 用 grep 而不是
LSP）已经回答完了。但更值得追问的是一个更深层的 framing：为什么 agent
的控制平面是 text-native/shell-native 的，而不是 IDE-native 的？

人类开发者在 IDE 里工作时，享受的是一个高度集成的语义环境：LSP
提供导航和诊断，debugger 提供运行时状态，build system
提供编译反馈，version control 提供历史上下文。这些能力通过 IDE
的图形界面和快捷键暴露给人类用户。

Agent 的工作环境与此根本不同。它通过 shell
与代码库交互，通过文本输入输出传递信息，通过 tool calls
执行操作。它的”感知器官”是 stdout，它的”肌肉”是 shell
命令。在这个运行时架构下，一个能直接在 shell 里执行并输出文本的工具（如
ripgrep）天然比一个需要长连接、有状态协议、额外封装层的工具（如
LSP）更原生。

这不是技术局限——Claude Code 已经证明可以把 LSP
集成进来。这是一个架构选择：agent loop 的主控制流程按照 text-in-text-out
设计，因为这个模式的组合性最强、失败最温和、调试最透明。LSP
是这个控制流程上的高精度附件，不是控制流程本身。

Anthropic 在 agent 设计指南中的表述也印证了这一点：

> Just-in-time context, not pre-inference RAG—maintain lightweight
> identifiers, dynamically load data at runtime using tools.

([Mike
Mason: AI Coding Agents in 2026](https://mikemason.ca/writing/ai-coding-agents-jan-2026/))

这句话的核心含义是：agent
的上下文获取策略不应该依赖预建的复杂索引，而应该通过轻量工具在运行时按需获取。grep/rg
完美符合这个原则：零预建成本、按需调用、结果立即可用。

---

## 分层检索模型

综合以上分析，行业正在收敛的模型可以用一个检索漏斗来描述：

**第一层：文本扫描（grep/rg/glob）**。零配置，全文件类型覆盖，高召回率，失败温和（假阳性）。用于
agent 的探索性搜索、假设生成、上下文觅食。这是 agent loop
的默认搜索原语。

**第二层：结构约束（tree-sitter/ast-grep/repo
map）**。低配置，按语言提供 AST-level 匹配。用于在 grep
结果上叠加结构精度，或在 token 预算内生成代码库结构概览。不需要 language
server。

**第三层：符号导航（LSP）**。需要 language server
配置和启动。提供定义跳转、引用查找、类型信息、诊断、调用图。用于精确操作阶段：确认符号位置、执行重命名、检查类型错误。条件性可用。

**第四层：语义索引（embedding/vector
search）**。需要预建索引。提供自然语言级别的语义匹配。用于模糊搜索、概念性查询。Cursor
和其他工具将其作为补充手段，但 Anthropic 的实践表明 plain grep
在多数场景下已经足够好。

每一层的成本结构不同。往上走，fixed cost 更低，failure blast radius
更小，但精度更低。往下走，精度更高，但 fixed cost（配置、启动、维护）和
failure blast radius（环境不一致导致完全不可用）也更高。Agent
的默认行为是从顶层开始，只在需要时才下沉到更精确的层。

---

## 演进方向

当前行业的演进方向不是用 LSP 替代 grep，而是在每一层上各自优化。

**文本搜索层的优化**：Cursor 正在为 regex search
建本地索引，用 sparse n-gram 方案在客户端实现毫秒级查询，解决超大
monorepo 中 ripgrep 线性扫描的性能瓶颈。这说明行业判断是：text search
本身的性能优化比切换到另一种检索范式更有价值。([Cursor: Fast regex
search](https://cursor.com/blog/fast-regex-search))

**模型层的优化**：Cursor 的内部模型命名 SWE-grep-mini
专门针对上下文检索做 post-training。这个名字本身就是信号：grep 作为
agent
基础操作的地位重要到值得单独训练一个专用模型来提升它的使用效率。

**LSP 层的形式化**：Princeton 的 Lanser-CLI 研究试图把
LSP 交互变成 schema-validated 的 CLI 命令，带有显式的错误分类和确定性
replay 能力，目标是让 LSP 成为 agent loop 中可靠的 process reward
信号。这代表了一种让 LSP 更 agent-native 的努力方向。([Lanser-CLI,
arXiv:2510.22907](https://arxiv.org/pdf/2510.22907))

**结构搜索层的扩展**：ast-grep 在 agent
生态中的采用正在增长。VT Code 等新工具将 tree-sitter parsing 与 ast-grep
pattern matching
结合，在修改代码前做结构化预览。这个中间层有可能在某些场景下承接部分原本需要
LSP 才能完成的任务。

---

## 对工具设计者的启示

如果你在设计 agentic coding 工具或 agent loop
的搜索策略，以下几个判断可以作为参考。

第一，grep/rg
应该是默认搜索工具，不需要论证。行业已经用实践收敛了这个选择。你需要论证的是为什么要在特定场景下使用更重的工具。

第二，LSP
应该作为可选增强层存在，而不是搜索基线。它的价值在精确操作阶段最大。如果你的
agent 需要做重命名、类型检查、调用链分析，LSP 是正确的工具。如果你的
agent 在探索代码库、寻找线索、理解架构，grep 更合适。

第三，不要低估中间层（tree-sitter/ast-grep）的价值。它在不引入
language server
复杂度的前提下提供了有用的结构精度，而且部署门槛很低。

第四，搜索工具的选择不只是精度对比，还涉及成本结构。需要考虑的维度包括：fixed
cost（配置和启动成本）、variable cost（每次调用的延迟和 token
消耗）、failure cost（工具不可用时的恢复代价）、freshness
cost（索引与工作区状态同步的代价）。在 agent loop
这种高频迭代的场景下，低 fixed cost 和低 failure cost
往往比高精度更重要。

第五，evolution path
不是替换，而是分层增强。文本搜索层会继续被优化（更好的索引、更智能的模型驱动），LSP
层会继续被 agent-native 化（更好的 CLI
封装、更可靠的错误处理），中间层会继续扩展覆盖面。三者各自进化，同时协作。

---

## 主要来源

- Boris Cherny, Pragmatic Engineer: [Building
  Claude Code](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)
- Cursor: [Fast
  regex search: indexing text for agent tools](https://cursor.com/blog/fast-regex-search)
- OpenAI Codex CLI: [prompt.md](https://github.com/openai/codex/blob/6a0c4709ca2154e9f3ebb07e58fb156386630188/codex-rs/core/prompt.md#L264),
  [orchestrator.md](https://github.com/openai/codex/blob/6a0c4709ca2154e9f3ebb07e58fb156386630188/codex-rs/core/templates/agents/orchestrator.md),
  [Safety
  whitelist](https://github.com/openai/codex/blob/6a0c4709ca2154e9f3ebb07e58fb156386630188/codex-rs/shell-command/src/command_safety/is_safe_command.rs#L113-L134), [Prompting
  Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
- OpenCode: [ripgrep.ts](https://github.com/sst/opencode/blob/d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3/packages/opencode/src/file/ripgrep.ts),
  [grep.txt](https://github.com/sst/opencode/blob/d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3/packages/opencode/src/tool/grep.txt),
  [lsp.txt](https://github.com/sst/opencode/blob/d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3/packages/opencode/src/tool/lsp.txt)
- Continue: [grepSearch.ts](https://github.com/continuedev/continue/blob/d220a2e3702994bc1a6e0a4daed84da67cb1277e/core/tools/implementations/grepSearch.ts)
- Aider: [repomap.py](https://github.com/paul-gauthier/aider/blob/bdb4d9ff8ef88c3015a9845119bff37f49c93d7b/aider/repomap.py#L525)
- Lanser-CLI (Princeton): [arXiv:2510.22907](https://arxiv.org/pdf/2510.22907)
- Mike Mason: [AI Coding
  Agents in 2026](https://mikemason.ca/writing/ai-coding-agents-jan-2026/)
- Claude Code LSP: [zircote.com](https://zircote.com/blog/2025/12/lsp-tools-plugin-for-claude-code/),
  [HN
  discussion](https://news.ycombinator.com/item?id=46355165)
- ast-grep: [GitHub](https://github.com/ast-grep/ast-grep),
  [Core
  Concepts](https://ast-grep.github.io/advanced/core-concepts.html)
- OpenCode LSP Setup: [amirteymoori.com](https://amirteymoori.com/lsp-language-server-protocol-ai-coding-tools/)

## 相关阅读

- [RAG
  的每一项核心技术，搜索引擎都做过](https://yage.ai/share/rag-reinvented-search-engine-20260326.html) — grep
  持续存在的根源：搜索引擎几十年解决的同类问题，在 Agent
  上下文里被再次验证
- [LanceDB
  选型指南：它为什么这么火，以及你的项目是否该用它](https://yage.ai/share/lancedb-selection-guide-20260327.html) — grep
  之外的检索层：当代码库需要语义检索时，向量数据库的选型考量
- [RAG
  向量检索的核心抉择：什么时候最简单的方案就够用](https://yage.ai/share/rag-ann-vector-search-20260524.html) — 与 grep
  互补而非替代：ANN 向量检索的适用场景与成本边界

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
