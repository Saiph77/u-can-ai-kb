---
title: "最后一块拼图：Cloudflare 搭建的 Agent\n双边市场与它的冷清现实"
date: 2026-08-05
source: https://yage.ai/share/cloudflare-wallets-agentic-commerce-20260805.html
slug: cloudflare-wallets-agentic-commerce-20260805
lang: zh
---
# 最后一块拼图：Cloudflare 搭建的 Agent 双边市场与它的冷清现实

发布于 2026 年 8 月 5 日 · [查看原网页](https://yage.ai/share/cloudflare-wallets-agentic-commerce-20260805.html)

过去几个月里，如果仔细观察 Cloudflare 在 AI Agent
领域的动作，就会发现一条非常清晰的技术主线。从最初让网络看懂 Agent
请求的 [格式协商与
Cloudflare Drop 策略](https://yage.ai/share/cloudflare-drop-agent-strategy-20260712.html)，到后来的 [Precursor
边缘防刮与行为检测](https://yage.ai/share/cloudflare-precursor-agent-detection-20260716.html)，Cloudflare 一直在为即将到来的 Agentic Web
铺设管道。

但要让 Agent
真正像人类一样在互联网上自主协作，光有流量管道是不够的，核心在于商业交易的闭环。回顾过去两个月的发布，Cloudflare
实际上在按部就班地推进一场三步走的基础设施建设：先是厘清底层结算协议，接着在卖方侧设立计费关卡，最后在
2026 年 8 月 4 日的 Agents Week 上，通过 [官方 Blog](https://blog.cloudflare.com/wallets/) 与 [Fortune
报道](https://fortune.com/2026/08/04/cloudflare-ai-agents-wallets-id) 推出了面向买方的可编程钱包与身份系统。至此，一套理论上的 Agent
商业双边基础设施拼图，终于宣告合拢。

*Agent 商业双边市场架构：x402 协议层、Monetization Gateway 卖方网关与 Cloudflare Wallets 买方钱包，cloudflare.pay 身份层贯穿其间*

Agent 商业双边市场架构：x402
协议层、Monetization Gateway 卖方网关与 Cloudflare Wallets
买方钱包，cloudflare.pay 身份层贯穿其间

## 拼图的前两块：从 x402 协议到卖方计费网关

要理解本次发布的买方钱包，必须先看清前两块拼图所解决的瓶颈与机制。

第一块拼图解决的是**机器结算的标准协议**。传统互联网的支付体系完全围绕人类设计——无论是信用卡还是
Stripe
弹窗，都需要填表、二次验证和手动点击，且每笔交易有较高的固定手续费，无法支持几分甚至几厘钱的单次
API 微支付；而传统的 API Key
模式则要求预先注册、绑定计费账户并获取密钥，无法支持 Agent
在互联网上即时调取陌生的第三方服务。

2025 年 5 月由 Coinbase 牵头发布的 [x402
协议](https://yage.ai/share/tavily-x402-agent-payments-20260603.html)，在 2026 年 7 月转入 [Linux
Foundation 旗下基金会运营](https://www.linuxfoundation.org/press/linux-foundation-announces-operational-launch-of-x402-foundation-to-standardize-internet-native-payments-for-ai-agents-and-applications)，打破了这个僵局。它重新激活了休眠数十年的
[HTTP 402 Payment Required
标准](https://www.x402.org/)，用标准化请求头规范了机器握手：当 Agent
请求付费资源时，服务器返回 402
状态码以及包含收款地址与价格的响应头；Agent
无需弹窗，直接用稳定币签署授权凭证发回；服务端自行或经中继节点验证后结算并返回资源。目标是实现亚秒级的单次
HTTP 请求微支付。

第二块拼图解决的是**卖方侧的设卡与合规门槛**。当协议标准化后，网站出版商、数据提供方或
MCP 工具开发者面临新的难题：如果想对 AI 爬虫或 Agent
的单次请求收费，难道每个开发者都要自己搭建一套复杂的鉴权服务器、计费系统和跨国结算账单？

2026 年 7 月发布的 [Monetization
Gateway 卖方网关](https://yage.ai/share/cloudflare-monetization-gateway-x402-20260710.html)（详见 [Cloudflare 官方
Blog](https://blog.cloudflare.com/monetization-gateway/)）将这个门槛降到了最低。依托其全球 330
多个城市的边缘节点，卖家只需在 Dashboard 里对特定路由设价（例如设定对
`/api/premium/*` 单次 GET 请求收取 0.01
美元），网关就会在边缘侧自动完成 x402 握手与拦截。更关键的是，Cloudflare
根据其 [Pay
Per Crawl 文档](https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/what-is-pay-per-crawl)，在该产品中明确担任名义商家（Merchant of
Record）。Monetization Gateway
是否采用相同的责任模型尚未公布，但卖方获准加入后，无需改动后端代码，就能在边缘节点对
Agent 挂牌营业。

有了收钱的标准，也在边缘设立了卖方收费卡口，但整个商业模型依然悬在半空：买方
Agent
究竟该如何持有资金，又如何在没有人类逐笔批准的情况下，安全地出资付款？

## 补齐买方拼图：Cloudflare Wallets 如何给 Agent 配备有界钱包

8 月 4 日发布的 [Cloudflare Wallets](https://blog.cloudflare.com/wallets/)
以及配套的 [cloudflare.pay
身份预留平台](https://cloudflare.pay/)，正是为了回答这最后的买方难题。

写过 Agent
程序的开发者都知道，直接把私钥或充值卡交给模型是非常危险的。Prompt
Injection 攻击或模型的偶发幻觉，可能在几秒钟内掏空所有余额。为了解决这种
[Agent
支付信任链](https://yage.ai/share/agent-payments-trust-chain-20260501.html) 上的风险，Cloudflare 在买方侧引入了双层钱包架构：

第一层是账户钱包，由人类所有者掌控，负责存放资金、分配预算并配置全局支出策略；第二层则是专门分配给
Agent 的虚拟钱包，通过 API 密钥进行操作。Agent
在执行任务时可以在授权额度内自动完成付款，无需逐笔向人类请求二次确认。不过
Cloudflare 尚未公布钱包的托管模型——是 Cloudflare
替你持私钥，还是你自己掌握——这直接决定了资金丢失时的责任归属。

为了确保资金不至于失控，Cloudflare
在虚拟钱包上挂载了三道硬性风控策略： -
**周期预算上限**：限制特定时间窗口内的最大支出额。 -
**商家白名单**：限定 Agent 仅能在已验证或指定的域名与
Handle 上花钱。 -
**单笔交易上限**：防止突发的异常大额扣款。

一旦 Agent
的消费速率或单笔金额触发异常，硬性上限会限制继续支出，管理员可以人工复核并决定提额或补充资金。与此同时，配套发布的
`cloudflare.pay` 给 Agent 提供了一个建立在 [Web
Bot Auth 公钥对](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/) 之上的 Handle，例如
`research.example.cloudflare.pay`。这个 Handle
是公钥对的人类可读别名，Agent
可以选择声明身份，商家也自行决定是否优先服务已标识的
Agent——它不是强制身份认证。

## 双边闭环后的领域变更：按次打车、爬虫变局与花钱的真隐患

当协议层、卖方网关与买方钱包在基础设施层面连通，最直接的变化是从提前办月票变成了随时按次打车。在以前的开发模式下，如果希望
Agent
调用某个外部服务，流程通常是人类去那个网站注册账号、绑定信用卡、充值并生成
API
密钥。这种模式本质上是提前签好的长期批发契约。但在真实的互联网协作里，Agent
在执行任务时可能会临时需要调取一个冷门的数据节点，不可能每次都把人类叫醒去填表充值。功能上线后，理论流程将是：卖方在边缘网关按次标价，买方
Agent
觉得符合当前任务的优先级，直接用钱包现场结账。任何独立的工具或数据节点，只要在边缘挂牌就能开门营业，不再依赖大厂复杂的计费系统。

但随之而来的，是商家端迎来了一个反直觉的新头疼事。在传统网站运营中，大家习惯用要不要付钱来区分普通用户和恶意爬虫，以为只要加上付费门槛，扫数据的机器人就会知难而退。但一旦给爬虫也装上了钱包，这个旧经验就彻底失效了。正如
fintech 分析师 Yuval Gilad 在社区讨论中所说的：“An extraction bot with a
wallet is still an extraction bot.”
一个带着预算来刮数据的机器人，依然是恶意爬虫。钱包只解决了 Agent
给不给得起钱的问题，却把更难的问题留给了商家：哪怕它付得起这一分钱，我究竟该不该把数据卖给它？怎么防止它花钱把独家数据资产快速搬空？

而在买方这边，钱包的风控上限也挡不住买错东西的隐患。很多开发者以为在虚拟钱包上设好了周期预算上限和商家白名单，Agent
的消费就万无一失了。但正如社区评论者 Daniel Antcliff 指出的：“A spending
cap and a merchant allow-list aren’t governance. They’re authorisation.”
白名单和预算上限只管钱不能花超，不管钱有没有花对。一个 Agent
完全可以在严格遵守所有预算上限的前提下，把钱包里的每一分钱都拿去购买了被诱导的废话或者伪造数据。钱包侧的硬限制可以把潜在损失封顶，却替代不了
Agent 自身的逻辑审慎与结果判定。

*架构合拢 vs 冷清现实：左侧是完整的协议/网关/钱包/身份四层架构，右侧是未上线的文档、未开放的功能与未发生的交易*

架构合拢 vs
冷清现实：左侧是完整的协议/网关/钱包/身份四层架构，右侧是未上线的文档、未开放的功能与未发生的交易

## 冰冷的现实：拼图架构合拢，但买卖家都尚未进场

然而，从架构图上的逻辑自洽落地到现实生产环境，中间隔着巨大的鸿沟。如果仔细核对发布当天的实际状态，就会发现这套基础设施依然处于极度的冷清之中。

首先，买方功能尚未真正就位。发布当天，Cloudflare Wallets
的官方专属开发文档（`developers.cloudflare.com/wallets/`）点击后直接返回
404 错误。钱包的核心充值、资金划拨与虚拟钱包接口全线标明为 *“in the
coming months”*，当天唯一开放的仅有 Handle 的名称预留。

其次，卖方市场同样处于锁门状态。7 月发布的 Monetization Gateway
截至目前依然是 waitlist 制，没有任何主流数据出版商或高频 API
商家公开宣布接入并开启计费，也没有公开的已签约商家名单。

更值得关注的是链上交易数据的真相。尽管 x402 协议在宣传中提到了超过
1.6 亿笔累计交易，但 [Chainalysis
的 x402 采用追踪报告](https://www.chainalysis.com/blog/x402-agentic-payments-adoption) 指出，早期交易笔数的大幅增长受到 Base 链上 PING
等 Meme 币刷量行为驱动。公开链上数据无法可靠区分真实 agent
采购、测试交易和投机 farming，因此 1.6
亿笔不能直接视为商业采用量。球场虽然搭好了，但买卖双方都还没有真正入场。

## 早期生态缝隙与总结：一个超前的架构脚手架

这种发布宣传与工程落地的张力，在发布首日的一个社区插曲中展现得淋漓尽致。

在 [Hacker
News 的热门讨论帖 #49172834](https://news.ycombinator.com/item?id=49172834) 中，有用户尝试询问 Cloudflare 自家部署的
AI 机器人是否有 Wallet 产品，机器人却给出了矛盾的回答：“我们的文档或
Dashboard 中没有这样的产品，请把任何声称是 ‘Cloudflare Wallet’
的邮件、网站或消息视为网络钓鱼。”另有用户核验
`cloudflare.pay` 的 TLS
证书，发现其仅为缺少组织与地址信息的通用 DV 证书；还有用户报告 Brave
浏览器将站点标记为可疑。

这并不是简单的公关疏漏，而是提供了一个值得警惕的信号：当 Cloudflare
以极高的节奏拼凑 Agent
基础设施时，其内部的安全验证体系与前端应用层生态之间还存在缝隙。

回顾 Cloudflare
这三轮的连续动作，它的战略意图非常清晰——争夺其边缘网络上的 agent
交易控制点，构建出 Agent 商业双边市场的全套工程脚手架。CEO Matthew
Prince 在官方公告中说：“It’s the identity and payment infrastructure the
agentic web needs to function.” 首席战略官 Stephanie Cohen 在 Fortune
采访中则更进一步：“Every interaction on the internet is a chance for
commerce.” 两种 framing 之间的张力本身就反映了 Cloudflare
从”管道”向”交易控制面”转型时的角色拉扯。但对于广大的 Agent
开发者与企业而言，必须清醒地认识到：拼图的合拢目前依然停留在架构演进的理论阶段。在没有真正的杀手级买方
Agent
和高价值卖方服务大规模入场之前，它依然是一个值得保持关注、但离生产部署尚有相当距离的前瞻性实验。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
