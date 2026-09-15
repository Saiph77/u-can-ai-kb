---
title: "AI Agent 的凭证问题，正在变成一个独立产品"
date: 2026-03-23
source: https://yage.ai/share/ai-agent-credential-product-20260323.html
slug: ai-agent-credential-product-20260323
lang: zh
---
# AI Agent 的凭证问题，正在变成一个独立产品

发布于 2026 年 3 月 23 日 · [查看原网页](https://yage.ai/share/ai-agent-credential-product-20260323.html)

## 摘要

2026 年 3 月，1Password 发布了 Unified Access，把人类用户、AI agent
和机器身份放进同一套凭证治理体系。这篇报告分析的不是这次产品发布本身，而是它背后一个更大的变化：当
AI agent 开始代替人类拿钥匙、调 API、跑流程、触发下游任务时，围绕 agent
身份和凭证的治理正在从一个附属功能，变成一个被单独包装和单独销售的产品模块。

核心判断：这件事已经被当成单独的产品在卖了，技术架构上的分化也比较清楚，但公开证据还不足以说明它已经成为企业单独拨预算采购的独立品类。它处在从功能到产品模块的过渡期。

## Agent 和人不一样：进门之后的事变复杂了

过去的安全模型有一个简单的假设：你登录一次，系统信任你，后续操作基本放行。这个假设能成立，是因为登录的人和用凭证做事的人是同一个人。你通过了身份验证，然后你自己去拿
API
key、连数据库、推代码。整个过程中，“谁登录”和”谁在操作”从来没有分开过。

Agent 把这两件事拆开了。现在的常见模式是：你登录，但 agent
代替你去拿凭证、调 API、跑工作流、触发下游任务。你在 Cursor
里写代码，Cursor 的 agent 需要访问你的 GitHub repo；你让一个调研 agent
去查数据，它可能需要用你的 API key 访问多个数据源；你让一个部署 agent
推代码，它可能触发 CI/CD 管线，管线里又有其他 agent
需要访问生产环境的数据库。

每一步都涉及凭证和权限，但操作者已经不是你了。更麻烦的是，agent
的行为模式和人完全不同：它可能在几秒内调用十几个
API，跨越多个服务边界，而且它的行为路径在启动前无法完全预测——它会根据中间结果动态决定下一步做什么。传统的”登录时验证一次就够了”的安全模型，在这种场景下开始失效。

1Password 在一篇架构博客中把这个变化描述得很准确：凭证不应该在 agent
启动时一次性发放然后就不管了，而应该在每次使用时根据当前上下文动态发放和验证（[1Password
架构博客](https://blog.1password.com/ai-security-runtime-controls)）。CyberArk 从另一个角度得出了类似结论：真正的安全风险不在
AI 模型回答了什么，而在 agent 持有身份、继承权限、调用工具、触发下游
agent 后形成的执行链（[CyberArk](https://www.cyberark.com/resources/blog/why-reducing-ai-risk-starts-with-treating-agents-as-identities)）。

用一句话概括这个变化：过去安全团队关心的是”谁在登录”，现在还得关心”谁的
agent、在什么时候、用了什么凭证、在什么背景下做了什么事、做完之后能不能查到”。控制点从门口挪到了每一次钥匙的使用现场。

## Agent 不是普通脚本：它正在成为一种新的数字身份

企业 IT 系统里一直存在”非人类用户”。CI/CD 管线用的 service
account、监控系统用的 API
key、服务器之间互相认证用的证书——这些东西存在已久，管理方式也比较成熟。它们的特点是长期存在、权限在配置时就定好了、行为路径可预测。一个数据库备份脚本永远就是做备份，不会突然决定去访问你的邮件系统。

AI agent 不一样。它的 session
是短暂的，任务结束就消失；它的权限是从发起任务的人那里临时继承的，不是自己固有的；它做什么事在运行时才决定，而且它还可能调用其他
agent，形成一条权限逐级传递的执行链。

这些差异大到不能只是在现有的管理方案上打个补丁。Strata Identity
在一篇分析中的总结很到位：“AI agents need their own identity playbook,
not just an extension of NHI management”——agent
需要自己的身份治理方案，不能只是把管理传统机器账号的办法拿过来套用（[Strata](https://www.strata.io/blog/agentic-identity/new-identity-playbook-ai-agents-not-nhi-8b/)）。

行业里对此有不同态度。Oasis Security 最激进，直接说自己是”the first
identity solution built for AI agents”，把 agent
身份和传统机器身份明确分开（[Oasis](https://www.prnewswire.com/news-releases/oasis-security-launches-agentic-access-management-the-first-identity-solution-built-for-ai-agents-302619375.html)）。CyberArk
最保守，倾向于把 agent 当作特权机器身份的自然延伸来管理（[CyberArk](https://www.cyberark.com/resources/blog/ai-agents-and-identity-risks-how-security-will-shift-in-2026)）。1Password
和 SailPoint 处在中间，承认 agent
有独特性，并为此做了专门的产品模块。

本报告的判断是：agent
和传统机器身份有继承关系，但差异大到需要专门的治理设计。这个判断也是理解后面厂商动作的前提。

## 管身份、管权限、管凭证：这几层分别由谁在做

要理解 1Password
这次发布为什么重要，需要先理解一个背景：安全行业里有几类公司，它们看上去都在做和”登录”“密码”“权限”相关的事情，但各自管的层不一样。如果你每天都在用
Okta 登录公司系统、用 1Password
填密码，但从来没想过它们到底有什么区别，这一段就是为你写的。

Okta
做的事情更像是公司的门禁系统。你早上打开电脑，点登录页面，输入账号密码或者扫一下指纹，然后就能访问公司的邮件、Slack、Jira、AWS
console 等一堆系统。“你是谁、你能进哪些系统”这个判断就是 Okta
管的。它的核心能力是身份认证和单点登录。SailPoint 和 Veza
也在这个方向，侧重点是权限的发现、审计和治理——不只是让你进门，还要确保你应该被允许进门，以及定期检查哪些人的权限该收回。

1Password
做的事情更像是钥匙柜。你进了门之后，实际操作各种系统需要具体的”钥匙”：登录数据库的密码、调用
API 的 key、连服务器的 SSH
key。这些钥匙怎么存、怎么拿、怎么安全地交给需要用的人或程序，就是
1Password 管的。它的起点是密码管理和 secrets vault。

CyberArk 管的是高权限账号的安全。企业里有些账号权限特别大：root
账号、数据库管理员、云平台
admin。这些账号泄露的后果比普通账号严重得多。CyberArk
专门管理这类特权身份，包括密码轮换、访问录像、即时权限授予。

HashiCorp Vault
管的是基础设施层面的密钥分发。你的应用需要连数据库、访问云服务、调用其他微服务，这些连接都需要凭证。Vault
的做法是动态生成这些凭证，用完即销毁，而不是在配置文件里写一个固定密码。它更偏向
DevOps 和基础设施团队使用。

这四类公司过去各管各的层，交集不大。一个简化的模型是：Okta
管”你能不能进门”，1Password 管”你进门以后用什么钥匙做事”，CyberArk
管”最危险的那几把钥匙”，HashiCorp
管”钥匙怎么自动造出来、用完怎么销毁”。

## 为什么 1Password 会从钥匙柜这一层切进来

理解了上面的分层，就能理解为什么 1Password
会在这件事上动作比较早。

Agent 的问题恰好发生在”进门之后拿钥匙做事”这一步。当越来越多的 AI
agent 开始代替人类去拿 API key、SSH
key、数据库密码来执行任务时，这些钥匙就存在 1Password 的 vault
里。它比任何人都清楚凭证在被谁、以什么方式、在什么时候使用。1Password
的一篇配套博客用了一句很准确的话：“Identity providers govern the front
door; 1Password governs what happens after”（[1Password
博客](https://blog.1password.com/credentials-dont-stop-at-sign-in)）。身份认证厂商管的是谁能进门，1Password
管的是进门之后拿什么钥匙、怎么用。

Agent
把这个”进门之后”的问题变复杂了一个数量级。过去凭证被人使用，频率低，上下文稳定。现在凭证被
agent 使用，频率高，上下文在每次调用时都可能变化，agent
还可能把凭证或权限传递给下游 agent。一个 agent 帮你写代码时需要访问
GitHub，写完后触发 CI/CD，CI/CD
又需要访问云资源——每一步都涉及不同的凭证和权限。

所以 1Password
做这件事不是因为它想转型做安全平台，而是因为它坐在凭证存储和分发的交叉点上。Agent
的兴起让它原本管的那层东西突然变得比以前重要得多，也复杂得多。它选择把这个问题产品化。

## 四条路径在从不同方向切入同一个问题

目前市场上至少有四条路径在同时切入 agent
身份和凭证治理。理解这些路径的区别是这篇文章希望你带走的可复用框架，它比记住任何一家公司的产品名都有用。

**从钥匙柜出发（vault-native）：1Password。**
它已经掌握了企业凭证的存储和分发，现在要做的是在凭证被使用的那个瞬间加上治理能力。优势是离凭证最近，知道什么凭证在什么时候被谁用了。局限是缺少身份图谱和策略引擎——它知道这把钥匙被拿走了，但对于”这个
agent 到底该不该有权限拿这把钥匙”的判断能力比 Okta 这类公司弱。

**从门禁系统出发（identity-native）：Okta、SailPoint、Veza。**
它们原本就在管”谁是谁、谁有什么权限”，现在要把 agent
当作一种新的身份对象纳入已有体系。Okta 在 2026 年 Showcase 中展示了面向
agent 的新能力（[Okta](https://www.okta.com/newsroom/press-releases/showcase-2026/)）。SailPoint
推出了独立命名的 Agent Identity Security 模块（[SailPoint](https://www.sailpoint.com/products/agent-identity-security)）。Veza
发布了 AI Agent Security，侧重 agent 权限的发现和治理（[Veza](https://veza.com/company/press-room/veza-introduces-ai-agent-security-to-protect-and-govern-ai-agents-at-enterprise-scale/)）。优势是身份生命周期管理和策略引擎成熟。局限是对凭证层面的运行时细粒度控制不如
1Password 深。

**直接为 agent
从零建产品（agent-first）：Aembit、Astrix、Oasis。**
这些是新公司，从第一天起就围绕 agent 身份治理来设计。Aembit 做 workload
之间的身份认证和即时访问控制（[Aembit](https://aembit.io/press-release/aembit-introduces-identity-and-access-management-for-agentic-ai/)）。Astrix
做 agent 发现和策略执行（[Astrix](https://www.prnewswire.com/news-releases/astrix-security-delivers-the-most-comprehensive-ai-agent-discovery-and-enhances-security-with-agent-policy-enforcement-302719653.html)）。Oasis
从 agent 生命周期的角度构建治理能力（[Oasis](https://www.prnewswire.com/news-releases/oasis-security-launches-agentic-access-management-the-first-identity-solution-built-for-ai-agents-302619375.html)）。这些公司的存在本身就是一个有价值的信号：如果
agent
身份治理只是传统产品里的一个附加功能，不会有这么多创业公司专门围绕它融资和做产品。

**从基础设施层出发（infrastructure-native）：HashiCorp、CyberArk。**
HashiCorp Vault 从 secrets engine 和 workload identity
的角度管理基础设施层面的凭证生命周期，重点是动态凭证生成和自动销毁（[HashiCorp](https://developer.hashicorp.com/vault/docs/concepts/cloud-access-management)）。CyberArk
从特权身份管理的角度把 agent 视为特权机器身份的自然延伸（[CyberArk](https://www.cyberark.com/resources/blog/ai-agents-are-forcing-a-reckoning-with-identity-and-control)）。

四条路径同时展开，每条路径都在向其他路径的核心能力区域延伸。这个格局本身传递的信息是：agent
身份治理的问题空间足够大，没有哪一家现有产品能独自覆盖全部。如果这个问题
Okta 加一个功能就能解决，不会出现这样的竞争态势。

## 1Password 这次具体发布了什么

把前面的背景讲完之后，回到这次具体的产品发布。

1Password 官方新闻稿把 Unified Access 称为”a new agent security
platform”（[新闻稿](https://1password.com/press/2026/mar/1password-unified-access)）。产品页的定义是”governing
credential access across humans, AI agents, and
machines”，列出了四个核心能力（[产品页](https://1password.com/product/unified-access)）：endpoint
discovery（发现企业环境中有哪些 agent
在使用凭证）、集中化的凭证存储与治理、runtime credential
delivery（凭证在 agent
每次需要时动态发放，用完收回）、统一的审计与归因（记录谁的 agent
在什么时候用了什么凭证做了什么事）。

官方博客的核心叙事是：传统的登录式安全模型在 AI
agent、自动化脚本、CI/CD
管线这些场景下会失效，因为权限应该在每次凭证使用时被重新确认（[博客](https://1password.com/blog/introducing-1password-unified-access)）。

新闻稿列出了一串合作伙伴：Runlayer、Natoma、Anchor
Browser、Browserbase 是 agent 执行环境；Perplexity Comet、Cursor 是 AI
工具；GitHub、Vercel 是开发者基础设施；还提到了与 OpenAI 和 Anthropic
的合作（[新闻稿](https://1password.com/press/2026/mar/1password-unified-access)）。需要注意的是，这些合作在公开信息中大多还停留在公告阶段，哪些已经变成真实的产品整合，目前无法完全确认。产品页列出的四大能力中，哪些已经全面上线、哪些仍在分阶段交付，也需要后续跟踪。

FAQ 中有一个关键定位：Unified Access “extends governance beyond
authentication”（[产品页](https://1password.com/product/unified-access)）。它没有说要取代
Okta
或重做身份认证，而是在认证完成之后加一层控制。这和前面分析的”钥匙柜层向上扩展”的逻辑一致。

身份和凭证治理是 agent 安全的基础层，但不是全部。Dark Reading
报道指出 AI agent 在实际执行中可能忽略安全策略（[Dark
Reading](https://darkreading.com/application-security/ai-agents-ignore-security-policies)）。围绕 MCP（Model Context Protocol，agent
调用工具时用的协议）的安全讨论揭示了 agent
和工具之间的连接层也存在信任问题（[Dark
Reading](https://darkreading.com/application-security/mcp-security-patched)）。Aqua Security 记录的 Trivy 供应链攻击说明 agent
的工具链本身也可以被攻击（[Aqua
Security](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know/)）。1Password Unified Access
覆盖的是凭证治理这一层，不是整个 agent 安全栈。

## 事实、推断与未决问题

这个话题容易滑向过度概括，所以需要把判断的依据和强度讲清楚。

**产品层面的证据最实在。** 1Password 已经把 Unified
Access
包装成独立的产品模块，有自己的产品页、定价入口和新闻稿，这不是一个藏在设置菜单里的小功能，而是被当成一个单独的产品在推。同时期，Okta、SailPoint、Veza、Aembit、Astrix、Oasis、CyberArk
都推出了独立命名的 agent identity 或 agent security
相关产品或模块。多个独立来源把 agent
场景的核心风险一致指向身份、权限委托、凭证治理和审计追溯，而不是 AI
模型输出本身。

**技术架构层面的证据比较充分。**
控制点从登录时刻移到凭证使用时刻，这个趋势在 1Password、CyberArk
和多家新兴公司的技术文档和产品设计中都有体现。Agent
身份的操作模式和传统机器身份确实不同，这一点多个独立来源交叉验证过。但这些判断仍然包含推断成分——技术趋势已经清楚，至于它会以多快的速度被企业广泛采纳，还要观察。

**预算和采购层面的证据最薄弱。**
有一些公司已经在单独评估 agent
身份治理方案，但这些还属于早期信号，公开数据不多。说”企业已经普遍为此单独拨预算”，证据不够。更准确的说法是：这个领域正在从”某个产品里的一个功能”变成”一个可以被单独拿出来评估和采购的东西”，但转变还在早期。

几个完全开放的问题：1Password
那串合作伙伴名单里有多少是真实的产品整合？Unified Access
的四大能力中哪些已全面上线？1Password 在整个 agent
安全栈里最终会占多大的位置——是停在凭证治理这一层，还是会向更广义的运行时治理延伸？这些目前都没有确定答案。

## 结论

1Password Unified Access 的发布，和同时期
Okta、SailPoint、Veza、Aembit、Astrix、Oasis、CyberArk
各自的动作放在一起看，指向一个判断：AI agent
的身份与凭证治理正在从密码管理和身份认证产品里的一个附属功能，变成一个被单独包装、单独销售、可以被单独评估的产品模块。

这件事值得关注，不是因为某一家公司发了新产品，而是因为它指向了一个正在发生的分层重组。传统身份安全管的是入口：你是谁，你能不能进来。Agent
把问题推到了入口之后：你的 agent
拿了什么凭证、什么时候用的、在什么背景下用的、用完之后能不能追溯。这个”入口之后”的空间正在被多家公司从不同方向同时产品化。

判断的边界也需要写清楚。产品包装和技术架构分化的证据已经比较清楚。独立预算和品类定型的证据还不充分。这更像是从功能到产品模块的过渡期，终点还没到。

对于正在构建 agent
产品的开发者：值得在架构设计中预留凭证治理的集成点，因为这一层迟早会变成企业采购的硬性要求。对于在企业里评估安全方案的人：可以开始单独看
agent 身份治理的需求了，而不是假设现有的身份认证方案能自动覆盖 agent
场景。对于关注行业动态的人：理解”门禁层”和”钥匙柜层”的区别、理解四条路径各自从哪里切入，比记住任何一家公司的产品名都更有长期价值。

---

*调研日期：2026-03-23*
*所有来源均为公开可访问的一手或二手材料，URL
已标注于正文对应位置。*

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
