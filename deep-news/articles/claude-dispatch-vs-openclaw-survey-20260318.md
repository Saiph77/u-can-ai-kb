---
title: "Claude Dispatch 深度分析：Anthropic 的 OpenClaw\n应答，以及 AI Agent 平台分野的底层逻辑"
date: 2026-03-18
source: https://yage.ai/share/claude-dispatch-vs-openclaw-survey-20260318.html
slug: claude-dispatch-vs-openclaw-survey-20260318
lang: zh
---
# Claude Dispatch 深度分析：Anthropic 的 OpenClaw 应答，以及 AI Agent 平台分野的底层逻辑

发布于 2026 年 3 月 18 日 · [查看原网页](https://yage.ai/share/claude-dispatch-vs-openclaw-survey-20260318.html)

> Dispatch 和 OpenClaw 的根本分歧，不是开放还是封闭，而是谁拥有你和 AI
> 之间逐渐积累的默契。 一个把 agent 做成服务，把记忆锁在平台里；一个把
> agent 当基础设施，尽量让用户带走上下文。
> 它们争夺的核心不是模型，而是长期关系和控制权。

> 调研日期：2026-03-18 触发：Anthropic 于 3 月 17 日发布 Claude
> Dispatch（Cowork 子功能），Latent Space 当天以 Anthropic’s Answer to
> OpenClaw 为标题报道。结合此前的 [OpenClaw
> 深度分析](https://yage.ai/openclaw.html)（2026-02-14），本文从产品决策和 axiom
> 体系两个维度，拆解这次发布的底层逻辑。

## 1. 一句话背景

2026 年 3 月 17 日，Anthropic 发布 Claude
Dispatch：一条持久化对话线程，桌面端沙箱执行任务，手机端发指令，跨设备同步。Felix
Rieseberg 的描述很精确：one persistent conversation with Claude running
on your computer, message it from your phone and return later to
finished work。设置流程是扫 QR 码配对手机和桌面，5 分钟完成。

时间线上，OpenClaw 1 月底爆火，我 2 月 14 日发布 [OpenClaw 深度分析](https://yage.ai/openclaw.html)，同一天 Peter
Steinberger 宣布加入 OpenAI。3 月 5 日 Jensen Huang 在摩根士丹利 TMT
大会上称 OpenClaw 为有史以来最重要的软件发布。Anthropic 这边，Claude
Code 的 ARR 2 月已超 25 亿美元，刚完成 300 亿美元 G 轮融资，估值 3800
亿。在这个背景下发布
Dispatch，策略意图很清晰：巩固开发者生态，同时向非技术用户延伸，堵住
OpenClaw 正在打开的缺口。

多数分析到”封闭 vs 开放”就停了。但真正有意思的问题在更深处。

## 2. 谁拥有你和 AI 的默契

这是理解 Dispatch vs OpenClaw 整个竞争逻辑的核心钥匙。

先说一个观察。OpenClaw 博客里分析过的飞轮（统一入口 → 数据汇聚 →
记忆复利 → 更懂你 →
更多使用），本质上是在构建一种东西：默契。你用得越多，AI
越了解你的偏好、习惯、决策模式。这种累积的上下文带来的竞争优势，远超模型本身的原始智能提升。一个”熟悉你的”次等模型，在实际工作中往往比”陌生的”顶级模型更有价值，因为它知道你的会议应该用什么格式，知道你给客户写邮件的语气，知道你上周的那个决定意味着这周的方案应该怎么调整。

Dispatch 和 OpenClaw 都在构建这种默契。区别在于：谁拥有它？

OpenClaw 的默契归用户所有。MEMORY.md、USER.md、SOUL.md 都是本地
Markdown 文件，用户可以 Git
版本控制、手动编辑、迁移到其他系统。记忆的格式是人类可读的。即使
OpenClaw 项目死了，这些文件仍然有价值。

Dispatch 的默契归 Anthropic 所有。Claude Memory 存储在 Anthropic
服务器上，用户可以查看和删除，但无法导出完整的结构化记忆并迁移到其他系统。如果用户从
Claude 切换到 GPT，积累的默契就丢失了。

这个所有权差异带来了一个重要的非线性效应。切换 AI
系统的成本和使用时间的关系是非线性的：用了一周，切换成本低；用了一年，切换成本巨大。因为在这个过程中，你积累的远远超过
AI 对你的了解，还有你对 AI
的了解：知道它的强项和弱点，知道怎么表达它才能准确理解，知道什么任务可以放心交给它。这种双向的默契无法轻易转移。

Dispatch
的商业模式恰好利用了这个非线性：用的时间越长，积累的默契越深，切换的损失越大，锁定效应越强。这在商业上是天才设计，但对用户来说是需要清醒认识的风险。

OpenClaw
的默契外化为文件的做法，实现了理想中的第一步：把隐含的理解捕获为显式的、可迁移的记忆。但
OpenClaw 的自动蒸馏机制（heartbeat 自动整理记忆）又引入了 OpenClaw
博客中批评过的问题：更新过程是黑盒，你不知道它为什么删掉了某条记忆，为什么把两个不相关的东西合并在一起。知识没法显式管理。

理解了默契所有权这个视角，Dispatch 和 OpenClaw
的很多设计选择就有了更深层的解释。Dispatch 为什么选择自有 App
入口而非接入
WhatsApp/Slack？为什么选择服务端记忆而非本地文件？为什么锁定 Claude
模型而非开放多模型支持？这些选择表面上各有各的理由（安全、合规、体验一致性），但它们共同的效果是：确保默契只能在
Anthropic 的生态里积累，只能被 Anthropic 的产品消费。Epsilla
的分析说得很直接：企业 AI SaaS 平台 80%
的营收依赖于管理面板、用量分析、合规审计这些功能，这些功能的前提是平台能够访问用户数据。如果把记忆做成本地文件，这些服务就无法提供。换言之，封闭记忆系统是商业模式的必然要求。

而 OpenClaw 的每个设计选择都在朝反方向走。50+
消息平台接入、model-agnostic
架构、本地文件记忆、Skills-as-Markdown，这些选择的共同效果是：降低用户的切换成本，让默契可以被用户带走。

从我们自己的实践来看（OpenCode + AGENTS.md + Mono
Repo），最理想的方案是默契外化为文件（可迁移、可版本控制），但蒸馏过程由用户主导（或至少可审查）。Dispatch
和 OpenClaw 都没有完全做到这一点。

## 3. Agent 是服务，还是基础设施

默契所有权的分歧，根源在一个更深层的问题：AI Agent 到底是什么？

Dispatch 的世界观是 Agent 是服务。在这个视角下，AI Agent
是一种由提供商托管、维护、保障安全的服务。用户的角色是消费者，提交任务、接收结果。服务质量由提供商保证，用户为此付费。这个世界观隐含的假设是：Agent
的行为边界应该由提供商的安全团队来定义。

OpenClaw 的世界观是 Agent 是基础设施。在这个视角下，AI Agent
是一层可以自建、自管、自改的系统。用户的角色是运维者或构建者，负责部署、配置、安全加固。Agent
的能力上限由用户的技术能力决定。这个世界观隐含的假设是：用户愿意且有能力为
Agent 的行为负责。

这两种世界观各自选择了配套的技术栈。Dispatch 用 Apple Virtualization
Framework 启动一个定制 Linux VM，内部再套一层 bubblewrap + seccomp
进程级沙箱，外加 OAuth MITM 代理和网络出口
allowlist，形成四层防御纵深。这套安全架构在 AI Agent
产品里是首次完整落地，从架构上消除了大量攻击面。OpenClaw 则是一个单进程
Node.js gateway，安全主要依赖可选的 Allowlist 和
ExecApprovalManager。两个高危 CVE（WebSocket Origin 验证缺失导致的一键
RCE，配置写入导致的命令注入）和 ClawHub 12-20% 的恶意 Skill
比例，都是这种轻量安全模型的直接后果。

但技术栈的差异只是表象。真正值得关注的是：这两种世界观在当前阶段都可能是错的。Agentic
AI 的基础概念还在快速演进，任何突破性理解都可能随时出现。

Dispatch 的服务模型有一个深层限制：它无法自我进化。Cowork 确实可以在
VM
沙箱内写代码并执行，但它产出的是一次性的成品（spreadsheet、报告、演示文稿），而非可复用的能力。没有
skill 保存和复用机制，每个 session 在工具层面都是从零开始。对比
OpenClaw，当 Agent 遇到没有现成 skill 可用的场景时，它会当场写一个新的
skill（Markdown
文件），保存下来，下次遇到类似场景直接复用。这个自我进化的闭环是
OpenClaw 真正牛的地方：它让 Agent
的能力上限随着使用时间持续增长。Dispatch 的 Agent
今天能做什么，明天还是只能做什么，除非 Anthropic 推送新功能。这是”Agent
是服务”这个世界观的结构性约束：服务的能力由提供商定义，用户只能等待升级。

OpenClaw 的基础设施模型则面临另一端的风险。安全事件正在升级（Palo
Alto Networks 的安全报告、ClawHavoc 攻击活动、两个高危
CVE），如果严重到足够的程度，社区可能被迫收紧权限，而这恰好会削弱让它强大的那些特性。

在快速演进的领域过早锁定世界观，代价很高。当你选择了一种框架，你用框架作者的视角看世界，如果后来发展出不同的理解，迁移成本可能比从头开始更大。这个判断在
AI Agent 领域格外适用：Android vs iOS
在诞生时面对的是一个已经基本稳定的智能手机使用范式（打电话、发短信、上网、装
App），差异主要在实现路径。而 Dispatch 和 OpenClaw
面对的是一个尚未稳定的范式：Agent
到底应该做什么、做到什么程度、安全边界在哪，这些基本问题还没有共识。两个平台都在押注自己的世界观最终会被证明正确。

## 4. 构建者 vs 消费者：能力上限由谁决定

世界观的分歧，在用户层面表现为一个实际的选择：你是想做构建者，还是做消费者？

OpenClaw 的整个设计都在鼓励构建者行为。Skills-as-Markdown
意味着用户（或 Agent 自身）可以随时写新能力，而且 Agent 在发现缺少现成
Skill
时会当场造一个，保存下来下次复用，形成自我进化的闭环。模型无关性意味着用户可以根据任务特性选择最优模型。ClawHub
从不到 3000 个 Skills 在几周内爆发到
17000+，就是社区构建力的直接体现。这些设计选择的共同效果是：OpenClaw
的能力上限取决于用户的构建投入。

Dispatch
的设计则在系统性地消除构建的必要性，同时也消除了构建的可能性。沙箱环境预配置好了，安全策略由平台决定，工具生态由
Anthropic 的 Partner-driven Skill Directory
管理（质量更高但增长速度慢一个量级），模型选择被锁定在 Claude
生态内。用户只需要说”帮我做 X”。这降低了门槛，但也意味着 Dispatch
的能力上限取决于 Anthropic 的产品决策，而非用户的投入。

这个分野呼应了 OpenClaw
博客中的核心论点：工具会过气，对工具本质的理解不会。选择 Dispatch
的用户获得了即时的便利，但放弃了通过构建获得深层理解的机会。选择
OpenClaw
的用户承担了更高的前期成本，但在过程中积累了可迁移的认知资产。换个角度说：Dispatch
的用户消费的是 Anthropic 的认知，OpenClaw 的用户积累的是自己的认知。

这里有一个微妙但重要的边界。并非所有构建都值得做。对于”只是想在通勤时让
AI 整理邮件”这类需求，Dispatch
的零构建成本就是正确答案。判断的关键在于：你是否有持续改进和深度使用
Agent
的意图。如果有，构建者路线的复利效应会随时间压倒消费者路线的即时便利。如果没有，消费者路线就够了。

这里还藏着一个悖论。降低入门门槛最有效的方式（封闭、简化、代替用户做选择）恰好会阻碍用户向深度使用演进。而为深度使用提供能力（开放、可组合、让用户做选择）又会提高入门门槛。Dispatch
和 OpenClaw 分别选择了这个悖论的两端。我们在 OpenCode + iOS Client
上做的事情，本质上是在悖论中找第三条路：用 OpenCode
提供构建者级别的可组合性，用 iOS Client 提供接近 Dispatch
的低门槛入口，用 AGENTS.md + Mono Repo 提供可控的记忆基础设施。

## 5. 三种架构哲学的竞争

把视角从两个产品拉到行业层面，2026 年 Q1 的 AI Agent
平台竞争已经形成了三个清晰的阵营。

**本地优先的激进简约派（OpenClaw 模型）。**
用户拥有一切：数据、记忆、模型选择权。安全由用户负责。社区驱动的 Skill
生态提供长尾覆盖。GitHub 三个月 20 万 stars，Jensen Huang
的背书让它成为开源 AI 项目的标杆。但安全问题已经开始反噬：Palo Alto
Networks 的安全报告、ClawHavoc 攻击活动通过专业文档包装的 Skills 分发
macOS 恶意软件、两个高危 CVE、明文存储的凭证。Steinberger 加入 OpenAI
后项目转交独立基金会，后续治理和安全投入存在不确定性。

**云优先的企业编排派（Dispatch/Anthropic 模型）。**
提供商保证安全和质量，用户交出控制权和数据。Claude Code 25 亿 ARR
证明企业市场愿意为此付费。Baytech Consulting
的客户调研表明企业的诉求正在转向 a ChatGPT that lives on our servers,
follows our rules, and never talks to strangers。但 Epsilla
的分析指出了结构性矛盾：企业 SaaS
的商业模式要求平台访问用户数据，这与真正的数据主权不可调和。

**混合主权派（第三条路）。** 用开放框架的灵活性 +
企业级的安全合规。Epsilla、cognipeer
等公司正在这个空间里构建编排层。我们自己用 OpenCode + iOS Client +
AGENTS.md
搭建的系统也属于这个阵营。优势是避免了前两者的极端化，劣势是没有现成的端到端产品，需要构建者自己组装。

MCP 协议在这个格局中的角色值得单独说一句。2025 年 12 月 Anthropic 把
MCP 捐赠给 Linux Foundation 下的 Agentic AI
Foundation，OpenAI、Google、Microsoft、AWS 都参与了共建。MCP 标准化了
Agent
连接工具的方式，但并没有解决”记忆归谁”“数据放哪”“用哪个模型”这些根本分歧。它是三个阵营都能采用的协议层，但不改变阵营之间的战略分野。HTTP
标准化了 Web 通信，但 HTTP 没有决定 iOS 和 Android 的竞争走向。

这三个阵营之间的真正技术分歧，在于看不见的基础设施层。

记忆基础设施方面，OpenClaw 有最完整的本地记忆体系（分层、向量 0.7 +
关键词 0.3 的混合检索、自动蒸馏），但可控性差。Dispatch
的记忆最薄弱（基本靠 context window + 服务端
Memory），但安全性最好。安全基础设施方面，Dispatch
的四层防御纵深领先一代。可观测性方面，MacStories 的实测显示 Dispatch
手机端返回结果的可靠性只有大约 50%，OpenClaw
的聊天窗口更差，只能看到”对方正在打字”。编排能力方面，两者大致持平。

谁先在记忆基础设施上实现”自动蒸馏 + 用户可审查 + 可版本控制 +
跨项目隔离”的完整闭环，谁就占据了下一阶段的先发优势。这个问题的重要性远超”Dispatch
好用还是 OpenClaw 好用”的表层比较。

## 6. 对我们意味着什么

回看 2 月 14 日的 OpenClaw 博客，核心论点是：OpenClaw
的设计决策是为最广泛用户群优化的结果，进阶用户应该提取可迁移的认知，在自己的工具链上构建更好的系统。

Dispatch 的发布从反面验证了这个判断。Anthropic
做的事情和我们做的事情在本质上一样：从 OpenClaw
的成功中提取关键要素（persistent conversation、cross-device
sync、always-on agent），然后在自己的基础设施上重新实现，在 trade-off
轴上选择了不同的位置。Anthropic 选了更靠近”安全可控”的那端（VM
沙箱、锁定模型、封闭生态），我们选了更靠近”灵活可构建”的那端（OpenCode +
Mono Repo + iOS Client）。

Dispatch 把”从手机远程控制桌面 AI Agent”的门槛从”需要搭服务器 + 配置
Docker + Node.js + WebSocket gateway”压缩到了”扫一个 QR
码”。这个能力之前完全存在（OpenClaw 做了同样的事，甚至 SSH + tmux +
Claude Code 也能实现），所以 Dispatch 的核心价值是成本压缩（专家级能力 →
大众可用），而非创造新可能性。值得提取的认知是：跨设备的持久化对话确实是刚需，QR
码配对 + VM 沙箱证明了这件事可以做得很简洁。但 Dispatch
的封闭性意味着它很难成为进阶用户的长期工具。对于已经搭建了自己系统的构建者，Dispatch
更有价值的角色是参考实现和竞争基准：看看 Anthropic
在同一个问题上做了什么选择、放弃了什么，然后反过来审视自己的方案是否在关键维度上做得更好。

最后回到那个 Android vs Apple
的类比。它在入口策略、生态模型、安全哲学上是准确的，但需要一个关键修正。Android
和 iOS 是在一个已知赛道上的路线之争。Dispatch vs OpenClaw
是在一个赛道还在修建的时候，就开始了路线之争。在领域基础尚未沉淀的时刻锁定世界观，风险很高。两个平台都在押注自己的世界观最终会被证明正确。历史告诉我们，最终胜出的往往是那些保持了最大适应性的选手。

毕竟，工具会过气，对工具本质的理解不会。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
