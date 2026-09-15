---
title: "三把锁：为什么 Google 和微软做不出 Agentic\n的文档编辑"
date: 2026-04-12
source: https://yage.ai/share/three-locks-agentic-doc-editing-20260412.html
slug: three-locks-agentic-doc-editing-20260412
lang: zh
---
# 三把锁：为什么 Google 和微软做不出 Agentic 的文档编辑

发布于 2026 年 4 月 12 日 · [查看原网页](https://yage.ai/share/three-locks-agentic-doc-editing-20260412.html)

2026 年了，Copilot 还是不能帮你改 PowerPoint 里的幻灯片。

这话听着像段子，但它是事实。微软在 2026 年 2 月之前，Copilot 在
PowerPoint 中根本无法修改已有的幻灯片。用户请求编辑时，得到的回复是：[对不起，我做不到](https://learn.microsoft.com/en-us/answers/questions/2076041/copilot-edit-in-powerpoint)。2
月之后，微软宣布了 Edit with Copilot，但仅限 Web 端，Windows 和 Mac
还在排队。[第三方测试](https://www.prezent.ai/blog/microsoft-copilot-review/)的结论是：能改文字、换配色，但无法重组叙事结构，无法跨幻灯片调整逻辑，甚至给一个形状里的文字换个措辞都做不到。Prezent.ai
的原话：It makes PowerPoint faster. It does not fundamentally change how
presentations are built.

Google 这边也好不到哪去。Gemini 在 Google Docs
里就是一个聊天窗口：你问它一个问题，它给你生成一段文字，然后你自己粘贴。它不能自己改文档结构，不能跨段落重组内容，不能在你不介入的情况下完成任何多步操作。[MindStudio
的分析](https://www.mindstudio.ai/blog/gemini-google-workspace-what-it-can-do)说得很直白：Gemini in Workspace is confined to in-document
tasks。2026 年 Zapier 的 AI 演示工具年度评测，直接[把 Copilot 和
Gemini 都从推荐列表中移除了](https://zapier.com/blog/best-ai-presentation-maker/)。

这件事之所以离谱，是因为技术上这不是什么难题。Claude Cowork 在 2026
年初用大约两周时间就实现了 .docx 和 .pptx
的编辑能力。但这个”两周”需要放在正确的语境里理解：[Cowork
不是从零造的文档编辑器](https://support.anthropic.com/en/articles/11003498-what-is-claude-cowork)，它是 Claude Code 这个 agentic coding
工具的自然延伸。Claude Code 已经具备了完整的 agent
基座——规划、执行、工具调用、错误恢复——Cowork
只是把这些能力指向了新的文件类型，在隔离的虚拟机里跑 Python 代码，调用
python-pptx 和 python-docx 这些现成的开源库来操作 OOXML 结构。有了 agent
基座之后，接一个新的文件类型确实很快。

而且 Cowork 目前的实现还很粗糙。它甚至不能”看到”自己生成的 slide
长什么样——Claude 的 Read 工具不支持图片文件，这意味着它改 PPT
基本是在盲改：操作 XML
结构，但不知道渲染出来是否正确。这个问题在工程上是可以解决的（比如用
LibreOffice 渲染成 PNG 让 AI 自检），但目前 Cowork 没有做这一步。

创业公司也在证明同样的事情。Harvey AI 在法律文档领域做到了 100
页以上合同的单指令编辑。Gamma 做了一个 7000 万用户的 AI 演示工具，[估值 21 亿美元](https://gamma.app)。这些不是技术
demo，是在生产环境里跑着的产品。

那问题来了：Google 和微软坐拥最强的 AI
模型和最大的办公生态，为什么自家的 AI 在自家的 app
里连改个幻灯片都做不好？

最直觉的答案是”大公司掉头慢”。但这个解释经不起追问。里面都是聪明人，不可能没人想到要做
agentic。大厂缺的不是工程能力，甚至不是对 agent 架构的理解——微软做
Copilot Cowork 时，[直接用了
Anthropic 的 Claude 模型和 agentic 框架](https://www.microsoft.com/en-us/microsoft-365/blog/2026/03/09/copilot-cowork-a-new-way-of-getting-work-done/)，说明他们知道 agent
架构该长什么样。它们缺的是那个 agent
基座本身，而不去建那个基座，才是需要解释的事情。

有人会说是技术原因：OOXML 格式太复杂，Google Docs 的协作模型不适配 AI
的速度。这些确实是事实，但它们是表象而非根因。[Harvey
AI 用几个月就构建了 OOXML
的翻译层](https://www.harvey.ai/blog/enabling-document-wide-edits-in-harveys-word-add-in)，微软拥有这些格式的全部文档和工程能力，如果真想做，格式复杂度不会是阻碍。同样，Copilot
的 RAG
架构（检索然后生成文本建议，没有对文档的直接写入权限，没有验证闭环）看起来是技术局限，但它是被选择的结果，不是不可避免的技术约束。

那为什么不做？我认为有三个原因。它们单独看都不是致命的，但组合在一起，形成了一个非常稳固的均衡，让这两家公司被困在”聊天侧栏”的模式里出不来。

## 第一把锁：收入模型冲突

微软的整个生产力业务建立在 per-seat 订阅模式上：Copilot 每用户每月 30
美元。这个模式制造了一个根本矛盾：AI 越
agentic，用户需要的座位数就越少。

如果一个 AI agent 真的能自主完成一个员工的工作，企业就不再需要 500
个座位，而是 100 个、50 个，甚至更少。这不是假设。2026 年初，[一份被广泛传播的投资备忘录](https://x.com/CompoundWithRen)描述了
SaaSpocalypse：AI agent 压缩座位数的前景已经让 SaaS 行业市值蒸发了约 2
万亿美元。

这就把微软放在了一个不可能的位置上。做一个真正 agentic 的
AI，用户座位数减少，收入下降。做一个仅仅 assistive 的
AI，每个座位稍微好用一点，座位数不变，收入稳定。微软选了后者。结果就是一个每月
30 美元的聊天侧栏，让每个人稍微提效一点，但不会替代任何人。

这个选择在产品上的痕迹很明显。[Aragon
Research 的分析](https://arag.com/)直接说：Copilot was poorly designed, primarily to
enhance and protect Microsoft’s cash
cows。微软的定价策略也暴露了问题：Copilot 价格从 30 美元打折到 18
美元，[不到 20% 的销售人员能完成 AI
产品的配额](https://arstechnica.com/)，微软罕见地把 AI
销售目标砍了一半。当行业领头羊开始降价促销的时候，产品价值和定价之间的缺口就很清楚了。

[Bloomberg
报道了一个更直接的案例](https://www.bloomberg.com/)：制药巨头 Amgen 为 2 万名员工购买了
Copilot，结果大多数人转向了 ChatGPT，Copilot 主要只在 Outlook 和 Teams
这些微软专属场景中被使用。Bain & Company 的数据显示 ChatGPT 座位和
Copilot 座位的比例大约是 8:1。当员工有选择的时候，他们选了 AI
原生公司做的产品，而不是塞在旧产品里的 AI。

Nadella 自己知道这个困境。2025 年 9 月，他在内部 town hall 上[告诉员工](https://www.theverge.com/microsoft/612899/satya-nadella-microsoft-ai-dec-digital-equipment-corporation)他被
DEC 的案例困扰。DEC
的工程师做出了微型计算机的原型，但管理层拒绝大规模推广，因为那会蚕食高利润的小型机业务。最终
DEC 被 Compaq 收购，消失了。Nadella 的原话：有些我们经营了 40
年的业务，可能不再有意义。

但知道和能做到之间有巨大的鸿沟。微软的组织反应不是重组产品团队，而是[提拔了四位销售高管到
EVP](https://arag.com/)。一个产品问题，用销售去解决。

## 第二把锁：组织架构

Conway’s Law 说，一个组织的软件架构会映射这个组织的沟通结构。Google
和微软的生产力团队是在过去二十年里为确定性的、人类参与的软件构建的。测试基础设施、发布节奏、权限模型、质量指标，全都假设人类是行动的主体。AI
被塞进这个架构的结果，就是一个聊天侧栏——因为”用户发起请求，系统给出建议，用户确认执行”恰好是这些团队最擅长构建的交互模式。

这个路径还有一层更具体的技术债。2023 年，Google
和微软几乎同时面对”怎么把 AI
集成到办公产品里”这个问题，不约而同选择了同一个答案：通用的 chat sidebar
组件，一套 UI 适配 Docs、Sheets、Slides、Drive、Gmail
所有产品线。从工程复用的角度看完全合理——一个团队就能覆盖所有产品。但这个选择创造了路径依赖。Chat
sidebar 的整个技术栈——输入框、对话历史、markdown
渲染、复制粘贴按钮——都是为一问一答设计的。要把它改成
agent，需要重新设计交互模型（怎么展示 AI 正在做什么）、状态管理（AI
操作到一半失败了怎么办）、错误处理（怎么回滚）、以及和现有功能的兼容性（和评论、修订历史、协作编辑怎么共存）。这不是加个按钮的事，是需要重新来过。而
Claude Code 从第一天就是为 agent 设计的，Cowork
继承了这个架构，所以它天然就是 agentic 的。这不是 Anthropic
更聪明，是它没有 chat sidebar 的历史债务。

Google 的问题最具戏剧性。Sergey Brin 的泄露备忘录里有一个细节：Google
内部有一个经审批的编码工具列表，[Gemini
因为”奇怪的历史原因”被列在了禁用名单上](https://www.linkedin.com/posts/eliehabib)。Brin
有超级投票权，理论上可以决定公司的任何事情。但他说，修改这个政策花了”令人震惊的长时间”。他最后去找
Sundar Pichai 说：I can’t deal with these people, you need to deal with
this.

这个故事之所以重要，不只是因为它好笑。如果一个拥有公司控制权的创始人都无法快速改变一个明显错误的内部政策，那么要让安全、法务、合规、基础设施、产品这些团队协同起来做一个需要深度跨团队整合的功能（agentic
文档编辑），需要的协调成本是什么量级？

Google 的组织困难有据可查。Sundar Pichai [有 18
个直接下属](https://www.entrepreneur.com/)。每个产品面（Search、Workspace、Cloud、Android、YouTube）半自治运行，各有自己的
P&L。Workspace 团队关心生产力指标和企业客户满意度，Cloud 团队关心与
AWS 和 Azure 竞争，Gemini 团队关心模型能力。[Google 多次尝试重组](https://technology.org/)——合并 Brain 和
DeepMind，把 Gemini app 挪到 DeepMind 旗下，设立桥接 PM 和 AI
委员会——效果有限。[研究人员反馈的核心矛盾](https://kavukcuoglu.org/)是：研究卓越和产品速度需要相反的组织文化，没有一种组织形式能同时优化两者。

微软的问题表现不同但本质相同。Copilot 这个品牌被贴在了
Windows、Edge、Bing、Microsoft 365、GitHub、Azure、Power
Platform、Dynamics 365 上面，每个产品团队各自独立添加 Copilot 功能，[用户体验极不一致](https://gigazine.net/)。NoJitter 追踪了
Copilot 的品牌演变：2023 年是个人助手，2024 年是多人 AI，2025
年是团队协作，2026 年是自主
agent。每年换一个定位，每个定位都没做透。这不是战略摇摆，是十几个产品团队各自行动在品牌层面的投影。

对比之下，AI 原生公司的优势恰恰在于组织简单。OpenAI [研究和产品不分家](https://kavukcuoglu.org/)，做出 GPT-4
的团队也负责
ChatGPT，研究者每天都看用户反馈。这种紧耦合不是管理技巧，是小组织的自然状态。Google
在试图通过重组来复制这种状态，但大组织的重组往往只是换了报告线，没有改变信息流动的方式。Conway’s
Law 的核心教训是：你改不了信息流动的方式，就改不了产品的架构。

## 第三把锁：责任真空

企业客户对 agentic AI 的抵触不是空穴来风。[EY 的调查](https://www.ey.com/)显示近 9 成企业领导者都能指出
agentic AI 的采用障碍。[Deloitte](https://www.deloitte.com/)
发现只有五分之一的企业有成熟的 AI agent 治理模型。[Icertis 的调查](https://www.icertis.com/)显示 56% 的高管对让 AI
agent 自主做商业决策感到”非常担忧”。[Gartner 发现](https://www.gartner.com/) 83%
的企业因为信息治理问题难以将 Copilot 整合到日常工作中。

这些数据背后是一个很具体的问题：如果 Copilot
自主修改了一份合同里的赔偿条款，或者改动了一个财务模型里的关键假设，出了问题谁负责？用户？微软？模型提供商？[Reuters 2026 年 4
月的分析](https://www.reuters.com/)指出：传统的法律框架假设人类对系统的行为有实质控制。Agentic
AI 直接挑战了这个前提。目前没有成熟的法律框架、保险产品或合同模板来处理
AI 自主行为的责任归属。

这造成了一个不对称的风险结构。Agentic AI
搞砸一次——比如自动修改了一份重要合同——可能带来巨额诉讼和声誉损失。但做对十次，用户可能完全不会注意到。风险的下行远大于上行。对于服务数亿用户的大公司来说，保守是理性选择：让用户自己确认每一步，而不是让
AI 自主行动。

创业公司之所以能更激进，是因为它们服务的场景更窄、用户更专业。Harvey
AI 的用户是律师，每一份文档都会被人工审查。Gamma
的用户做的是内部演示，不是法律合同。在这些场景里做 agentic
是可行的，因为出错的后果被用户的专业能力和场景的低风险性兜住了。微软和
Google 服务的是全场景、全行业的用户群，没法做同样的假设。

而且，责任真空不只是大公司的外部约束，它也是内部阻力的合法武器。任何一个不想改变现状的团队，都可以用”合规风险”和”用户安全”来否决
agentic
功能的推进。这让责任真空和组织架构这两把锁互相加强：组织里推不动的事情，找到了一个完美的理由。

## 三把锁是互锁的

收入模型冲突、组织架构错位、责任真空，这三个因素互相加强。

收入模型使得投入 agentic
功能开发的资源优先级排不上去——为什么要花大力气做一个可能蚕食自己收入的功能？组织架构使得即便决策层意识到了问题（Nadella
的 DEC
演讲足够清楚），执行层也很难协调跨团队的深度整合。责任真空给了所有不想改变的人一个在道德和法律上都站得住脚的理由。

这三把锁共同决定了大厂在技术层面的选择：用 RAG 而不是 agent
架构，不构建 OOXML
翻译层，不做渲染验证闭环。这些技术选择不是工程能力不足的结果，而是在三把锁的约束下，保守方案被理性地选择了。

这就是为什么 Nadella 可以在 town hall 上引用 DEC
的案例来警告员工，但组织的实际行动是提拔销售高管。他不是不知道，是三把锁的合力太大了。

## 谁在打破这个均衡

均衡不是永恒的。外部力量正在从不同方向施压。

一类是绕过整个战场的玩家。[Gamma 的 7000
万用户](https://gamma.app)说明了一个事实：很多人并不需要
.pptx。当演示文稿变成一个可滚动的网页而不是一组幻灯片，Office
生态的格式锁定就失效了。Notion 的 AI Agent 可以在基于 block
的文档里自主编辑 20 分钟。这些工具完全不在微软和 Google
的地盘上竞争，而是重新定义了”文档”是什么。

另一类是在大厂的地盘上做到了大厂做不到的事情的玩家。Harvey AI [用几个月做出了
OOXML 翻译层](https://www.harvey.ai/blog/enabling-document-wide-edits-in-harveys-word-add-in)，在 Word 里实现了 100 页以上合同的单指令编辑。Claude
Code 把 .docx/.pptx
当作数据结构来操作，还能渲染检查结果，形成闭环。这些工具证明了大厂不做不是因为做不到。

还有一类是 AI 原生的工作平台。Coda
把文档变成了可编程的应用。它们不在格式和功能上竞争，而是改变了用户对”办公软件应该是什么”的期待。

这三类力量暂时还不构成对 Office 和 Google Workspace
的致命威胁。企业惯性和格式锁定仍然非常强——一个咨询公司不可能给客户交一个
Gamma 链接来代替 PowerPoint。但方向很清楚。

## 这件事的判断框架

回到最开始的问题：为什么 2026 年了，Google 和微软的 AI 在自家 app
里还不能 agentic 地编辑文档？

“大公司慢”是正确的观察，但不是有用的解释。有用的解释需要指出具体的锁定机制：收入模型冲突使得
agentic
功能在商业上不被优先；组织架构使得跨团队的深度整合在执行上极其困难；责任真空使得保守策略在法律和合规上是理性选择。这三把锁不是某个人的失误，而是这些公司在过去二十年的成功路径中自然积累下来的约束。

这个框架不只适用于文档编辑。任何一个大公司想在自己的核心产品里做
agentic AI，都可以用这三把锁来检验：它的收入模型是否允许 AI
替代人类工作？它的组织架构是否允许 AI
团队和产品团队深度耦合？它的客户群和法律环境是否允许 AI 自主行动？

对于正在观望 AI 的人来说，一个实际的判断标准是：不要看一家公司的 AI
模型有多强，要看它的收入模型和组织架构是否允许这个模型被充分释放。模型能力是必要条件，但远不是充分条件。2026
年的现实是，最强的模型被困在最差的产品里，最赚钱的产品被困在最保守的 AI
策略里。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
