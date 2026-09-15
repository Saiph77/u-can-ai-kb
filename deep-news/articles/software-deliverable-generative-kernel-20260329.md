---
title: "当软件的交付物不再是软件"
date: 2026-03-29
source: https://yage.ai/share/software-deliverable-generative-kernel-20260329.html
slug: software-deliverable-generative-kernel-20260329
lang: zh
---
# 当软件的交付物不再是软件

发布于 2026 年 3 月 29 日 · [查看原网页](https://yage.ai/share/software-deliverable-generative-kernel-20260329.html)

过去二十年，软件行业卖的基本上是同一种东西：给人用的成品界面。功能固定，开箱即用，用户按设计者预设的方式点击操作。整个产品的价值通过
GUI 传递给人。但一种不同的交付物正在成形——不是给人点的，而是给 AI
调度的。它的用户不是坐在屏幕前的员工，而是代替员工执行任务的 AI
agent。这种变化不是某个产品经理的构想，而是已经在真实的企业环境中发生了。Klarna
最近的内部系统重构，是目前最清晰的一个样本。

## Klarna 具体做了什么

Klarna 过去两年做了一件很具体的事：用 [Neo4j
等工具构建内部知识图谱](https://neo4j.com/customer-stories/klarna/)，把散落在 1200 多个 SaaS
系统中的企业数据重新组织成统一的语义层。CEO Sebastian Siemiatkowski
自己的表述是 data equals
knowledge——关键动机不是省许可证费用，而是让碎片化的数据变成 AI
可以直接消费的知识。

在这个统一知识层之上，Klarna 部署了内部 AI 助手
Kiki，让员工通过自然语言直接查询和操作企业知识与流程。Kiki
已经在生产环境中运行。Sebastian 还在 [20VC
的公开访谈](https://www.thetwentyminutevc.com/sebastian-siemiatkowski-2)中演示了更进一步的原型：用 Claude 搭建在开源会计系统和 CRM
之上的 agent，展示 AI
如何在统一数据层上完成过去需要多个专业软件配合的工作。但这些原型目前仍然是
prototype，不是 Klarna 的生产系统。

需要区分的是：统一知识层 + Kiki 是已经落地的工程事实；Claude-based
的跨系统 agent 原型展示的是方向，不是已验证的生产能力。

## 这不是一个更聪明的界面

Klarna 值得认真分析，不是因为它淘汰了多少
SaaS，而是因为它在做一件不同性质的事：不是在做一个更聪明的界面，而是在重组内部的运行底座——把过去只有人能操作的系统，改造成
AI 也能调度的系统。

这种新的交付物大致由三层构成。

第一层是硬底座：支付清算、风控模型、商户网络，以及
records、permissions、transactions、audit
这些绝对不能出错的核心能力。这些不是 AI
能凭空生成的，它们是整个系统的地基。

第二层是知识层：Klarna 用 Neo4j
构建的统一知识图谱，把散落在各个系统中的业务语义、组织结构、流程规则重新编码成
AI 可直接消费的形式。没有这一层，AI
面对的就是一堆碎片化的数据，什么也做不了。

第三层是 AI 操作层：Kiki 和 Sebastian 演示的 Claude-based
原型，把过去需要人在多个 GUI 之间切换才能完成的复合操作，变成 AI
可以一步调度的高层动作。

我把这种交付物叫做生成内核（Generative
Kernel）：不是交付成品家具，而是交付核心部件、装配知识和杠杆工具，让 AI
可以按需组装、按需操作。在 AI 编程领域，这个模式已经在逐渐成形——比如
Stripe 如果要为 AI
编程时代重新设计开发者体验，大致也需要做同样的事：提供硬底座（支付
API）、写给 AI
看的知识体系（最佳实践、边界条件）、以及把复杂操作变成确定性调用的杠杆工具。Klarna
面向的是内部员工的 AI agent，Stripe 面向的是外部开发者的 AI
agent，但模式高度相似。这才是这件事值得注意的原因：它说明这个模式正在从开发工具向企业软件领域扩散。

## GUI 的角色重分配

在这个变化中，GUI
的命运是一个容易被简化的话题。更准确的描述是角色重分配。

在传统软件中，GUI
同时承担三个功能：操作入口（用户通过它执行动作）、信息展示（用户通过它理解状态）、流程约束（界面设计本身引导用户按正确路径操作）。当主要操作者从人切换到
agent，这三个功能的重要性发生了不对称的变化。

操作入口这个功能被大幅削弱。Agent 通过 API、tool
call、代码执行来操作系统，GUI
上的按钮和表单对它来说既慢又不精确。信息展示功能保留但角色变了：它不再是操作者的主视图，而是监督者的观察窗。人类通过
GUI 来审核 agent
的操作结果、发现异常、做审批、处理例外情况。流程约束功能则部分迁移到了自然语言层面：过去靠界面设计防止用户误操作，现在靠
skill 边界定义、权限设计和 agent 契约来约束 AI 的行为范围。

GUI 从人与软件的唯一接口，变成了人观察 agent
与软件交互的窗口。它仍然存在，仍然有价值，但它不再独占主控制面。主控制面开始转向自然语言
+ agent + tool call 这条链路。

这和我们在日常 AI 开发中的体验完全一致。用 Claude Code 或 Cursor
做项目时，你大部分时间不是在点 IDE 的菜单，而是在用自然语言描述意图，AI
去调用编译器、测试框架、文件系统、版本控制。IDE 的 GUI
仍然在那里，但它的角色已经从主操作面退到了结果预览和异常审核。Klarna
在企业软件中做的事情，和这个转变在模式上完全一致。

## 结果确定性

当操作者从人变成 agent，可靠性的类型也随之变化。

传统 SaaS
提供的确定性是过程确定性。用户点某个按钮、填某个表单、走某个审批流程，每一步的行为由界面设计和后端逻辑精确规定。这种确定性有效的前提是操作者是人，人需要被引导、需要防误操作、需要可预测的交互反馈。

Agent
关心的是另一种确定性：给定目标和约束，能否稳定地交付正确结果。它不关心中间走了哪条路径、点了哪个按钮、经过了几个页面。它需要的是结果确定性——明确的输入输出契约、可验证的结果标准、出错时的反馈信号。但这不意味着所有东西都进入结果确定性。Records、permissions、transactions、audit
这类硬底座仍然需要过程上高度可控的系统来托底。Agent
接管的是这些硬底座之上的查询、编排、跨系统操作和界面生成。

这正是 Klarna 重建内部系统时面对的核心设计选择。当 Kiki
代替员工去执行一个跨部门的业务流程，重要的不是它在哪个界面上点了什么，而是它是否在约束范围内完成了目标，以及当它偏离时是否有反馈机制让它自我修正或向人类求助。

## 对 builder 意味着什么

如果把 Klarna 的实践和我们在 AI
开发中的经验放在一起，可以提取出几个对 builder 有实际意义的判断。

第一，统一知识层是前提条件，不是可选项。Klarna
花了大量精力做数据统一，不是因为知识图谱时髦，而是因为没有这一层，AI
就只能在碎片化的数据上做碎片化的操作。对于任何想让 AI agent
在自己的系统中真正发挥作用的团队，第一步都不是接入大模型，而是审视自己的数据和知识是否处于
agent 可消费的状态。

第二，交付物的设计标准在变。如果你在做一个产品，值得思考的问题是：你的核心能力是否可以被
agent 直接调用，而不是只能通过人类点击 GUI
来触发？你的业务知识是否编码成了 AI
可以理解的形式，而不是只存在于界面设计和用户手册中？你是否提供了杠杆工具，让
AI 在关键操作上能达到确定性的结果？

第三，GUI 不会消失，但只做 GUI
会越来越危险。如果一个产品的全部价值都绑定在界面体验上，当 agent
成为主要操作者时，这个价值会被迅速绕过。真正有持久价值的是核心能力层和知识层，GUI
只是其中一个（而且正在变得不是最重要的那个）呈现渠道。

第四，这件事和 vibe coding 不是一回事。Vibe coding
的叙事是”人人都能用 AI 写代码”。Klarna
做的事情远比这深：它重建了企业数据的组织方式，让 AI
能在统一的语义层上执行复杂的跨系统操作。前者改变的是代码生成的门槛，后者改变的是企业计算的架构。两者的共同点是它们都在推动同一个方向：软件的主要操作者从人向
agent 迁移，软件的交付物从 GUI 成品向生成内核迁移。

## 标题与边界

这件事在传播中积累了不少噪音。Klarna CEO 上 [20VC
那期访谈](https://www.thetwentyminutevc.com/sebastian-siemiatkowski-2)被冠以”SaaS is Dead”的标题，随后被两种叙事接走：一种是”AI
正在取代 SaaS”，另一种是”这只是 CEO 在讲故事”。Sebastian
自己后来做了多次修正——他在 [TechCrunch
的采访](https://techcrunch.com/2025/03/04/klarna-ceo-doubts-that-other-companies-will-replace-salesforce-with-ai/)里说得很明确：“So no, we did not replace SaaS with an LLM.”
他甚至说过 “I don’t think it is the end of Salesforce; might be the
opposite.” 在 [TIME
的采访](https://time.com/charter/7378651/what-klarna-learned-from-its-ambitious-ai-rollout/)中，他承认 AI
对简单任务有效，人类支持会保留，甚至会成为一种高端服务。

这些修正值得记住。“用 AI 替代 Salesforce”比”用 Neo4j
重建企业知识图谱”好传播得多，但前者掩盖了真正重要的那一层：Klarna
的核心动作不是让 LLM 替代 CRM 功能，而是先把碎片化的企业数据统一成 AI
可消费的知识层，再在这个知识层上建新的接口和工作流。没有第一步，第二步不成立。

Sebastian 关于 switching cost 的判断也值得一提：the real kill shot is
when AI solves the switching cost of data。这个判断同样来自他在 [20VC](https://www.thetwentyminutevc.com/sebastian-siemiatkowski-2)
和 [TechCrunch](https://techcrunch.com/2025/03/04/klarna-ceo-doubts-that-other-companies-will-replace-salesforce-with-ai/)
中反复强调的数据层视角。当 agent
能把数据从旧系统中抽出来并重新接入新的知识层，SaaS
靠数据锁定建立的护城河就会被削弱。这是一个有力的判断，但前提是统一知识层真的能建好，agent
在复杂业务流程中的结果确定性真的能做到——这些条件今天还远未被大规模验证。

## 写在最后

这条线还很早期。Sebastian 演示的那些 Claude-based
原型，有多少能进入生产环境还不清楚。统一知识层的维护成本是否可持续，agent
在复杂业务流程中的可靠性能做到什么程度，这些问题都还没有答案。

但方向已经足够清晰：当 AI agent
成为软件的主要操作者，软件的设计重心会从”让人用得顺”转向”让 agent
调得动”。对 builder 来说，最值得跟踪的不是”谁又用 AI 替代了什么
SaaS”这类标题，而是交付物本身正在重新定义——从面向人类的成品界面，变成面向
agent 的生成内核：能力、知识和可验证的反馈回路。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
