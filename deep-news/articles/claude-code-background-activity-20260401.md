---
title: "Claude Code\n的后台活动：你以为它在等你打字，其实它一直在做事"
date: 2026-04-01
source: https://yage.ai/share/claude-code-background-activity-20260401.html
slug: claude-code-background-activity-20260401
lang: zh
---
# Claude Code 的后台活动：你以为它在等你打字，其实它一直在做事

发布于 2026 年 4 月 1 日 · [查看原网页](https://yage.ai/share/claude-code-background-activity-20260401.html)

泄露的 Claude Code 源码揭示了一个此前难以验证的事实：Claude Code
的生命周期远远超出用户可见的请求-响应循环。当你的光标在输入框里闪烁，等待你组织下一句话的时候，Claude
Code
的后台正在执行预测执行、记忆提取、文档维护、上下文压缩等数十种异步任务。每一次你以为的空闲，都是系统密度最高的工作时段之一。

## 为什么这篇文章跟你相关

这些后台机制并非 Claude Code 独创的巧思。它们代表了 AI agent
行业正在收敛的一组通用 pattern，理解它们对构建任何 agent
系统都有直接价值。

我们自己的 [context
infrastructure](https://yage.ai/context-infrastructure.html) 设计理念与 Claude Code 的后台活动体系高度相通。Claude
Code 的记忆提取、自动压缩、prompt cache
优化，可以无缝迁移到我们的工作流中，因为底层解决的是同一个问题：如何让
agent 在多次交互间维持连贯的认知状态。[OpenClaw 的 heartbeat
自动蒸馏机制](https://yage.ai/openclaw.html)是同一个 pattern 的另一种实例化。当我们看到 Claude Code
的 auto-dream 每 24 小时整合一次会话记忆，OpenClaw 的 heartbeat
按固定节奏蒸馏上下文，两个系统独立演化出了几乎相同的认知维护节奏，这说明这类设计已经成为行业的标准做法。我们在
[Claude
Dispatch vs OpenClaw 的分析](https://yage.ai/share/claude-dispatch-vs-openclaw-survey-20260318.html)中讨论过的自动化 vs
可控性的张力，与这篇文章的观察直接呼应：后台活动越多，系统越智能，用户越难理解系统在做什么。这个
trade-off 贯穿了下面每一个机制的设计决策。

这篇文章从源码出发，选取四个最具工程深度的后台机制，展开其设计决策和实现细节。

## Prompt cache：贯穿始终的工程约束

在展开具体机制之前，有一个跨切面的工程原则需要先说清楚：prompt cache
的维护是 Claude Code 全部后台活动的硬性约束，而非某个单一 feature
的优化点。Anthropic 自己的 [context
engineering 博客](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)也将 cache 放在 context engineering 的核心位置。

Claude Code 的每一个后台 agent 都以 forked agent 模式运行，而 forked
agent 的第一条设计原则是：必须与父进程共享完全相同的 cache key
参数（system prompt、tools、model、messages prefix、thinking
config）。任何参数偏差都会导致缓存失效，代价是一次完整的冷启动 API
调用。源码中记录了一个真实的教训：PR #18143 试图给 fork 设置
`effort:'low'`，结果 cache hit rate 从 92.7% 暴跌到
61%，cache write 量飙升 45 倍。安全的 override
只有四个：abortController（不发送到
API）、skipTranscript（纯客户端）、skipCacheWrite（控制 cache\_control
标记，不影响 cache key）、canUseTool（客户端权限检查）。

这个约束体现在每一个后台机制中。推测执行的 forked agent 共享 prompt
cache。记忆提取的 forked agent 共享 prompt cache。auto-dream 的 forked
agent 共享 prompt cache。session memory 的 forked agent 共享 prompt
cache。所有后台 agent 都是在 prompt cache
的约束下设计的，参数不敢动，模型不敢换，thinking config
不敢改。这使得后台活动的成本极低（绝大多数 token
命中缓存），同时也解释了为什么这些 fork 的行为空间被限制得如此狭窄。

## 一、推测执行：预测你的下一步，然后真的做出来

推测执行（Speculation）是整个后台活动体系中最激进的设计。（Anthropic
内部专属，`USER_TYPE === 'ant'`。）它的逻辑链条分三步：预测用户即将输入什么指令，将这条预测指令交给一个
forked agent 真正执行，用 copy-on-write overlay
文件系统隔离执行产物。如果用户最终接受了预测，overlay
立刻合并到主文件系统，响应几乎即时返回。

### 预测阶段

预测发生在每次模型回复完成之后。`promptSuggestion.ts` 在
stop hooks 中被 fire-and-forget 调用，fork 出一个子
agent，用与父进程完全相同的 prompt cache 参数生成预测。（Prompt
Suggestion 本身是公开版可用的，受 GrowthBook
`tengu_chomp_inflection` 实验标志控制。推测执行是在 prompt
suggestion 基础上的进一步行为，仅限内部用户。）

```
const result = await runForkedAgent({
  promptMessages: [createUserMessage({ content: prompt })],
  cacheSafeParams, // Don't override tools/thinking settings - busts cache
  canUseTool,
  querySource: 'prompt_suggestion',
  forkLabel: 'prompt_suggestion',
  overrides: { abortController },
  skipTranscript: true,
  skipCacheWrite: true,
})
```

预测内容经过一系列过滤器筛选：长度限制在 2-12
个单词，过滤掉评价性语句（thanks、looks good）、Claude 口吻的表达（Let
me…、I’ll…）、多句话、格式化标记。过滤的目标是只留下用户自己可能打出来的短指令。

### 执行阶段

当预测通过筛选后，`speculation.ts`
立刻启动真正的推测执行。关键设计是 copy-on-write overlay：

```
// Copy-on-write: copy original to overlay if not yet there
if (!writtenPathsRef.current.has(rel)) {
  const overlayFile = join(overlayPath, rel)
  await mkdir(dirname(overlayFile), { recursive: true })
  try {
    await copyFile(join(cwd, rel), overlayFile)
  } catch {
    // Original may not exist (new file creation) - that's fine
  }
  writtenPathsRef.current.add(rel)
}
input = { ...input, [pathKey]: join(overlayPath, rel) }
```

overlay 路径位于
`~/.claude/tmp/speculation/<pid>/<uuid>/`。当
forked agent 要写文件时，系统先把原始文件拷贝到 overlay
目录，然后把写操作重定向到 overlay
中的副本。读操作则做反向检查：如果目标文件已经在 overlay
中被修改过，就从 overlay
读取；否则直接读主文件系统。这样就实现了完全隔离的推测执行环境。

推测执行有明确的安全边界。只有 Edit、Write、NotebookEdit
三种工具允许写入（且写入被重定向到 overlay），Read、Glob、Grep
等只读工具直接放行，Bash 命令只允许通过 read-only
验证的指令。遇到需要用户确认的文件编辑（权限模式低于
acceptEdits），推测立刻暂停并记录一个 boundary。最多允许 20 轮对话、100
条消息。

### 接受与 Pipelining

当用户按下 Tab 接受预测时，`acceptSpeculation` 将 overlay
中的文件逐一 copy
回主文件系统，把推测过程中产生的消息注入到正式对话流中。如果推测已经完成（boundary
type 为
complete），整个响应即时呈现。如果推测中途因触及安全边界而暂停，系统会截断到最后一条
user 消息，发起一次后续查询让模型从断点继续。

更精彩的是
pipelining。当第一轮推测完成后，系统立刻在等待用户接受的间隙里启动第二轮预测：

```
// Pipeline: generate the next suggestion while we wait for the user to accept
void generatePipelinedSuggestion(
  contextRef.current,
  suggestionText,
  messagesRef.current,
  setAppState,
  abortController,
)
```

如果用户接受了第一轮预测，系统检查是否已经有 pipelined suggestion
可用，有的话直接提升为新的预测并立刻启动对应的推测执行。这形成了一条预计算链：第一步预测完成的瞬间，第二步已经在路上。

理论上讲，如果用户连续接受多次预测，每一次的响应时间都趋近于零，因为所有计算都发生在用户思考的间隙里。这已经跨越了补全的范畴，进入了
agentic 的自主工作流领域。

## 二、Auto-Dream：24 小时无交互后的记忆整合

Auto-Dream 的设计灵感很明确：人类在睡眠中整合白天的记忆，Claude Code
在无人交互时整合多次会话的上下文。（公开版可用，GrowthBook
`tengu_onyx_plover` 实验标志控制。用户设置
`autoDreamEnabled` 可覆盖远程配置。）

源码中的入口是
`autoDream.ts`，触发条件遵循一个三级门控（gate order:
cheapest first）：

```
1. Time: hours since lastConsolidatedAt >= minHours (one stat)
2. Sessions: transcript count with mtime > lastConsolidatedAt >= minSessions
3. Lock: no other process mid-consolidation
```

默认参数是 24 小时和 5 个 session。也就是说，只有在距离上次整合超过
24 小时、且期间积累了至少 5 个会话的 transcript 后，dream
才会触发。这些参数由 GrowthBook feature flag
`tengu_onyx_plover` 远程控制，可以在线调整而无需发版。

触发后，系统 fork 一个子 agent，给它一段精心设计的 consolidation
prompt。prompt
把整合过程分为四个阶段：Orient（读取现有记忆文件了解当前状态）、Gather（从
transcript
中搜索新信号）、Consolidate（将新信息合并到记忆文件中）、Prune and
Index（更新索引、清理过期内容）。

关于 transcript 搜索，prompt 明确指示子 agent 用 grep 做窄搜索：

```
grep -rn "<narrow term>" ${transcriptDir}/ --include="*.jsonl" | tail -50
```

原因是 transcript 文件（大型 JSONL）可能非常大，全量读取会消耗大量
token。prompt 的指导哲学是 “Don’t exhaustively read transcripts. Look
only for things you already suspect matter.”

子 agent 的权限受到严格限制：Bash
只允许只读命令（ls、find、grep、cat、stat、wc、head、tail），Edit 和
Write 只能操作 memory 目录内的文件。这通过
`createAutoMemCanUseTool` 函数实现，extractMemories 和
autoDream 共享同一套权限逻辑。

整合完成后，如果子 agent
修改了任何记忆文件，系统会在主对话流中插入一条 “Improved N memories”
的系统消息，让用户知道后台发生了记忆更新。如果子 agent
执行失败，系统会回滚锁文件的
mtime，这样下次时间门控检查时会重新通过，实现自动重试。两次重试之间有一个
10 分钟的 scan throttle，避免在 session gate 不满足时反复扫描。

这个设计中值得注意的工程取舍是：dream 总是在用户与 Claude Code
正常交互的间隙触发（每次 stop hooks
执行时检查），而非由独立的定时器驱动。这意味着如果用户连续 48
小时没有使用 Claude Code，dream
不会执行，直到下一次交互开始时才被触发。这个设计优先保证了资源效率，代价是整合可能存在延迟。

## 三、Magic Docs：读一次就被跟踪的自动维护文档

Magic Docs 的触发机制非常优雅。（Anthropic
内部专属，`USER_TYPE === 'ant'`。）任何 Markdown
文件的第一行如果匹配 `# MAGIC DOC: <title>`
这个模式，就会被自动注册为需要持续维护的文档。注册发生在 FileReadTool 的
listener 回调中：

```
registerFileReadListener((filePath: string, content: string) => {
  const result = detectMagicDocHeader(content)
  if (result) {
    registerMagicDoc(filePath)
  }
})
```

也就是说，你只要读过一次这个文件，它就被跟踪了。之后每次模型回复结束且最后一轮助手消息中没有工具调用时（表示对话处于自然空闲点），Magic
Docs 的 post-sampling hook 就会逐一更新所有已跟踪的文档。

更新过程使用 Sonnet 模型（而非主对话使用的 Opus），作为一个受限的子
agent 运行，只被赋予 Edit 工具权限，且只能编辑对应的 Magic Doc
文件。update prompt 的哲学值得引述：

```
DOCUMENTATION PHILOSOPHY - READ CAREFULLY:
- BE TERSE. High signal only. No filler words or unnecessary elaboration.
- Documentation is for OVERVIEWS, ARCHITECTURE, and ENTRY POINTS - not detailed code walkthroughs
- Do NOT duplicate information that's already obvious from reading the source code
- Focus on: WHY things exist, HOW components connect, WHERE to start reading, WHAT patterns are used
```

此外，Magic Doc header 下面如果紧跟一行斜体文字，会被解析为
document-specific
instructions，作为优先级高于通用规则的定制化指令传递给更新子
agent。这意味着文档作者可以在文件内嵌入对 AI 更新行为的控制。

prompt 还有一个关键约束：“Keep the document CURRENT with the latest
state of the codebase. This is NOT a changelog or history.” 更新子 agent
被明确要求原地修改信息、删除过时内容，而非追加历史记录。这使得 Magic Doc
始终反映代码库的当前状态，而非沦为无人维护的变更日志。

## 四、Extract Memories：每轮对话结束后的持久记忆提取

Extract Memories 是 Claude Code
记忆系统的核心写入路径。（公开版可用，构建标志
`EXTRACT_MEMORIES` 编译进公开发行版，运行时由
`isExtractModeActive()` 和自动记忆开关
`isAutoMemoryEnabled()` 共同控制。）每次 query loop
结束时（模型产生最终回复且没有工具调用），`handleStopHooks`
会 fire-and-forget 地调用 `executeExtractMemories`：

```
if (feature('EXTRACT_MEMORIES') && !toolUseContext.agentId && isExtractModeActive()) {
  void extractMemoriesModule!.executeExtractMemories(
    stopHookContext,
    toolUseContext.appendSystemMessage,
  )
}
```

提取 agent 以 forked agent 模式运行，共享父进程的完整 prompt
cache。它只看最近新增的消息（通过一个 cursor UUID
追踪上次处理到哪条消息），从中识别值得持久化的信息，然后写入
`~/.claude/projects/<path>/memory/` 目录。

这里有一个精妙的互斥设计。如果主 agent
自己在对话过程中已经写过记忆文件（用户显式要求 “记住这个”），提取 agent
会跳过这一轮：

```
if (hasMemoryWritesSince(messages, lastMemoryMessageUuid)) {
  logForDebugging(
    '[extractMemories] skipping — conversation already wrote to memory files',
  )
  // ...advance cursor past this range
  return
}
```

主 agent 和后台提取 agent
对同一段对话是互斥的。这避免了重复写入，也避免了两个 agent
对同一段对话产生冲突的记忆。

提取频率受两个维度控制：token
阈值和工具调用计数。只有两个条件都满足时才触发提取。此外还有一个
`tengu_bramble_lintel` feature flag
控制的轮次间隔，允许进一步稀释提取频率。

提取 agent 的 prompt 设计强调效率。它被限制在 5
轮以内完成工作，推荐的策略是：第一轮并行读取所有需要更新的文件，第二轮并行写入所有修改。prompt
明确禁止 “读代码去验证某个记忆是否正确” 这类探索行为：

```
You MUST only use content from the last ~N messages to update your persistent memories. 
Do not waste any turns attempting to investigate or verify that content further — 
no grepping source files, no reading code to confirm a pattern exists, no git commands.
```

在非交互模式下（`-p` 模式或 SDK），`print.ts`
会在刷出响应后显式等待 in-flight extraction 完成再执行 graceful
shutdown，确保记忆提取不会被进程退出截断。这通过
`drainPendingExtraction` 实现，带 60 秒超时。

## 完整的后台活动图谱

上述四个机制是后台活动中工程复杂度最高的。在它们之外，Claude Code
还运行着一系列辅助性后台任务：

- Session Memory（公开版可用，GrowthBook
  `tengu_session_memory` 控制）：基于 token
  阈值和工具调用计数定期维护当前会话的摘要笔记，供 auto-compact 和 away
  summary 使用。只有 Sonnet 子 agent 带 Edit 权限，且只能编辑对应的
  session memory 文件。
- Auto-Compact（公开版可用，默认开启，`autoCompactEnabled`
  设置项默认
  `true`）：上下文窗口接近容量上限时自动压缩旧消息。计算公式是
  `effective context window - 13000 tokens`，达到这个阈值就触发。优先尝试基于
  session memory 的压缩，失败后 fallback 到 legacy compaction。有一个
  circuit breaker：连续失败 3
  次后停止重试，避免在上下文不可恢复的情况下反复调 API。
- Cron Scheduler（公开版可用，构建标志 `AGENT_TRIGGERS`
  编译进公开发行版，GrowthBook `tengu_kairos_cron` 默认
  `true` 作为远程 kill switch）：一个完整的 cron
  调度系统，每秒检查一次是否有到期的定时任务。支持文件驱动（`.claude/scheduled_tasks.json`）和
  session-only 两种任务类型。多个 Claude
  实例共享同一个工作目录时，通过锁机制确保只有一个实例执行 cron
  任务。
- Prevent Sleep（公开版可用，macOS 专属，无 feature flag 门控）：在
  macOS 上通过 `caffeinate -i -t 300`
  阻止系统空闲休眠。caffeinate 进程每 4 分钟重启一次（超时 5
  分钟），这样即使 Node 进程被 SIGKILL 杀掉，孤儿 caffeinate 也会在 5
  分钟后自动退出。采用 refcount 模式管理，多个并发任务共享同一个
  caffeinate 进程。
- Away Summary（公开版可用，无 feature flag
  门控）：用户一段时间不活动后回来，系统调小模型（small fast
  model）基于最近 30 条消息和 session memory 生成一段 1-3
  句的摘要，告诉用户 “你不在的时候我们在做什么”。
- Plugin Auto-Update（公开版可用，无 feature flag
  门控）：启动时后台检查已安装插件的更新。先 refresh 启用了 autoUpdate 的
  marketplace（git pull），再逐一检查这些 marketplace
  中的已安装插件。更新是 non-inplace
  的（只写磁盘），需要重启才生效。更新完成后通过 callback 通知 REPL
  显示重启提示。
- GrowthBook Feature Flag Refresh（公开版可用，无 feature flag
  门控，外部用户 6 小时刷新一次，内部用户 20 分钟一次）：定期从远程拉取
  feature flag 配置。几乎所有后台功能的开关、参数和行为变体都通过 feature
  flag 控制。
- Background
  Housekeeping（公开版可用）：`startBackgroundHousekeeping`
  函数在启动时一次性初始化 Magic Docs、Skill Improvement、Extract
  Memories、Auto-Dream 和 Plugin Auto-Update，并在启动 10
  分钟后（且用户最近 1
  分钟内无交互时）执行老版本清理和消息文件清理等慢操作。长时间运行的
  session 在内部用户环境下还会每 24 小时执行一次 npm cache
  和旧版本的周期性清理。

## 设计哲学：空闲时间是计算资源

把这些机制放在一起看，Claude Code
的设计哲学很清晰：用户的思考间隙是最宝贵的计算资源。在传统的 REPL
模型中，用户输入和 AI 响应之间的空白是纯粹的等待。Claude Code
把这段空白变成了一个密集的后台调度窗口，运行着预测执行、记忆整合、文档维护、上下文管理等多条并行流水线。

每条流水线都遵循相同的工程约束：forked agent 模式确保与父进程共享
prompt cache（代价是参数不能有任何偏差），fire-and-forget
调用确保后台任务不阻塞用户交互，feature flag
控制确保任何新机制都可以灰度发布和在线调参，权限沙盒确保后台 agent
只能操作其职责范围内的资源。

所有后台活动的总调度枢纽是 `handleStopHooks`，在每次 query
loop 结束时执行。这个函数里的调用顺序就是后台活动的优先级：先 save cache
params（为未来的 fork 准备缓存），再并行启动 prompt suggestion、extract
memories、auto-dream。这些 fire-and-forget 调用跑在 Node
的事件循环里，直到用户的下一次输入到来时，仍在持续工作的后台任务会通过
abort controller 被取消（如 speculation）或继续在后台静默完成（如
extract memories）。

从工程实践的角度看，Claude Code 已经是一个带有自主生命周期的
daemon，而非一个等待输入的
REPL。这种从被动响应到主动计算的转变，可能代表了 AI
辅助编程工具演进的一个方向：AI
系统在与人类协作时，应该利用一切可用的空闲窗口预先计算、整理和优化，使得当人类准备好时，AI
的响应已经在路上。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
