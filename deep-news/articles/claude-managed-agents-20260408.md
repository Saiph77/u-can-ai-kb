---
title: "Claude Managed Agents：Anthropic 想替你管 agent"
date: 2026-04-08
source: https://yage.ai/share/claude-managed-agents-20260408.html
slug: claude-managed-agents-20260408
lang: zh
---
# Claude Managed Agents：Anthropic 想替你管 agent

发布于 2026 年 4 月 8 日 · [查看原网页](https://yage.ai/share/claude-managed-agents-20260408.html)

调研日期 2026-04-08，发布当天。

## 一句话

今天 Anthropic 发布了 [Claude Managed
Agents](https://claude.com/blog/claude-managed-agents)。你写一个 agent
的定义——模型、prompt、tools、MCP、skills——交给 Anthropic，它帮你在自家的
sandbox 里运行 session，按 runtime 小时加 token 收费。官方 tagline 是
“build and deploy agents 10x
faster”，客户引语都在说”几天而不是几个月”，看上去是一个”让开发者少操心基础设施”的产品。

读完所有材料以后，我的判断是：这个产品帮你省事是副作用，让 Anthropic
而不是 AWS 握住 agent
这层的入口才是主线。你用不用它，实际上是在选一件事——愿意把 agent 的
operational state（credential、memory、session 历史）托管在 Anthropic
那里，换取几周不用写的 plumbing 代码；还是继续自己管这些东西，换取不被
Claude 绑住的自由。

这个选择本身不新，所有云服务都是这笔账。新的是它把”agent”这一层变成了这笔账的新战场。

## 产品本身

最快的理解方式是拿一个具体场景走一遍。假设你想给自己的 SaaS
产品加一个”研究助手”——用户扔一个问题进来，agent 能搜网页、读你们内部的
wiki、整理出一份报告回去。这件事过去要你自己干：租一台 container、写
agent loop、管会话状态、配 credential、做 tracing。MA
的存在是让你从头到尾都不碰这些东西。

你打开 Anthropic 控制台填一张表：agent 用 Claude Opus 4.6，system
prompt 是”你是研究助手”，工具是 web search 加你自己的一个 MCP
server，skills 装上你写的那个”公司 style guide”。表交出去，你拿到一个
agent ID。这是第一个概念，叫 **Agent**——它就是你对”这个 AI
是什么、会做什么”的完整声明，一个静态对象。

然后你告诉 Anthropic 这个 agent 要跑在什么样的环境里：预装
`pandoc` 和 `weasyprint`，容器只许访问
`api.mycompany.com` 和 `serpapi.com`，其他 host
都封掉。你拿到一个 environment
ID。这是第二个概念，**Environment**——一个 container
模板。它和 agent 分开是因为同一个 agent
可以在不同环境里跑，比如生产环境和 staging 环境走不同的 host
白名单。

用户一来，你创建一个 session，把 agent ID 和 environment ID
一起扔进去。Anthropic 那边起一个容器，你的 agent
就在里面活过来了。这是第三个概念，**Session**——一次具体的运行实例。你的应用和这个
session 之间走一条 SSE 通道来回传消息，这些消息叫
**Events**，也是第四个概念，全部在服务端持久化。你的 web
服务器挂了也没事，重连接着跑。用户关了浏览器，session 进
idle，不计费。下次他回来，session 继续，对话状态不用你自己管。

走完这一遍你会注意到两件事。第一件是：**整个过程你没写一行
agent loop**。模型什么时候调 web
search、调用失败怎么重试、context 太长怎么
compact、对话历史存哪——这些决定都是 Anthropic 的 harness 替你做的。这是
MA 的核心卖点。第二件是：**credential 是放进一个叫 vault 的
write-only 存储的**，agent 运行时能用但读不到原文；每一次 tool
call 都写进 event stream，在 Console 里变成一条可审计的时间线。这是 MA
的 governance 卖点。

但同样在这套流程里，有两件官方没大声说的事值得你看一眼。

一是 `agents.update` 这个 API 没有审批。你的 agent
定义本身是 immutable 的（每次更新都发一个新版本号），但任何拿到你 API
key 的人都可以直接发 update 改 system prompt 和 tool 清单。Anthropic
在自己的 [cookbook](https://platform.claude.com/docs/en/managed-agents/overview)
里承认这是个 tradeoff，让调用方自己用版本号 pinning 和 PR review
补上这层保护。对金融、合规、高风险场景，这个洞要在集成时显式堵上。

二是 MA 最吸引人的三个功能今天都在 research preview，没有 GA
时间表。**Outcomes** 是其中最像 demo 的那个——你写一份
rubric，Claude 自己迭代到 rubric 被满足为止。官方 blog 里反复强调的”让
Claude 自己迭代直到任务完成”就是这个功能，今天你用不到。另外两个是
**Multi-agent orchestration**（目前只支持单层
delegation，不能 agent 套 agent 套 agent）和 **Memory**（跨
session 的持久记忆）。发布日能跑的是编排 harness 和 governance
基础，最出片的能力留在门后。

定价只有一行，定义留得很松。blog 原文是
`standard Claude Platform token rates apply, plus $0.08 per session-hour for active runtime`，TheNewStack
的[独立报道](https://thenewstack.io/with-claude-managed-agents-anthropic-wants-to-run-your-ai-agents-for-you/)补了两个细节：idle
time 不算钱，web search 额外 $10 每 1000 次。Anthropic 的 pricing docs
页面到今天都还没有 Managed Agents 的章节。`active runtime`
到底按秒、按分钟还是按小时向上取整，`rescheduling` 状态算不算
active，这些 docs 都没写。

## 为什么说这是 Anthropic 的入口战

把产品的”它帮你做了什么”放一边，换一个角度：Anthropic
选在这个时间点做这件事，是在解决什么问题？

按时间看 Anthropic 是四家大厂里最晚下场的。[AWS
Bedrock AgentCore Runtime](https://builder.aws.com/content/3BfYvUNKt1db2KOxfT2j9SOPVsX/choosing-between-managed-vs-modular-ai-agents-amazon-bedrock-agents-vs-amazon-bedrock-agentcore) 2025 年 10 月 GA，OpenAI AgentKit 加
Responses API 差不多同期，Google Vertex Agent Engine
也已经到位。Anthropic 晚了半年。这个 delay 不是技术没准备好，Claude Code
早在 2025 年 2 月就有完整的 agent runtime 了，MA 的 harness 大概率就是从
Claude Code 里抽出来的。

真正解释时机的是两件挨得很近的事。

第一件是财务。公开报道里 Anthropic 2025 年前 9 个月给 AWS 付了 26.6
亿美元的 compute，超过同期 revenue，2024 gross margin 大约
-94%，对投资人的承诺是 2028 做到
77%。这条曲线要走通，必须从某处收回毛利。Claude Code 在 2025 年末做到约
10 亿美元 ARR，2026 年初到 25 亿美元以上，证明了”比 raw API
更高层级的产品”确实能把毛利拉起来。MA 是同一个逻辑的第二次发球，从”卖
token”升级到”卖 runtime 加 token”。

第二件是平台控制权。MA 发布的 4 天前，Anthropic 切断了 [OpenClaw](https://yage.ai/openclaw.html) 和几个类似的第三方
harness 通过订阅计划接入 Claude
的便宜通道。两件事挨这么近不像巧合。合理的读法是：先关闭”用我的 token
跑你的 harness”那条价廉路径（这条路径上 Anthropic 拿不到 runtime
的钱，也控制不住 agent 的交互形态），再开放”用我的 harness 在我的
runtime 上跑”的官方路径。一堵一疏，同一个动作的两半。Hacker News
发布日讨论里有人直接点出了这个动机（[47693047](https://news.ycombinator.com/item?id=47693047)，用户
cedws）：

> “Anthropic wants to shift developers on to their platform where
> they’re in control. The fight for harness control has been terribly
> inconvenient for them. To score a big IPO they need to be a platform,
> not just a token pipeline.”

还有第三件事，更隐蔽一点。Claude Cowork 已经被 Microsoft 嵌入
Copilot，如果 Anthropic 没有自己独立的 platform
层，它面对的长期局面是”Claude 成为 Microsoft
产品里的一个模型选项”。MA、Claude Code、Cowork 这三层加起来，让
Anthropic 有了 consumer、developer 和 platform builder
三个自己直接掌握的入口，不必把分发权交给任何一家 hyperscaler。

把这三件事并排放：财务要改善毛利、产品要收回 harness
控制权、渠道要摆脱 hyperscaler 依赖。MA
同时解这三道题。“帮开发者省几个月基础设施工作”是卖点，不是动机。

## 省的事，到底省给谁

发布日有两个独立的声音值得并排读。

一个是 Hacker News 主线程上的 JLO64（[原贴](https://news.ycombinator.com/item?id=47693047)），一个用
Anthropic Agent SDK 在 Docker 里给客户做 Jekyll 站点生成服务的人：

> “I didn’t find it that difficult to set up the infrastructure, the
> hard part was getting the agents to do exactly what I wanted.”

另一个是瑞士开发者 Tamas Kaljuste 发布日晚上在 LinkedIn
上给了一个真实账单对比（[来源](https://www.linkedin.com/posts/claude_claude-managed-agents-now-in-public-beta-activity-7447693438180995072-AjCH)）。他把一个
newsletter agent 搬到 Managed Agents 上跑：

> “Managed Agent: 20+ minutes, $5+ burned. My same n8n workflow: runs
> in a few minutes, costs cents… Forcing a model to pause and ‘reason’
> through a strictly repeatable pipeline is a fundamentally expensive
> architecture.”

这两句话放在一起，MA 价值主张的边界就浮出来了。MA 想省掉的是”写
sandbox、checkpoint、credential 管理、tracing
的几周活”。对一个已经跑了生产 agent 的人，这几周活根本不是最大的坑——让
agent 做对事情才是。对一个把结构化流水线硬塞进 agent loop 的人，$0.08 的
runtime 只是皮毛，真正的账单来自”让模型在一条本来可以写死的路径上反复
reason”。20 分钟 5 美元不是 MA 贵，是 agent 架构本身对不上 workflow
automation 的成本模型。

所以 MA 实际服务的是一群很具体的人：还没建过 production agent
infra，但手里有一个现成的 SaaS 产品想加 agent feature。LinkedIn
和早期客户名单几乎全是这群人。bnchrch 在给一个小啤酒厂写 invoicing
agent，Dan Rooney 已经为 Google Ads / HubSpot / Peec AI 写了 custom MCP
server、但 orchestration 还是 duct tape，Notion 想让用户在 Notion 里委派
agent 做事，Sentry 想让 error 直接变成一个 PR。这些场景里 MA
省的东西都是真的。

HN 主线程那一群人是另一个画像：他们手上已经有
Docker、K8s、multi-model
pipeline，已经过了”搭基础设施”那个阶段。这一群人发布日的反应几乎统一是”我不会切过来”。主线程至少五个用户明确表态自己已经在跑
self-hosted 等价物——JLO64 的 Docker + SDK、rick1290 的 Pydantic AI 加
DBOS / Temporal、jawiggins 的 K8s-based Optio、\_pdp\_
在整理自己的开源版本、0o\_MrPatrick\_o0 的 multi-model 路由。Managed
Agents 对他们的吸引力是负的：省的东西他们已经有，代价（Claude-only
的绑定）他们承担不起。

mccoyb 在同一条 thread 上给了我觉得当天最尖锐的那一句：

> “Opus 4.6 on max does not hold a candle to GPT 5.4 xhigh in terms of
> bug finding.”

他的整个 production pipeline 是 Claude 做 planning、GPT 做 bug
finding、本地 Qwen 做简单操作。这种 mixed-agent 配置 MA
一个都支持不了。对这一类开发者，MA 的 value prop
不是持平、是负值——接受它意味着在每一个子任务上都要用次优的模型。

## Lock-in 在哪一层

MA 的 lock-in 有三层，值得分开看，因为它们迁移难度完全不同。

第一层是模型绑定。MA 只支持 Claude 4.5
及以上。这一层所有人都看得见。讽刺的是 Claude Agent SDK（self-host
路径）反而更开放，明确支持通过 Bedrock、Vertex、Azure 路由其他模型。

第二层是 API shape。Agent、Environment、Session、Events 这四个抽象是
Anthropic 私有的命名，跟 OpenAI 的 Responses API、Bedrock AgentCore 的
runtime 完全不兼容。迁移的时候你得重写 agent
loop，但至少代码是你的，重写工作量可估。

第三层是 operational state，也是最隐蔽的一层。独立博主 Dan Goodman 在
MA 发布前 12 天写了一篇 [预判文](https://danthegoodman.substack.com/p/where-agents-converge)
指出：model lab 真正的 lock-in 不在 API，在 context。managed
compaction、persisted session、跨 session memory——这些东西一旦托管在
Anthropic 那里，你想迁走要带的不是代码，是 state。Anthropic 没有官方的
export 工具。你 vault 里的 credential、memory store 里的跨 session
记忆、session 历史的完整 event stream、agent version
的演化记录，这些都是 MA 的真实 egress cost。

这一层比 cloud 的 egress fee 更难算。AWS 的 egress
至少是标价的，你知道自己被锁得多紧。context lock-in
是随运营时间累积的，你用 MA 跑 agent 半年以后，真正难迁走的是半年积累的
memory store 和 skill 配置，不是当初那几百行 agent 定义代码。

发布日 HN 上另一位用户 0o\_MrPatrick\_o0
给了一个具体的理由为什么他不愿意承担这层 lock-in：

> “Model reliability is transient. When the models have an off day, the
> workflows you’ve grown to depend upon fail. Build in multi-model
> support, so your agents can modify routing if an observer discovers
> variability.”

这不是”反垄断”的意识形态立场，是”我自己运营 agent 的时候被 Claude 的
off day 烧掉过一整天”的经验。MA 在架构上不给你这个逃生口。

## 一个需要修正的预言

这段是写给读过我之前两篇文章的读者的，不熟悉的读者可以跳到下一节。

[2025 年初写 Claude Code
的时候](https://yage.ai/claude-code.html)，我的判断是它是 AI-Native
软件开发的一块关键拼图，推动”Library as a
Service”这种新范式——让每个软件库都变成 AI 可以直接调用的 agent。MA
把这个方向再推了一步：让你的库以 managed agent
的形态对外提供服务，Notion / Asana / Atlassian 的案例就是这个模式的
proof of concept。从 LaaS 的角度 MA 是在预期的路径上。

但同时我在[关于 Agentic AI
框架的那篇文章](https://yage.ai/why-forget-all-frameworks.html)里写过一个更底层的预测：“未来，Agentic AI
的各个组件一定会尘埃落定，收敛出类似 Web 标准一样的通用接口。”
一年多后回头看，收敛确实在发生——四家大厂同期推 managed agent runtime
是最明显的信号——但收敛的方向跟预测不一样。收敛到的是各家的 proprietary
runtime，不是 open standard。MA 的 Agent / Environment / Session、OpenAI
的 Responses API、Bedrock 的 AgentCore Runtime，彼此都不兼容。MCP
是唯一的例外，因为它是 Anthropic 发起后捐给 Linux Foundation 的 tool
层协议，四家都支持。但 **agent 这一层本身没有 MCP
对应的开放协议**。A2A 是 Google 的，AG-UI 是 CopilotKit 的，MA
都不支持。

所以预言需要打个补丁。收敛在发生，时间点就是现在，但形态不是 HTTP /
MIME type 那种人人遵守的公共标准。形态是四五家厂商各自有一套 managed
runtime，中间靠 MCP 做浅层的 tool 互通，agent-to-agent
层还是一片没有共识的空白。

这个补丁的实际后果是：2026 年选 agent 的生产运行时，你做的决定比 2025
年选 LangGraph 还是 SmolAgents 更重。框架你可以改写，runtime 里的
operational state 不行。避免 lock-in
的代价也比一年前更高，因为自建要补的不止是 agent loop，还有
sandbox、vault、memory store
这些东西。两边都在加价，没有一个免费的选项。

## 三类读者分别该做什么

如果你已经在跑 agent 生产系统，用的是 Claude Agent SDK 加自己的
Docker / K8s / Cloud Run。**继续待着**。MA
现在没有能撬动你迁移的东西，等两件事发生以后再重新评估：Outcomes /
Memory / Multi-agent 三个 research preview 功能 GA 并且定价清楚，以及
Anthropic 提供 operational state 的官方 export
工具。两件事至少发生一件，才值得动。

如果你是 SaaS 产品团队，想在现有产品里加 agent 作为一个
feature，目标客群是普通用户而不是开发者。**MA
是当前最顺的选择**，前提是你接受 Claude-only 绑定。上手比
AgentCore 轻（不用自己决定 sizing），支持的 session 长度比 OpenAI
Responses API 的 20 分钟 container cap 长得多，比从零自建省几周
plumbing。Notion / Asana / Atlassian
出现在早期客户列表不是巧合。**现在就值得做的一件事**：在自己这边维护一个
agent 配置的 source of truth，把 vault content、memory store、skill
集合都放在 MA
之外的地方定期同步进去。这样未来想迁出，迁的是同步脚本不是运营历史。MA
的 API 支持这种做法。

如果你还没开始建 agent，正在评估选型。我的建议是**先别选
managed runtime**。用 Claude Agent SDK 在 Fly.io 或 Cloud Run
上跑一个最小可用的
agent，跑一两周，感受一下真实的瓶颈在哪里。绝大多数情况瓶颈不在基础设施，在让
agent 做对事。等你对这个体感清楚以后，再决定要不要接受某一家的 lock-in
换 managed 的便利。现在直接跳上 managed runtime
的风险是你用到的一半能力自建本来也能有，另一半你其实并不需要，但 lock-in
已经发生。

## 几个还没被回答的问题

发布日的信息不够验证几件事，值得在接下来一两周继续看。

一个是真实账单。Tamas Kaljuste 的 20 分钟 newsletter
测试是当天唯一一条独立行为数据，我们没有”我跑了 8 小时 coding agent
账单是 X 美元”这种端到端的复盘。这种数据通常在发布后 7 到 14
天出现。

一个是 migration
story。到今天为止所有客户引语都是”我们集成了”，没有一条是”我们从 X
迁过来”。没有人从 Bedrock AgentCore 切到 MA，也没有人从 self-hosted
切过来。这种缺席本身是信号，但需要等 migration 数据出现以后才能判断 MA
到底有没有吸引力拉到已经站队的客户。

一个是 Outcomes、Memory、Multi-agent 什么时候 GA，GA
的时候定价会不会变。这三个是 MA marketing
里最吸引人的东西，也是目前最不确定的。

一个是 MA 的 container
底层用什么技术隔离。文档只说”sandboxed”，Firecracker、gVisor、Docker
还是别的什么完全没提。AgentCore 明确写了 Firecracker microVM。对
compliance 场景这个答案需要写进合同，现在没有。

一个是 12 个月之内 MA 能不能做到 500 M 美元以上的 ARR。能，它就是
Anthropic 继 Claude Code
之后第二根独立的应用级产品支柱，毛利故事站得住。不能，它就是一个进度追赶的动作，重要但不决定
Anthropic
的命运。现在没人能回答这个数字，明年这个时候回头看就知道了。

---

### 主要来源

**一手资料** - [Claude Managed
Agents 官方 blog](https://claude.com/blog/claude-managed-agents) - [Managed
Agents docs overview](https://platform.claude.com/docs/en/managed-agents/overview) - [Managed
Agents quickstart](https://platform.claude.com/docs/en/managed-agents/quickstart) - [Claude
Agent SDK secure deployment](https://platform.claude.com/docs/en/agent-sdk/secure-deployment) — Anthropic 自己承认 “container minimum
cost roughly 5 cents per hour”

**独立报道与分析** - [The
New Stack: Anthropic wants to run your AI agents for you](https://thenewstack.io/with-claude-managed-agents-anthropic-wants-to-run-your-ai-agents-for-you/) - [Dan
Goodman: Where Agents Converge](https://danthegoodman.substack.com/p/where-agents-converge) — 发布前 12 天的预判文，lock-in
载体是 context - [Nicholas
Rhodes: Managed Agents for Small Business](https://nicholasrhodes.substack.com/p/claude-managed-agents-for-small-business) — solopreneur 视角的
$0.70/hour 算例

**独立社区反馈** - [Hacker News
发布日主 thread #47693047](https://news.ycombinator.com/item?id=47693047) - [LinkedIn
Claude 官方发布 post](https://www.linkedin.com/posts/claude_claude-managed-agents-now-in-public-beta-activity-7447693438180995072-AjCH) — Tamas Kaljuste 的 20 分钟 $5+ 成本对比

**竞品资料** - [AWS
Builder Center: Bedrock Agents vs AgentCore](https://builder.aws.com/content/3BfYvUNKt1db2KOxfT2j9SOPVsX/choosing-between-managed-vs-modular-ai-agents-amazon-bedrock-agents-vs-amazon-bedrock-agentcore)

**作者历史判断** - [被低估的 Claude Code：AI Native
软件开发的关键拼图](https://yage.ai/claude-code.html) - [为什么学习 Agentic
AI 的第一步是忘记所有框架](https://yage.ai/why-forget-all-frameworks.html)

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
