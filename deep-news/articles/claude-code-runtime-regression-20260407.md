---
title: "Claude Code 降智事件：一次 runtime\n层的隐性单边降级"
date: 2026-04-07
source: https://yage.ai/share/claude-code-runtime-regression-20260407.html
slug: claude-code-runtime-regression-20260407
lang: zh
---
# Claude Code 降智事件：一次 runtime 层的隐性单边降级

发布于 2026 年 4 月 7 日 · [查看原网页](https://yage.ai/share/claude-code-runtime-regression-20260407.html)

中文 AI 圈子最近在热议一个词：降智。指的是某个 AI
工具明明模型号没换、参数没变、订阅价格没动，但它的实际表现莫名其妙变差了。你交给它的任务它越做越敷衍，编辑文件之前不再先读文件，长会话里反复打转，开始用最简单的修复绕开复杂问题。每个用户的第一反应几乎都一样：检查自己的
prompt，怀疑自己的工作流，怀疑自己的运气。然后过几周，社区里有人拿出证据，厂商最终承认是某个
infra bug 或者 default 调整。

2026 年 2 月到 4 月发生在 Claude Code 上的这次降智，是过去八个月里
Anthropic
至少第五次面对同样的指控。前几次都以”用户先抱怨，厂商先沉默，几周后承认
infra bug”的方式落幕。这次有点不一样的地方在于，AMD AI Director Stella
Laurenzo 用 [6,852
个本地 session 文件、17,871 个 thinking block、234,760 次 tool
调用](https://github.com/anthropics/claude-code/issues/42796)做了一次反向审计，把”我感觉它变笨了”变成了”以下是它在哪天、以哪种方式、在哪些行为指标上变差的证据”。这份分析让
[Hacker News
上的讨论](https://news.ycombinator.com/item?id=47660925)冲到 1,147 分、630 多条评论，[The
Register 在 4 月 6 日跟进报道](https://www.theregister.com/2026/04/06/anthropic_claude_code_dumber_lazier_amd_ai_director/)，Anthropic 在 24 小时内把 issue
关掉，标记为 completed。

这篇文章不打算复述那份分析的所有数字。你在那份 issue 和 The Register
的报道里都能看到完整数据。这篇文章想做的是更轻一些的事情：通过这次降智事件，把一个
builder
应该带走的直觉讲清楚。具体的统计数字、机制名字、配置项过几个月就会过时，但这个直觉会留下来，并且适用于你今天和未来用的每一个
AI agent 工具。如果你现在正在用 Claude
Code、读到这里已经开始烦躁想立刻止损，文末有两行可以今天就加到你 shell
配置里的环境变量，能把大部分丢失的推理深度拿回来。

短话先说：这次降智的真正成因不在模型层。Claude Opus 4.6
的权重没动，benchmark 上的 pass rate
也没明显变化。变的是介于模型和你之间的一层东西，我把它叫做 runtime
层。它过去几乎没有被 builder
当作一个独立维度来评估，但它现在已经是决定你 AI 工具实际表现的关键。

## Runtime 层是个之前不存在的东西

理解这次事件需要先建立一个直觉：你今天用 Claude Code 或者任何 agentic
AI 工具的时候，模型和你之间隔着一层不透明的中间机制。

过去用 LLM 的方式很简单。你写一个 prompt，调用
API，拿回结果。中间没有什么需要你关心的东西，模型版本和 API
参数就是全部。但 agentic AI
工具引入了一种新的中间层：模型不再是你直接调用的对象，而是被一个 agent
runtime 包着。这个 runtime
决定每次调用的时候模型应该思考多深、应该用多少
token、应该看多少上下文、应该自动 compact 还是不
compact、应该在什么情况下
retry。这些决定每天都在影响你的工作产出，但它们既不在 release notes
里、也不在 changelog 里、对用户基本不透明。

Stella 的分析里揭示的三个变化都在这一层。Anthropic 在 2 月 9 日给
Claude Opus 4.6 加了一个叫 adaptive thinking 的机制，让模型自己决定每个
turn 想多久。3 月 3 日把默认 reasoning 强度从 high 调到了 medium。3 月 5
日开始灰度推一个让 thinking 内容默认不再回传到本地 transcript 的 UI
header。Claude Code 团队负责人 Boris Cherny [在 issue
下的回应](https://news.ycombinator.com/item?id=47660925)把这三件事说得很清楚，他甚至承认了某些 turn 上 adaptive
thinking 把推理预算分配到了零。但这些变化没有出现在任何一份 release
notes 里，没有任何提前通知，对每个 daily 用户来说就是一句话：你今天用的
Claude Code，跟你六个月前用的 Claude Code，已经不是同一件东西。

模型层没动，协议层没动。变的全在 runtime 层。但因为 runtime
层对用户不可见，结果在你那里就表现成”模型变笨了”。

值得在脑子里固化下来的第一条直觉是这样的：从今天起，做技术选型的时候，模型层、协议层和
runtime
层应该是三个独立的评估维度。问”这个工具用什么模型”已经不够了。你还要问，谁在控制
runtime
层的默认值，他什么时候会改这些默认值，他改了之后你用什么方式知道。

## Runtime 层为什么注定会被悄悄调低

第二条更深的直觉是关于这次降级为什么会发生。短答案是：subscription
经济学。

Stella 在报告里附了一组成本估算。她按 March 的真实使用量，把同样的
API 请求用 Anthropic 的 Bedrock on-demand 价格折算了一下，得到的数字是
$42,121 一个月。她实际付的 Claude Code subscription 是 $400
一个月。比例是 122 倍。

这个数字背后的逻辑很简单。Power user 想要的”全速
reasoning”在算力上实在太贵，subscription 价格根本不可能 cover
这种成本。Anthropic 不是技术上做不到给 Stella 用她预期的
quality，而是经济结构上做不到。按这个 $400 收费持续给 power user 全速
reasoning，每个 power user 都在拖整个 subscription 业务的后腿。当你看到
Boris 在 issue 里说会”测试给 Teams 和 Enterprise 用户默认
effort=high”的时候，你看到的就是这个经济矛盾被产品化的过程：把全速
reasoning 重新包装成一个更贵的付费档位，让 subscription 用户和
enterprise 用户在同一个工具里拿到不一样的 runtime 默认值。

这条规律不专属于 Anthropic。Cursor 在 2025 年中改成 credit-based
计费、引入 auto mode，是同一面墙的另一种撞法。OpenAI 用 reasoning effort
切档应对同一个问题。任何采用固定价格 subscription 模式的 LLM 工具，在
power user segment
都会迟早走到这一步。模型权重的边际成本太高，subscription
价格的弹性又太小，runtime 层就成了厂商唯一可以悄悄调节的旋钮。

这是第二条值得固化的直觉：你今天用得很顺手的任何 AI agent
工具，六个月之后大概率会以你看不到的方式被悄悄调低。这件事不是道德问题，是经济学问题。基于这个假设建工作流，比基于”工具会一直保持现在这个表现”建工作流要稳得多。具体形式可能是默认
reasoning 调低、可能是 context window 收紧、可能是 retry
次数减少、可能是某个隐藏 cap 被默默引入。但方向是一定的。

## 隐性变化和”用户错觉”之间只隔一层 audit log

第三条直觉是关于为什么这种 runtime 层降级可以持续这么久才被打穿。

时间倒回 2024 年 11 月，Lex Fridman 问过 Dario Amodei
一个非常具体的问题：为什么用户老说 Claude 变笨了。[Dario
当时的回答](https://lexfridman.com/dario-amodei-transcript/)是，这种抱怨是常态，模型大多数时候没变。这句话在当时听起来是合理的，因为用户拿不出证据。所有的”变笨”投诉在历史上几乎全都停留在三种证据形态：体感描述、孤例截图、或者第三方
benchmark 跑分。前两种太弱，最后一种又有 saturation 和 contamination
的问题。厂商完全可以把所有抱怨都归为体感偏差或者 prompt 质量问题。

但是 Anthropic 自己后来在 [2025
年 9 月的一份 postmortem](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues) 里写过一句很关键的话：他们的内部 eval
没有捕捉到用户报告的退化。原因是 Claude
在单步失败之后恢复能力很强，所以从 pass rate 这种 outcome metric
看不出问题，但用户在长会话和多步骤任务里会积累大量中间步骤的细微质量下降。这件事说明，“benchmark
看起来正常”和”用户体感变差”可以同时为真，而且正是 agentic AI
这一代工具最常见的失败模式。Stella 的 issue 发出来的同一时期，[Marginlab 的 Claude
Code daily benchmark tracker](https://marginlab.ai/trackers/claude-code/) 还显示 Nominal
状态，恰好印证了这个落差。

之所以这次的剧情终于不一样，是因为 Stella 用的不是
benchmark，也不是体感。她用的是她自己机器上的 audit log。Claude Code
把每一次 session 的完整 transcript 以 JSONL 格式保存在
`~/.claude/projects/` 目录下。每个 thinking block、每个 tool
call、每个 prompt、每个 model response 都在那儿。这不是 Anthropic
故意给的一个监控接口，而是 Claude Code
早期为了方便开发和调试做的一个产品决策，结果意外地让每一个 daily
用户手里都拥有了一份完整的 AI 工具行为审计材料。Stella
做的事情，本质上是把这份本地 audit log 跑了一次反向统计分析，让 runtime
层的隐性变化第一次以可复现、带时间戳、跨数千 session
的方式呈现出来。

这件事在 OpenAI 和 Cursor 这类把 session
数据存在云端的工具上是做不到的。Codex CLI 跟 Claude Code 类似，把
session 存在本地，所以原则上也能做。但目前为止，Claude Code
是第一个被这样反向审计的 agentic AI 工具，Stella
是第一个跑通这套方法的人。

第三条直觉因此是这样的：真正决定一个 AI
工具能否被外部问责的，不是它的 changelog
透不透明，不是它的客服回不回邮件，而是它有没有把行为数据交到用户手里。如果你在选
AI 工具，把”它是否在本地保留完整的可读 audit
log”作为一个评估维度，比关心它跑了多少 benchmark
重要得多。这件事在工具好用的时候你感觉不到价值，在工具悄悄变差的时候它是你唯一能拿出来的硬证据。

## 几个不那么重要但值得知道的事实

把上面三条直觉讲完之后，剩下的细节就只剩下一些可以快速带过的事实。

一个是关于 Boris Cherny 的回应。他在 GitHub issue 上把退化归因到
effort=85 默认值，建议 Stella 用 `/effort high`
调回去。Stella 回复说她团队早就在用 effort=max 了还是不行。Boris 后来在
HN 上换了一个说法，承认 adaptive thinking 在某些 turn 把 reasoning
分配到了零，建议改用
`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`。同时 issue
被关闭为 completed。这种”承认 bug 但 close issue”的组合在 [Reddit
上的讨论](https://www.reddit.com/r/ClaudeAI/comments/1ses1qm/anthropic_stayed_quiet_until_someone_showed/)里被总结成一句话：Anthropic
应该少花点力气让这种降级更难被看见，多花点力气真的修模型。

另一个是关于 Stella 不是孤例。从 3 月初开始，[Yan
Gao 的 Substack](https://alphaguruai.substack.com/p/whats-going-on-with-claude-code) 已经在做时间线整理，独立博客和 Reddit megathread
都在同一个方向上累积证据。但所有这些都停留在描述层面，Stella
是第一个把它量化的人。[InfoWorld
引用 Greyhound Research
的分析](https://www.infoworld.com/article/4154973/enterprise-developers-question-claude-codes-reliability-for-complex-engineering.html)里有一句话讲得比我准：这种降级不会让用户一夜之间全部走人，它的危险在于它是一种
quiet shift，让那些把 AI agent
用在严肃多步骤工作上的团队对系统的信任慢慢腐蚀。

还有一个是关于历史模式。Anthropic 已经走过这套流程很多次：2025 年 8
月到 9 月的 infra 三 bug postmortem，影响了大约 30% 的 Claude Code
用户；2025 年 12 月一个月内五起独立 incident；2026 年 1 月底一次 harness
rollback；现在这次。每一次都是 bug，每一次的 bug
也都真实存在，每一次承认都落后于社区抱怨数周到数月。pattern
这么稳定的话，下次再来的时候你应该已经知道怎么处理了。

## 今天就能做的缓解

在继续讨论更抽象的判断之前，先把最实用的部分讲完。Anthropic
这次不太可能主动再做什么动作（issue 已经 close 为 completed，changelog
里一个字没提），但 Boris 自己在 HN 上就给了两个 flag，你今天加到 shell
配置里就能立刻拿回来大部分丢失的推理深度。

```
export CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
```

这是最重要的一个。它禁用 adaptive thinking 机制，强制模型每个 turn
都用固定的 reasoning 预算，而不是让模型自己决定想多久。Stella
在她的数据里发现问题最严重的场景恰好是 adaptive thinking 把某些 turn 的
reasoning token 分配到了 0，Boris 在 HN
上也亲口承认了这一点。禁用之后这种”某些 turn
直接不思考”的行为就不会再出现。HN 上多个用户确认过这个 flag
单独就能带来显著差异。

另一件事是在 Claude Code session 里手动把 effort 调到最高：

```
/effort max
```

这是 session 级别的设置，每次起一个新会话可能都要重输一遍。它把
reasoning 预算的上限从 medium（effort=85）抬回到
max。这两件事是正交的：`/effort max`
提高上限，`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`
禁止在上限以下随机分配。单做 effort=max 不够，因为 Stella
的数据采集时她就是在 effort=max
前提下跑的，问题照样存在；两个一起做才能拿回真正的默认行为。

这两个 workaround 都是 Anthropic 自己给的，不是什么
hack。但值得注意的一点是：这意味着 Claude Code 的”真正的 power user
默认行为”现在需要你主动
opt-in，而新用户拿到的仍然是被悄悄调低过的默认值。这件事本身就是这次事件最值得记住的东西——runtime
层的默认值已经和六个月前不是同一个东西了，而且以后可能还会再变。下次再觉得不对劲的时候，先检查
Anthropic 有没有又加了什么新 flag 需要你 opt-in。

## 结语

Stella 的 issue 被关闭、Boris 的解释被部分接受、adaptive thinking 的
bug 估计会在下一个 Claude Code 版本里被悄悄修掉，这件事在 Anthropic
内部大概会以一份事后报告或者一段 release notes
的形式消化掉。但对所有重度使用 AI agent
工具的人来说，这次降智事件不应该只留下一个”Anthropic
又出问题了”的印象。

值得带走的是三个判断，按重要性递减。第一，今天的 AI agent
工具在模型和你之间多了一个 runtime
层，它天然不透明，做技术选型的时候要把它当独立维度来评估。第二，subscription
模式的 LLM 工具在 power user segment 一定会撞到经济学的墙，runtime
层的隐性降级是这堵墙最常见的撞法，所以不要假设你今天用得顺手的工具六个月之后还是同一件东西。第三，工具有没有把行为数据以可读格式留在你本地，是你将来唯一能拿来反向问责的杠杆，这件事比任何
benchmark 都重要。

这三条直觉里没有一条是关于 Claude Code 本身的。它们适用于
Cursor、Codex
CLI、Aider、Cline、OpenCode，适用于今天还没出现的下一代工具。Stella
这次事件最大的意义不是发现了一次降智，而是给所有 builder
留下了一个新的认知坐标：你跟 AI 模型之间，从此多了一层东西。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
