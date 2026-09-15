---
title: "关于 Anthropic Project Glasswing，AI\n从业者最需要知道的几件事"
date: 2026-04-07
source: https://yage.ai/share/anthropic-glasswing-ai-builders-20260407.html
slug: anthropic-glasswing-ai-builders-20260407
lang: zh
---
# 关于 Anthropic Project Glasswing，AI 从业者最需要知道的几件事

发布于 2026 年 4 月 7 日 · [查看原网页](https://yage.ai/share/anthropic-glasswing-ai-builders-20260407.html)

2026 年 4 月初，Anthropic 公布了 [Project
Glasswing](https://www.anthropic.com/glasswing)，宣布了一个名为 Claude Mythos Preview
的前沿模型。社交媒体上到处在讨论它。如果你是一个 AI 从业者或
builder，你大概率想搞清楚三个问题：Anthropic
是不是发布了一个我今天就能用的新模型？如果不是，为什么所有人都在谈论它？以及，我的认知需要做什么调整？

先说最直接的答案。Mythos Preview 没有公开 API，没有定价页面，没有
playground。你不能调用它，也不能把它集成到你的产品里。Anthropic
明确表示这个模型不会面向公众开放。所以不，这不是一次你需要立即评估并接入的模型发布。

那为什么所有人都在谈论它？因为 Anthropic
声称这个模型在发现和利用软件漏洞方面的能力已经超越了绝大多数人类安全专家，并且认为这种能力足够敏感，以至于需要为它设计一套不同于常规模型发布的机制：受限访问、防御性合作伙伴联盟、延迟披露、90
天后公开阶段性报告。换句话说，Glasswing
引起关注不是因为有新工具可以用，而是因为一家主要的 AI
实验室公开把“更强的编程模型”当成了需要特殊治理安排的能力来处理。

这对 AI builder 意味着什么？前沿编程 AI
可能正在分化为两条路径。一条是我们熟悉的：面向广大开发者的通用编程助手，竞争维度是速度、上下文窗口、工具集成、价格。另一条是
Glasswing
所预示的：面向安全基础设施的受限能力系统，竞争维度变成了访问治理、披露协议、合作伙伴网络和防御部署的可信度。即使你的日常工作和网络安全完全无关，这个分化本身也传递了一个重要信号：当编程模型的能力达到一定水平，它的发布方式、访问层级和责任分配都会被重新定义。这与过去
AI-native
开发讨论中的一个核心洞察一致——真正的资产不是代码本身，而是评估、验证和编排代码的能力。Glasswing
只是把这个逻辑放到了一个风险更高、后果更重的场景里。

## Anthropic 到底在说什么

根据 [Glasswing
官方页面](https://www.anthropic.com/glasswing)和 [Red Team
技术博客](https://red.anthropic.com/2026/mythos-preview/)，Anthropic 的主张可以分为三层。

第一层是能力声明。Anthropic 称 Mythos Preview
已经发现了数千个高严重性漏洞，覆盖所有主流操作系统和浏览器，其中超过 99%
尚未修补。Red Team 博客给出了具体案例：一个存在 27 年的 OpenBSD
bug、一个 16 年前的 FFmpeg 漏洞、FreeBSD NFS 远程代码执行、多个 Linux
特权提升链。在公开基准上，Mythos Preview 在 CyberGym 漏洞复现测试中得分
83.1%（对比 Opus 4.6 的 66.6%），SWE-bench Pro 77.8%（对比
53.4%），Terminal-Bench 2.0 82.0%（对比 65.4%）。

第二层是因果归因。Anthropic 明确表示 Mythos Preview
没有专门为网络攻击训练。这些能力来自代码理解、推理和自主执行能力的综合提升。换句话说，Anthropic
的判断是：足够强的通用编程模型会自然涌现出网络攻防能力。

第三层是部署决策。基于以上两层，Anthropic
走了一条完全不同于常规发布的路径。Mythos Preview
不公开发布，取而代之的是一个防御性部署联盟，成员包括
AWS、Apple、Broadcom、Cisco、CrowdStrike、Google、JPMorganChase、Linux
Foundation、Microsoft、NVIDIA 和 Palo Alto Networks。Anthropic 承诺最高
1 亿美元使用额度和 400 万美元直接捐赠给开源安全组织，并将访问权限扩展到
40 多个维护关键软件基础设施的机构。Anthropic 计划先在即将发布的 Claude
Opus 模型中部署防护措施，再考虑更广泛的能力释放。

## 对 AI builder 的实际意义

在消化完 Anthropic
的具体声明后，值得把视角拉回来，看看这件事对不同角色的实际含义。

对安全团队和关键软件维护者来说，信号最直接。如果 Anthropic
的能力声明哪怕部分属实，AI
辅助的漏洞发现就已经从实验阶段进入了实用阶段。防御者需要开始评估如何将这类能力纳入自己的安全工作流，而非等到这些工具公开可用时再被动应对。

对平台和基础设施公司来说，Glasswing
暗示了一种新的合作模式。与传统的安全漏洞赏金计划不同，这里是模型提供者主动选择防御性合作伙伴，并在信息披露前建立协调机制。这种模式是否会成为前沿
AI 实验室的标准做法，值得关注。

对普通开发者和产品构建者来说，短期内不需要做什么具体的事。但
Glasswing 提供了一个有用的思考框架：编程 AI
的演化路径不只是”更好用的工具”这一条线。当能力到达一定水平，它会触发新的制度安排、新的访问层级和新的责任分配。如果你在构建
AI-native
的产品或工作流，理解这种分化趋势有助于更准确地判断自己所依赖的模型能力在未来的可获得性和使用条件。

## 保持校准：三个值得追问的地方

以上分析主要围绕 Anthropic
构建的框架展开。在接受这个框架之前，有几个地方值得保持警觉。

模型能力是否是决定性变量？[Suzu
Labs
的分析](https://suzulabs.com/suzu-labs-blog/claude-mythos-and-the-cybersecurity-risk-that-was-already-here/)提出了一个有分量的反论点：在真实的攻防场景中，基础模型的能力固然重要，但
scaffolding（围绕模型的执行框架）和工作流设计可能同样关键。一个中等能力的模型配合精心设计的攻击框架，未必比一个更强的裸模型弱。同样，防御端的效果也高度依赖于将模型嵌入漏洞扫描、分类、修复验证工作流的工程质量。Anthropic
的叙事集中在模型跨过了某个危险阈值，但真正的杠杆点可能更分散。

Anthropic
的能力声明目前几乎完全来自第一方。基准数字和具体漏洞案例都出自官方材料。[系统安全卡](https://www-cdn.anthropic.com/53566bf5440a10affd749724787c8913a2ae0841.pdf)确认
Anthropic
进行了标准安全评估，也承认模型在规避防护措施方面仍有残余能力。但由于
Anthropic 称 99%
以上的发现尚未修补，外部目前无法独立验证这些漏洞的数量和严重性。部署决策本身（合作伙伴名单、限制发布政策、资金承诺）是可验证的事实，这些不需要信任
Anthropic 的自我评估就能确认。

Glasswing 的公开时机也值得留意。[Fortune
的报道](https://fortune.com/2026/03/27/anthropic-leaked-ai-mythos-cybersecurity-risk/)指出 Mythos 相关的内部资产在正式公布之前就意外泄露。[The
Atlantic 的报道](https://www.theatlantic.com/technology/2026/03/pentagon-anthropic-dispute/686307/)则将 Glasswing 置于 Anthropic
与五角大楼之间更大的定位博弈中。这些信息并不否定 Glasswing
的实质内容，但提醒我们：受限发布和防御联盟的包装同时服务于安全目标和品牌叙事，区分两者的权重有助于更准确地评估整件事的意义。

## 90 天后再验证

Anthropic 承诺在 90 天内公开报告 Mythos Preview
发现的漏洞和改进措施。这是所有现有判断最重要的验证窗口。届时可以检验的核心问题包括：公开披露的漏洞数量和严重性是否支撑”数千个高严重性发现”的声明？已修补的
CVE
是否可被独立安全研究者复现和评估？防御性合作伙伴的反馈是否证实了实际的安全改善？

在那之前，Glasswing 对 AI builder 的主要价值在于认知更新：一家头部 AI
实验室已经认为，至少在某些高风险场景里，编程模型需要不同于常规产品发布的治理机制。无论
Anthropic 对具体能力的判断最终被验证到什么程度，这个方向本身——前沿编程
AI
不再只是开发工具，也越来越像需要制度化管理的基础能力——都值得每一个构建
AI 系统的人认真对待。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
