---
title: "Shopify 把后台全开放给 AI\n了：从生成内核的视角看这件事为什么重要"
date: 2026-04-13
source: https://yage.ai/share/shopify-generative-kernel-20260413.html
slug: shopify-generative-kernel-20260413
lang: zh
---
# Shopify 把后台全开放给 AI 了：从生成内核的视角看这件事为什么重要

发布于 2026 年 4 月 13 日 · [查看原网页](https://yage.ai/share/shopify-generative-kernel-20260413.html)

## Shopify 发生了什么

2026 年初，Shopify
做了一个在电商行业相当激进的决定：把整个后台的读写权限通过标准化协议开放给了所有
AI Agent。产品信息、订单数据、库存状态、SEO 设置、图片素材、结账流程，AI
都可以直接操作。在一个[展示案例](https://www.shopify.com/news/ai-commerce-at-scale)里，商家说了一句帮我优化所有产品的
SEO，Claude 自动更新了 32
条商品，重写图片描述，设置元数据，逐一核对改动。

这件事对不同人意味着不同的东西。对 Shopify 的 480
万商家来说，以前每月光插件就要花 200 到 500 美元，一次 SEO 审计至少 2000
美元，雇助理每小时 50
美元。现在这些操作在原理上可以坍缩成一条指令。对开发者和创业者来说，更有意义的信号是
Shopify 的战略选择。

## 三种做法

Shopify 的 AI 策略可以用一句话概括：自己不造 AI
剧团，把舞台搭好让所有 AI 来唱戏。对比之下，Salesforce 自己养了一个 AI
剧团，WooCommerce 和 BigCommerce 则确保自己的店铺能被路过的 AI
看见。

具体来说，三家走了三条不同的路。

Shopify 选择搭一个开放的协议层。ChatGPT、Google Gemini、Microsoft
Copilot、Perplexity，所有这些 AI
助手都可以通过同一套协议访问商家的商品和服务。Shopify
自己不做购物助手，它的赌注是：AI 平台负责帮消费者发现和比较商品，Shopify
控制最终的交易环节。OpenAI 曾尝试在 ChatGPT
内直接完成购买，但已经退回到推荐模式，[这说明](https://agenticplug.ai/blog/shopify-ai-agents-and-agentic-commerce)当前行业共识正在收敛到发现与交易分离的分工。Shopify
的赌注恰好落在这个分工的有利侧。

为了支撑这个策略，Shopify 在不到一年的时间里推进速度很快。2025 年夏天
AI 访问端点上线。2025 年 12 月发布 [150
项以上更新](https://www.shopify.com/news/winter-26-edition-dev)，全生态商品搜索 API 面向所有开发者开放。2026 年 1 月和
Google 联合发布了一个[通用商业协议](https://www.shopify.com/news/ai-commerce-at-scale)，20
多家零售商和支付平台加入。2026 年 3 月 [AI
店面对所有美国商家默认启用](https://askphill.com/blogs/blog/shopify-just-released-an-ai-toolkit-for-claude-heres-what-it-actually-does)。

[Salesforce
走了另一条路](https://www.salesforce.com/agentforce/ai-agents/platform/)。它把 AI Agent 直接嵌入自有的 CRM 系统里，Agent
可以读写客户数据、触发定价策略、编排物流工作流。你给 Agent
一个业务目标，比如把这个季度的客户续约率提升
5%，它自己去调配资源达成。Salesforce 的 Agent
更像一个有自主决策能力的内部雇员，Shopify 的 Agent
更像一个外部的购物顾问。这两种定位对应着不同的信任模型：Salesforce
需要企业把更多运营决策权交给 AI，Shopify
只需要商家开放商品数据的读取和基本操作权限。

WooCommerce 和 BigCommerce
走的是第三条路：不主导任何协议的制定，确保自身能被各种 AI 发现和接入。[WooCommerce](https://developer.woocommerce.com/docs/features/mcp/)
通过 WordPress
的能力层直接暴露核心操作，在开源阵营中推进最快。BigCommerce 更多依赖
Stripe 等支付基础设施间接获得 AI
可达性。这条路的优势是不需要大量前期投入，劣势是在 AI
和商家之间的交互体验上没有话语权。

三种策略各有适用场景，但 Shopify
的做法让我最在意的原因是另一个：它几乎在逐条验证我半年前提出的一个框架。

## 宜家家具和生成内核

2025 年 11 月，我在[《超越 DRY：AI
原生软件工程的思考》](https://yage.ai/ai-software-engineering.html)中提出了一个判断。核心观点是，在 AI
帮用户写代码、定制软件的时代，软件公司交付的产物正在发生根本变化。

用一个类比来说：过去我们交付的是成品家具，像一把功能固定的椅子，开箱即用，但用户改不了高度和颜色。现在我们交付的更像宜家家具：一个套件，里面有几个关键的核心部件（用户在家造不出来的椅面和椅腿），一本详尽的说明书（不是给人看的，是给组装机器人看的），还有一把内六角螺丝刀（机器人虽然可以用机械臂打螺丝，但有螺丝刀打得更快更准）。

我把这个套件叫做生成内核（Generative Kernel），由三个部分组成。

第一是核心套件，对应宜家包装里那些用户造不出来的核心部件。对 Shopify
来说就是支付处理、物流追踪、库存管理、订单系统。这是 480 万商家选择
Shopify 的根本原因，也是 AI 替代不了的部分。AI
可以帮你写产品描述，但帮不了你和银行结算。

第二是引导知识，对应宜家那本 100 页的说明书。但这本说明书的读者是
AI，所以它可以写得非常详尽：设计哲学、最佳实践、常见陷阱，人类读完要几天，AI
几秒钟就消化了。Shopify 把[开发文档、API
参考和实践指南](https://www.shopify.com/news/winter-26-edition-dev)打包成了 AI 可以直接消费的接口。Claude Code
接入之后，一条命令就能获得完整的 Shopify
开发知识，然后按照这些知识去写代码、调用 API、操作店铺。[Ask
Phill 的分析](https://askphill.com/blogs/blog/shopify-just-released-an-ai-toolkit-for-claude-heres-what-it-actually-does)把这描述为基础设施而非聊天机器人：AI
可以查接口的工作方式、验证代码正确性，所有操作在一次对话内完成。

第三是杠杆工具集，对应宜家包装里的内六角螺丝刀。AI
在概念上理解怎么搜索商品、怎么完成支付，但实际执行这些操作极其复杂，涉及跨系统数据查询、安全校验、多方协议对接。Shopify
把这些操作打包成了高层工具：[全生态商品搜索](https://www.shopify.com/news/winter-26-edition-dev)让
AI 用一个查询就能搜遍整个 Shopify 生态的商品数据，结账工具让 AI
能安全地把购物车一路推进到支付完成，支持多种主流支付方式和 [Visa、Mastercard
的 Agent 支付协议](https://stellagent.ai/insights/shopify-ai-agentic-commerce-strategy)。这些工具把两个 AI
概念上能理解但实现上极容易出错的操作变成了确定性的单步调用。

生成内核这个框架是从个人开发经验中提炼出来的。半年前写那篇文章的时候，它还是一个理论推导，我用
Stripe 做了例子。Shopify 用 3780
亿美元年交易额的体量给出了一个更大规模的实证。

而且 Shopify
的平台策略本身就是生成内核思想在平台层面的体现：放弃穷尽所有用户需求去开发功能，转而最大化外部
AI
基于你的能力进行创造的潜力。用生成内核的框架回看三种平台策略，差异就更清楚了：三家在核心套件层面差别不大，都是各自不可替代的商业能力。但在引导知识和杠杆工具集的开放程度上，Shopify
走得最远。Salesforce 的引导知识主要服务于自己生态内的 Agent，WooCommerce
的杠杆工具集依赖第三方去构建。

半年前我写道，我们正在从构建软件走向构建软件的潜力。Shopify
是这个判断的第一个大规模实证。

## 协议层的问题

Shopify
验证了生成内核的概念是对的，但承载这个概念的协议层有不少问题。

Shopify 用的协议叫 MCP（Model Context Protocol），是 Anthropic
推出的一个让 AI 和外部工具通信的标准。2025 年 3 月我在[《统一工具协议的诱惑》](https://yage.ai/mcp.html)中分析过，MCP
的流行主要来自 Anthropic
的商业推动（完整的开发生态、开放叙事、品牌信任），技术上处于中庸位置。

半年后问题变得更明显。我在[《为什么 OpenAI Apps SDK 对
MCP 的支持反而是 MCP 的危机》](https://yage.ai/mcp-revisited.html)中分析了一个关键信号。MCP
的核心设计哲学是所有信息必须流经 AI 的理解范围，AI
对所有操作有完整的可见性。这个假设很优雅，但它是实验室里产出的。OpenAI
在实际工程中遇到了界面渲染的需求，发现 MCP
的架构处理不了，于是在协议上打了个洞，通过一个私有扩展绕过了这个限制。这从根本上违背了
MCP 的设计哲学。

Shopify 自己的做法也印证了单一协议不够用。它没有只用
MCP，同时推进了和 Google 共建的通用商业协议、和 Stripe
共建的支付协议、Google 的支付授权层、以及 Agent
之间的协调协议。一个商家的店铺同时暴露在四五种协议下，每种解决不同层面的问题。这正是我在分析
MCP 时预测的场景：MCP 更接近 SQL 和 CSS
这类表达性协议，天生有分裂成不同方言的倾向，和 HTTP、USB
这类即插即用的管道协议有本质区别。

工程层面的反馈也指向同一个方向。[社区论坛](https://community.shopify.com/t/shopify-mcp-server-http-500-error/420575)上有商家报告间歇性错误，社区维护的工具在
Shopify 更新接口后会断裂，[安全报告](https://www.docker.com/blog/mpc-horror-stories-cve-2025-49596-local-host-breach/)显示存在数据泄露风险。

所以判断分两层。平台从功能提供者变为 AI
可操作的基础设施，这个方向是确定的，也是不可逆的。但协议层面仍然处于早期混战。对开发者来说，理解生成内核这个思考框架（核心套件、引导知识、杠杆工具集分别对应什么、怎么设计）比绑定某个具体协议的实现有更持久的价值。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
