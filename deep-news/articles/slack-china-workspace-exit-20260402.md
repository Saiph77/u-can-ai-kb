---
title: "Slack 删除中国区\nWorkspace，这条新闻真正值得关注的是什么"
date: 2026-04-02
source: https://yage.ai/share/slack-china-workspace-exit-20260402.html
slug: slack-china-workspace-exit-20260402
lang: zh
---
# Slack 删除中国区 Workspace，这条新闻真正值得关注的是什么

发布于 2026 年 4 月 2 日 · [查看原网页](https://yage.ai/share/slack-china-workspace-exit-20260402.html)

External Article Draft | 2026-04-02 | Author: grapeot + Claude Opus
4.6

---

## 发生了什么

2026 年 4 月 1 日，大量 Slack 用户发现自己的 workspace
被突然停用。受影响的是 billing address 位于中国大陆、香港、澳门的
workspace，付费客户和免费用户都有波及。停用后所有历史消息、文件、频道和集成不可访问，Slack
同时启动了 90 天数据删除倒计时。

这件事之所以值得写一篇长文，原因有三个。第一，Slack
的执行方式极其粗暴，即使退出动机是合理的商业决策，用户端的体验仍然像是一次数据劫持。第二，这不是一个孤立事件，而是全球
SaaS
分层供给趋势中的一个信号：按司法辖区切割服务正在成为常态。第三，它提供了一个具体的案例来思考：当你依赖的基础设施平台决定退出你所在的市场，你的数据和业务连续性能撑多久？

---

## 时间线与证据分段

### 第一阶段：2019 年 Salesforce-阿里巴巴独家合作协议

2019 年 7 月 24 日，Salesforce 宣布与阿里巴巴建立战略合作，阿里云成为
Salesforce CRM 在中国大陆、香港、澳门、台湾的独家提供商（[Salesforce
官方博客](https://www.salesforce.com/blog/driving-customer-success-with-alibaba/)）。这份协议覆盖 Sales Cloud、Service Cloud、Commerce Cloud
和 Salesforce Platform。

2023 年 12 月 18 日，Salesforce 宣布 Sales Cloud、Service Cloud 和
Salesforce Platform 在阿里云上正式 GA（[Salesforce
新闻稿](https://www.salesforce.com/news/stories/sales-service-platform-alibaba-cloud/)），目标客户是在中国大陆运营的跨国公司，满足数据本地化和合规需求。

Slack 作为 Salesforce 2020 年以 277
亿美元收购的产品，逻辑上归入同一渠道安排。但 Slack
在阿里云上的实际可用性和迁移体验，在 2025 年之前缺乏公开记录。

证据强度：已证实（合作协议本身）；Slack
具体如何纳入该协议的执行细节在 2025 年之前是推断。

### 第二阶段：2025 年 11 月，Slack 通知大中华区客户停止直接服务

2025 年 11 月，The Information 首先报道 Slack
通知中国大陆、香港、台湾、澳门用户需在 2026 年 2
月前将账户迁移到阿里云（[Breaking
The News 转引](https://breakingthenews.net/Article/Salesforce's-Slack-may-halt-direct-service-in-China/65222767)）。报道引述了一位受影响地区的 Slack
客户和一位阿里云员工。

HN 上有用户贴出了两种不同版本的 Slack 通知邮件（[HN
thread](https://news.ycombinator.com/item?id=45961157)）。较大团队收到的邮件指引他们通过阿里云继续购买
Slack，邮件原文提到：“As you may know, on July 24, 2019, Salesforce and
Alibaba announced a strategic partnership, establishing Alibaba Cloud as
the exclusive provider of Salesforce CRM to customers in mainland China,
Hong Kong, Macau and Taiwan.” 而较小团队收到的是直接终止通知：“We are
writing to let you know that due to changes in how Salesforce services
are provided in mainland China, Slack will no longer be renewing your
workspace… Effective February 1, 2026, we will suspend all access to
your workspace… Your workspace and all associated data will be deleted
within 90 days thereafter.”

这里有一个重要的细节差异：较大的付费客户被引导迁移到阿里云，而较小的团队被直接终止服务，没有提供阿里云迁移选项。HN
thread 中一位用户更进一步指出，联系阿里云后得到的回复是：“Slack is no
longer selling in China mainland, neither by SFDC nor by Alibaba
Cloud.”

The Information 的报道将停服原因归结为”a privacy and data security
law entered into
force”——指向中国《网络安全法》《数据安全法》《个人信息保护法》体系。

证据强度：较强推断。原始邮件通过 HN 用户公开贴出（非 Slack
官方发布），但多个独立来源交叉印证了邮件内容。The Information
是付费媒体，原始报道未能直接获取，依赖二次转引。

### 第三阶段：2026 年 2-4 月，workspace 实际被停用

2026 年 2 月 1 日是通知中的停服日期。Reddit r/Slack 上在 2026 年 4 月
1 日出现多个帖子报告 workspace 被实际停用：

一位香港用户（[Reddit:
workspace suddenly suspended](https://www.reddit.com/r/Slack/comments/1sabysj/workspace_suddenly_suspended_without_a_chance_to/)，2026-04-01 发帖）描述其公司的付费
workspace 在 4 月 1
日被突然暂停，完全无法访问文件和历史数据，称未收到事先通知（或通知被遗漏到垃圾邮件），迁移到阿里云需签署最低一年合约。

另一位用户（[Reddit:
Hong Kong / China / Taiwan based Slack Suspended](https://www.reddit.com/r/Slack/comments/1sadwsh/hong_kong_china_taiwan_based_slack_suspended/)，2026-04-01
发帖）贴出了 Slack Support 的模板回复原文：“Your workspace was impacted
by a previously communicated change to terminate direct Slack services
in mainland China, Hong Kong, and Macau. A notice was sent to workspace
Owners and Admins advising that affected workspaces would be suspended
beginning early 2026. As of April 1, 2026, your workspace is no longer
accessible… the workspace and all associated data are scheduled to be
permanently deleted within 90 days.”

值得注意的是，Slack Support 模板回复中的受影响地区是”mainland China,
Hong Kong, and Macau”，没有提到 Taiwan。而 2025 年 11 月的通知邮件和 The
Information 报道中，台湾是被包含的。这可能意味着台湾的执行节奏不同，或者
Slack 调整了台湾的处理方式，但目前没有明确证据确认哪种情况。

证据强度：用户一手报告（Reddit），Slack Support
回复原文截图/贴出。属于可信的一手用户反馈，但非 Slack 官方公告。

---

## 这次事件的法务与商业逻辑

如果只看这条新闻本身，真正相关的约束并不复杂：Slack
面对的不是针对中国公司的身份识别问题，而是一个区域服务问题。

这次退出的法律背景主要来自中国方面的法规：《网络安全法》《数据安全法》《个人信息保护法》，以及
2025 年 1 月 1
日生效的《网络数据安全管理条例》。这套法规对跨境数据传输、数据本地化、安全评估等施加了严格要求。对
Slack/Salesforce 而言，继续直接在中国提供 SaaS
服务意味着需要在中国境内部署基础设施、进行数据安全评估、接受监管审查，合规成本极高。

而执行路径则来自 2019 年就已经铺好的
Salesforce-阿里巴巴合作框架。也就是说，这件事更像一个早就埋下伏笔、在
2025-2026
年集中兑现的区域服务重组：直营退出，渠道切换，部分客户迁移，部分客户被终止。

因此，这条新闻更稳妥的判断是：Slack
在大中华区收缩或终止直接服务，背后是数据治理合规成本和渠道策略，而不是针对中国公司身份的定向打击。停服的判断信号是
billing address 和 sales region
所在地，执行的是区域服务调整，而不是身份歧视。

---

## 用户为何感到执行粗暴

上一节厘清了动机和法务逻辑。但动机是否合理和执行是否得体是两件事。这次停服在用户端触发了极强的敌意感知，而这种感知有清晰的操作层来源，值得逐项拆解。

**通知到达率问题。** 多名用户在 Reddit 和 HN
上声称从未收到过任何事先通知，或者通知邮件进入了垃圾邮件文件夹。Slack 的
Support 模板回复坚持”a notice was sent to workspace Owners and
Admins”，但没有提供任何发送记录或确认机制。对于一次涉及数据删除的操作，仅依赖电子邮件单向推送、不设置产品内弹窗或
banner 提醒，是一个显著的执行缺陷。作为对比，主流 SaaS
平台在执行服务条款变更时通常会使用产品内通知 + 邮件 +
账户状态页面三重通道。Slack
在产品内通知这个最可靠的渠道上没有留下任何公开证据表明它做了这件事。

**锁死访问与数据劫持感。**
停服的执行方式是立即切断所有访问，包括历史消息、文件、频道、集成和工作流。用户在被停服后无法登录导出数据，形成事实上的
data hostage 状态。Reddit 用户原话：“We are completely locked out and
have zero access to our files, client communications, and historical
data… It feels like our data is being held to ransom.”
这种设计把”停止服务”和”扣押数据”绑定在一起：你要么签新合约（通过阿里云），要么在
90
天后失去一切。无论商业退出的动机多么中性，这种执行模式在用户端产生的感受和绑架没有区别。

**90 天删除倒计时。** workspace 被停用后，数据将在 90
天内被永久删除。这个倒计时叠加上无法登录导出的事实，意味着用户的唯一出路是联系
Slack Support 请求数据导出，而 Support
的响应速度和流程对于面临数据销毁倒计时的用户来说是不可控的变量。

**客服响应模板化。** 多名用户报告，联系 Slack Support
后收到的是完全相同的模板回复，没有针对具体情况的处理。模板中甚至没有提供数据导出的具体流程或时间表。对于一些用户来说，Support
的响应本身就是他们第一次知道停服原因的途径，因为他们之前根本没收到过通知。

**大小客户差异化处理。**
较大的付费客户收到了阿里云迁移指引，较小的团队收到的是直接终止通知。这种差异化本身在商业上可以理解（大客户有渠道转移价值，小客户没有），但当小客户被直接终止且没有迁移选项时，他们面对的是一个纯粹的最后通牒：接受数据丢失，或者在从未使用过的阿里云上签署新合约。更关键的是，至少一名用户联系阿里云后得到的回复是
Slack
在中国大陆已完全不再销售，这意味着”迁移到阿里云”这个选项对部分用户可能从一开始就是空头支票。

这五个因素叠加产生了一个整体效果：即使 Slack
的商业退出动机完全是合规驱动的、没有政治意图，用户体验到的仍然是”一个外国平台在毫无征兆的情况下锁死了我的数据并威胁在
90 天内删除它”。这种感知和真实原因之间的落差，是 Slack
执行层面的失败，也是中文社区愤怒的主要来源。

---

## 为什么这件事是一个坏的先例

Slack
个案如果只是一个通信工具的区域退出，影响范围有限。但它暴露了一个更深层的问题：当代企业运营中有多少关键依赖被放在了可以被平台单方面撤销的访问权上，而使用者习惯性地把这些访问权当作稳态基础设施。

**今天 Slack，明天可能是谁。** 如果按照 Slack
这次停服的执行模板推演——一个全球 SaaS
平台因为某个司法辖区的合规成本过高而决定退出该市场，通过邮件通知受影响用户，设定一个期限，到期后切断访问并启动数据删除倒计时——这个模板可以被套用到任何一个在中国有用户但没有在中国部署基础设施的
SaaS 服务上。

问题的关键在于：不同类型的 SaaS
被套用这个模板时，造成的损害完全不同。Slack
停服导致的是通信中断和历史数据丢失，这很严重但不直接涉及资金。如果
Stripe 用同样的模式停服，冻结的是现金流和交易能力。如果 Supabase
停服，锁定的是应用后端的数据库和运行时。这三者的风险画像有本质差异，后文逐一分析。

**全球 SaaS 的供给模式正在从统一全球服务走向分层供给。**
过去十年，SaaS
的默认假设是：注册一个账户就能在全球使用，服务条款全球统一，数据存储在平台选择的区域。这个假设正在被多股力量侵蚀：各国数据主权立法（中国的数据安全法、欧盟的
GDPR/Data Act、印度的 DPDP
Act）、平台自身的风险管理逻辑（退出合规成本高于收入的市场）、以及地缘政治摩擦带来的监管不确定性。这些力量的共同方向是：按司法辖区、风险类别和渠道关系对服务供给进行分层。对于依赖全球
SaaS
的企业来说，这意味着过去的”注册即全球可用”正在变成”你的服务连续性取决于你的
billing address 所在司法辖区、你的 KYC
状态、以及平台对你所在市场的商业判断”。

---

## 平台主权与基础设施风险框架

### 三方权力分配：国家、平台、客户

Slack 事件可以被放进一个更一般的权力分析框架。在任何一个 SaaS
依赖关系中，至少有三个主体在互动：服务提供方所在国的监管体系、客户所在国的监管体系、以及平台本身的商业决策权。客户处于这个链条的末端。

平台掌握了事实上的控制权：它控制数据存储位置、访问权限、服务条款、定价、以及终止服务的时间和方式。两端的国家通过立法和执法向平台施压，平台在夹层中做成本收益计算，客户处于权力链的末端。

这个框架解释了为什么 Slack 用户的愤怒指向了 Slack
而不是中国数据安全法：因为直接执行终止操作、锁死数据、设定删除倒计时的是
Slack，而不是政府。平台在这个链条里既是监管的响应者，又是对客户的直接施力者。

### 分层风险画像：支付、身份、通信、数据、AI 基础设施

不同 SaaS
层在面临区域退出或合规收缩时，风险烈度和可迁移性差异巨大。以下按照锁定强度和潜在损害排列：

**支付层（以 Stripe 为代表）：风险最高。**
支付平台掌控的是现金流本身。如果 Stripe 对某个区域执行类似 Slack
的退出模式，受影响的企业面临的是即时的资金冻结和交易中断，后果远比通信中断严重。Stripe
已经有过对特定国家或高风险行业实施账户冻结、资金滞留和强制关闭的先例（这在
fintech
合规领域是已知模式）。支付层的可迁移性在理论上存在（可以切换到其他支付网关），但迁移过程中的资金在途风险、商户协议重签、以及滞留资金的提取谈判，使得实际迁移成本极高。更关键的是，支付层涉及跨境资金流动的监管，这意味着它同时受到来源国和目的国的双重合规压力，平台的单边决策空间反而更大（因为它可以援引任一方的合规要求作为行动依据）。

**身份与认证层（以 Auth0/Okta 为代表）：风险次之。**
身份服务被切断意味着所有下游应用的登录和权限管理同时失效。虽然身份层不直接涉及资金冻结，但其连锁效应是即时的：所有依赖该身份服务的应用会同时变得不可用。可迁移性取决于是否使用了标准协议（OIDC/SAML），如果是，理论上可以切换提供商；如果身份数据和权限配置深度绑定了特定平台的扩展功能，迁移成本会显著上升。

**通信协作层（以 Slack
为代表）：可迁移性中等，数据锁定强。**
通信工具的替代品多（Teams、飞书、Discord、Mattermost），核心功能的迁移成本可控。真正的锁定在于历史数据：多年的频道对话、文件、工作流和集成，这些在迁移时要么丢失要么严重降级。Slack
这次事件中最致命的操作恰恰是在切断服务的同时锁死了数据导出，把一个本可以是中等风险的服务退出变成了高烈度事件。

**数据库与后端平台层（以 Supabase
为代表）：可迁移性取决于底座开放度。** Supabase 的风险画像和
Slack/Stripe 有本质区别。Supabase 的底座是
PostgreSQL，这是一个开源的、标准化的数据库引擎。如果 Supabase
停服，用户理论上可以将数据导出并迁移到任何 PostgreSQL
兼容的环境（自建、AWS RDS、其他托管服务）。Supabase
自身也是开源项目，极端情况下可以自建实例。这意味着 Supabase
的锁定强度集中在平台附加功能（Auth、Realtime、Edge
Functions、Storage）而非核心数据层。核心数据的可迁移性显著高于 Slack 和
Stripe。当然，如果用户深度使用了 Supabase
的非标准扩展功能，迁移成本也会上升，但底线保障（数据可导出、引擎可替换）是
Slack 和 Stripe 所不具备的。

**AI 基础设施层（以 OpenAI API、Anthropic API、云 GPU
为代表）：风险体现在可用性和供应连续性。** AI infra
的区域限制更多体现在 KYC 准入（部分 API
只对特定国家开放注册）、模型可用性（某些模型因政策原因在特定区域不可用）、配额和定价差异、以及供应连续性（GPU
供应链受到半导体管制影响）。AI infra
通常不涉及用户数据的深度锁定（推理请求是无状态的，微调模型可以在不同平台间迁移），但它的风险在于：如果你的产品核心功能依赖特定
AI 提供商的模型质量和 API
可用性，切换提供商意味着模型行为变化和可能的产品质量下降。

### 为什么 Stripe、Slack、Supabase 风险画像不同：一个总结

| 维度 | Stripe | Slack | Supabase |
| --- | --- | --- | --- |
| 锁定的核心资产 | 现金流 + 交易关系 | 历史通信数据 + 工作流 | 应用数据 + 平台功能 |
| 停服即时影响 | 资金冻结、交易中断 | 通信中断、数据不可访问 | 后端停摆 |
| 可迁移性 | 低（资金在途风险、商户协议） | 中（替代品多，历史数据难迁） | 高（PostgreSQL 底座、开源可自建） |
| 合规压力来源 | 双重（来源国 + 目的国金融监管） | 主要是数据本地化法规 | 数据本地化 + 基础设施合规 |
| 平台单边决策空间 | 最大（金融合规给了最大话语权） | 中等 | 最小（开源底座限制了锁定能力） |
| 最坏情况 | 资金被冻结数月、无法提取 | 历史数据在 90 天后被删除 | 需要重建平台功能，核心数据可保 |

---

## 制衡力量

上一节的分析可能给人一种平台全能、客户无力的印象。但现实中存在若干制衡力量，它们限制了平台单边行动的速度和烈度，也解释了为什么并非所有
SaaS 都会走 Slack 这条路。

**企业合同与收入依赖。** 大客户和 SaaS
平台之间通常签有多年期企业合同（Enterprise
Agreement），合同中包含服务水平协议（SLA）、数据处理条款、和终止条款。这些合同对平台构成法律约束：单方面终止服务可能触发违约赔偿。Slack
此次对大客户提供迁移选项而对小客户直接终止，部分原因就是大客户的合同约束力更强。对平台来说，高收入区域的退出成本也更高，这会延缓退出决策。

**竞争与替代品。** 如果 Slack
在通信协作领域是唯一选项，用户的愤怒只能停留在情绪层面。但
Teams、飞书、Lark、Discord、Mattermost、Zulip 等替代品的存在，意味着
Slack
的退出会导致用户永久流失到竞争对手。这种竞争压力限制了平台粗暴执行的动机（尽管
Slack 这次没有很好地体现这一点）。

**本地冠军。**
在中国市场，飞书、钉钉、企业微信已经占据了通信协作的主要份额。Slack
退出中国对 Slack
全球业务的收入影响有限（中国区收入占比极小），这反过来降低了 Slack
精心处理退出流程的商业激励。但这也说明：在有本地冠军的领域，全球平台退出的实际影响会被本地替代品吸收。

**开源底座和开放标准。**
这是对平台锁定最根本的制衡。PostgreSQL 之于 Supabase、OIDC/SAML
之于身份服务、SMTP 之于邮件、S3 API
之于对象存储——当底层协议或引擎是开放的，平台在核心功能层面的锁定能力就被削弱。平台仍然可以通过附加功能、易用性和生态集成创造切换成本，但用户至少保有”带着数据离开”的选项。Slack
的教训恰恰在于：它的数据导出功能在正常运营时存在，但在停服时被一并锁死，使得开放性在最需要它的时刻失效了。

**国家间博弈的缓冲效应。**
中美之间的科技竞争是这些事件的宏观背景，但也是一个制衡因素。任何一方过度收紧政策都有成本：对中国市场的限制意味着美国企业失去收入，过严的数据本地化要求会减少外资
SaaS
进入中国的意愿。两国各自的政策都受到内部利益集团的推拉。这意味着分层供给的最终形态会是谈判和妥协的结果，而非一方完全单边决定。

**品牌与声誉成本。** Slack 这次停服在 Reddit、HN
和中文社交媒体上产生了显著的负面影响。这些声誉损失对 Slack
在其他亚洲市场（新加坡、日本、韩国、东南亚）的品牌信任有溢出效应。“如果
Slack
可以这样对待中国区客户，它是否也会这样对待我们？”这个问题会被其他区域的客户问出来。长期来看，粗暴执行会削弱平台在全球客户中的可信度。

---

## 读者可以带走的治理清单

如果你把这件事只理解为一家美国公司又一次对中国用户不友好，那你会错过更重要的东西。更值得带走的判断框架是：**按层治理，把每一项外部
SaaS
依赖都当作可撤销的访问权来评估，而非当作稳态基础设施**。具体而言：

**第一优先级：识别哪些依赖一旦被撤销会造成不可逆损害。**
支付层（Stripe
等）首当其冲，因为涉及资金冻结。任何涉及现金流的外部依赖都应该有备用通道，且备用通道需要在主通道正常运行时就已经验证过（而非等到出事再去接入）。对于
Stripe
这类服务，至少需要：一个经过验证的备用支付网关；资金沉淀在平台侧的金额尽可能低（提高结算频率）；了解平台在极端情况下的资金滞留条款。

**第二优先级：对数据层的依赖，区分”可导出”和”在停服时仍可导出”。**
Slack
的教训是：正常运营时提供数据导出功能，和在停服时仍然允许导出，是两件完全不同的事。对于任何存有重要历史数据的
SaaS
服务，需要建立定期数据备份机制（不是”到时候再导”，而是自动化的增量备份），确保即使平台突然切断访问，数据也已经在本地或另一个可控环境中有副本。如果
SaaS 的底座是开源的或基于开放标准（如 PostgreSQL、S3
API），优先选择这类服务，因为迁移成本的下限更低。

**第三优先级：对通信和协作层，降低单一平台依赖度。**
这意味着关键的客户沟通和内部工作流不应该只存在于一个平台上。重要对话的归档、关键决策的记录，应该有独立于通信平台的存储。Slack、Teams、飞书，任何一个都可以在数月通知期后退出某个市场。

**第四优先级：对 AI infra 依赖，关注模型和 API
的可替代性。** 如果产品核心功能依赖特定 AI 提供商（如 OpenAI 的
GPT-4、Anthropic 的
Claude），需要评估：如果该提供商突然对你的区域或用例施加限制，你能在多长时间内切换到替代提供商（开源模型、其他商业
API）并保持可接受的产品质量？AI infra
的好消息是推理请求通常是无状态的，锁定强度低于数据层和支付层；坏消息是模型质量差异大，切换可能意味着产品体验降级。

**贯穿所有层的原则：**
不要把所有关键依赖都放在同一个司法辖区的平台上。这是 Slack
事件真正的启示——Slack 退出中国、Stripe 收紧特定区域的 KYC、Supabase
未来可能的区域限制，触发机制不同但底层模式相同：平台在特定司法辖区的合规成本超过收入时，会选择退出或收缩，而客户的数据和业务连续性在这个决策中处于从属地位。分散供应商、优先选择开放底座、维护本地备份、验证备用通道——这些措施的成本在正常时期看起来像是浪费，但在
Slack 事件这样的场景下就是救生衣。

---

## 仍未确认的问题

1. 台湾的执行状态。2025 年 11 月通知中包含台湾，但 2026 年 4 月
   Slack Support 模板只提及”mainland China, Hong Kong, and Macau”。台湾
   workspace
   是否已被停用、延期、或另行处理，目前没有明确的公开证据。
2. 阿里云 Slack 的实际可用性。HN 上有用户反映阿里云方面回复 Slack
   在中国大陆不再销售（“neither by SFDC nor by Alibaba
   Cloud”）。如果属实，这意味着”迁移到阿里云”这个选项对大陆客户可能根本不存在，只是名义上提供了一个出口。这条信息只有单一来源，需要更多确认。
3. billing address 在中国以外但实际运营团队在中国的 workspace
   是否受影响。现有报告都是关于 billing address 在大中华区的
   workspace。没有反例说明 billing address 在美国/新加坡但员工在中国的
   workspace 被停用。
4. 免费 workspace 的处理方式。所有已知案例都涉及付费 workspace。free
   plan workspace 是否受同一政策影响，没有公开信息。
5. Slack 是否发布过官方公告。目前所有信息来源都是 The Information
   的报道、用户转贴的邮件、和 Slack Support 的模板回复。没有找到 Slack
   官方博客或帮助中心的正式公告页面来确认这一政策变更。

---

## 关键来源索引

| 来源 | URL | 性质 |
| --- | --- | --- |
| Salesforce 官方博客：阿里巴巴合作 | https://www.salesforce.com/blog/driving-customer-success-with-alibaba/ | 一手 |
| Salesforce 新闻：阿里云 GA | https://www.salesforce.com/news/stories/sales-service-platform-alibaba-cloud/ | 一手 |
| Breaking The News：转引 The Information 报道 | https://breakingthenews.net/Article/Salesforce’s-Slack-may-halt-direct-service-in-China/65222767 | 二手转引 |
| HN thread：用户转贴 Slack 邮件 | https://news.ycombinator.com/item?id=45961157 | 用户一手报告 |
| Reddit：2026-04-01 workspace 被停用 | https://www.reddit.com/r/Slack/comments/1sabysj/workspace\_suddenly\_suspended\_without\_a\_chance\_to/ | 用户一手报告 |
| Reddit：2026-04-01 Slack Support 回复 | https://www.reddit.com/r/Slack/comments/1sadwsh/hong\_kong\_china\_taiwan\_based\_slack\_suspended/ | 用户一手报告 |
| GuruFocus：Salesforce 中国运营变动 | https://www.gurufocus.com/news/3217862/salesforce-crm-ends-direct-operations-for-slack-in-china | 独立媒体 |
| 阿里云博客：Salesforce 独家提供商 | https://www.alibabacloud.com/blog/alibaba-now-exclusive-provider-of-salesforce-crm-in-greater-china\_595141 | 一手 |

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
