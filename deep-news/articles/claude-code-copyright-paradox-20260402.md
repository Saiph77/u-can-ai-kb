---
title: "当 AI 写的代码被 AI 重写：Claude Code\n泄露暴露的版权真空"
date: 2026-04-02
source: https://yage.ai/share/claude-code-copyright-paradox-20260402.html
slug: claude-code-copyright-paradox-20260402
lang: zh
---
# 当 AI 写的代码被 AI 重写：Claude Code 泄露暴露的版权真空

发布于 2026 年 4 月 2 日 · [查看原网页](https://yage.ai/share/claude-code-copyright-paradox-20260402.html)

tags: AI Agent, 治理与合规, AI 产品与平台

2026 年 3 月 31 日，Anthropic 在一次 npm 更新中不小心把 Claude Code
的源码发出去了。约 [51.2
万行 TypeScript，1,900 个文件](https://blog.kilo.ai/p/claude-code-source-leak-a-timeline)，完整暴露。几小时内 GitHub fork
爆发，Anthropic 发起 DMCA 下架，[超过
8,100 个仓库被移除](https://arstechnica.com/ai/2026/04/anthropic-says-its-leak-focused-dmca-effort-unintentionally-hit-legit-github-forks/)。然后开发者 Sigrid Jin 用 OpenAI Codex
花两小时把整个项目从 TypeScript 重写成了 Python，项目叫 claw-code，star
数[超过
10 万](https://decrypt.co/362917/anthropic-accidentally-leaked-claude-code-source)。

到这里为止，它看起来像一个普通的代码泄露事故加一个高 star
的逆向工程项目。但这件事之所以值得单独写一篇分析，是因为它在同一个案例中同时暴露了版权法的三个裂缝，而这三个裂缝恰好是每个用
AI 写代码的人每天默默依赖的假设。

在展开之前，有一个法律背景需要先交代。2026 年 3 月 2
日，美国最高法院拒绝受理 Thaler v. Perlmutter 上诉，等于[确认了下级法院的裁定](https://copyrightlately.com/thaler-is-dead-ai-copyright-questions/)：纯
AI 生成的作品不享有版权保护。版权局进一步[明确](https://www.congress.gov/crs-product/LSB10922)：版权只保护包含人类创造性贡献的部分，而且申请注册时必须披露
AI 参与。换句话说，版权保护的前提是人类做出了创造性贡献，只是用 AI
当工具执行，这和完全由 AI
生成是两回事。至于这条线具体画在哪里，目前没有判例。

## 第一层：你用 AI 写的代码，版权可能没你想的那么稳

先说一个直觉。大多数开发者对代码版权的心智模型是：我写的代码归我，公司写的代码归公司，开源有许可证。在这个模型里，“谁写的”这件事通常很清楚。但如果写代码的是
AI 呢？

Claude Code 负责人 Boris Cherny 去年公开说过一句话：[“过去
30 天我对 Claude Code 的贡献 100% 由 Claude Code
自己写的”](https://futurism.com/artificial-intelligence/anthropic-development-claude-code-leak)，而且他”甚至不做小修改”。这句话本身是在炫耀产品能力，但放到版权框架里就有意思了。按照
Thaler 案确立的原则，如果代码的表达完全由 AI
生成，人类没有对代码的具体形式做出创造性控制，那这段代码就没有版权保护。

当然，Anthropic 可以辩护说：人类的创造性贡献体现在架构设计、prompt
编写、输出筛选这些环节。这确实是目前版权局[承认的思路](https://www.congress.gov/crs-product/LSB10922)。问题是这条线到底画在哪里。写一个
prompt 让 AI 生成 500
行代码，然后选了其中最好的版本，这算创造性控制吗？如果你让 AI
改了三轮才满意呢？如果你只看了一眼就 commit
了呢？没有判例，没有标准，全凭将来法院怎么理解”创造性贡献”这四个字。

泄露源码中的一个文件让这个问题更加尖锐。源码里有个
`undercover.ts`（90 行），实现了一种[隐身模式](https://www.modemguides.com/blogs/ai-news/claude-code-leak-architecture-analysis)：当员工用
Claude Code 向外部开源仓库提交代码时，系统会指示 AI
不添加联合作者标注，commit message 里也不提 Claude 或
Anthropic。这意味着 Anthropic 一边在 DMCA 中主张自己对 Claude Code
源码拥有版权，一边通过工具系统性地抹除 AI
参与的痕迹。而这些痕迹恰好是将来法院判断”人类 vs AI
贡献比例”时最直接的证据。

有[开发者在
Hacker News 上指出](https://news.ycombinator.com/item?id=47609294)，DMCA 的 512(f)
条款规定虚假版权声明可以构成伪证。如果 Anthropic 明知大量代码由 AI
生成仍主张完整版权，理论上存在法律风险。不过需要说明：目前还没有基于
512(f) 挑战 AI 生成代码版权的成功先例，这个风险更多是理论上的。

这层悖论对你意味着什么：如果你的产品代码大量由 AI
生成，你在合同里写的”所有代码为本公司专有财产”，法律基础可能比你想的脆弱。保留设计文档、代码审查记录、架构决策讨论的习惯，以后可能不只是工程最佳实践，还是版权主张的证据链。

## 第二层：用 AI 做的”洁净室重写”到底干不干净

这层的直觉是这样的。假设你的竞争对手泄露了源码，你想做一个合法的替代品。传统做法叫”洁净室重写”（clean-room
rewrite）：一组人读源码写功能规格，另一组从没见过源码的人根据规格重新实现。因为第二组人从头写的代码不可能”复制”原作，所以法律上通常认为结果是独立创作。[Sega
v. Accolade](https://en.wikipedia.org/wiki/Sega_Enterprises,_Ltd._v._Accolade,_Inc.)
是这个领域的经典判例，确认了这种方式可以作为合理使用的有力证据。

核心逻辑很简单：只要重写者没接触过原始代码，写出来的东西就是自己的。

claw-code 并没有尝试走洁净室流程——从公开信息看，它大概率就是直接让
Codex 对着泄露的源码做 TypeScript 到 Python
的逐模块翻译。这是一个比洁净室激进得多的操作，但它恰好把一个更深层的问题暴露了出来：即使你真的认真做洁净室，隔离团队、只传功能规格、让”干净”的一方独立重写，当重写工具换成
AI 时，隔离性这个前提本身就站不住了。原因很简单：Codex
这类模型是在海量代码上训练的，训练数据几乎确定包含 GitHub
上的公开代码，而 Claude Code 之前就有部分代码公开在 GitHub
上。所以即使你严格隔离了人类团队，AI
“重写者”本身很可能在训练阶段就已经”看过”原始代码了。

传统洁净室设计的全部法律说服力来自隔离性：重写者从未接触过原作，所以任何相似都是巧合或功能需要。claw-code
连这个表面隔离都没做，但更根本的问题是，即使做了也不够。一个在几乎所有公开代码上训练过的模型，从定义上就不可能”从未见过”任何特定的代码库。你用它做的每一次”重写”，都无法排除输出中包含对训练数据中原始代码的隐性复制。

chardet 事件是另一个说明这个问题的例子。Python 库 chardet 的维护者用
Claude 将项目从 LGPL 重写为 MIT 许可证，[引发了很大的争议](https://shujisado.org/2026/03/10/can-you-relicense-open-source-by-rewriting-it-with-ai-the-chardet-7-0-dispute/)。NVIDIA
工程师认为 [v7.0.0
对用户构成不可接受的法律风险](https://github.com/chardet/chardet/issues/331)。开源定义联合起草人 Bruce Perens
认为这种 AI 辅助重写会从根本上[瓦解软件许可证体系](https://www.theregister.com/2026/03/06/ai_kills_software_licensing/)。自由软件基金会执行董事
Zoë Kooyman 的立场很直接：[“一个已经摄入了目标代码的大语言模型所做的重写，没有任何’洁净’可言。”](https://arstechnica.com/ai/2026/03/ai-can-rewrite-open-source-code-but-can-it-rewrite-the-license-too/)

也有不同的声音。antirez（Redis 作者）[指出](https://antirez.com/news/162)，洁净室本来就只是诉讼中的”证据优化策略”，真正的法律问题是新代码是否复制了受保护的”表达”（expression），而非”功能”（function）。这个区分很重要：版权法保护的是代码的具体写法（变量命名、算法实现方式、代码组织方式），而非代码实现的功能本身。如果
claw-code 的 Python 实现和原始 TypeScript
在功能上等价，但在具体表达上完全不同，那就算 Codex
的训练数据里有原始代码，侵权也很难成立。反过来，如果 AI
生成的代码在数据结构、算法选择或整体架构上和原作高度相似，换了语言也可能构成侵权。[Oracle
v. Google](https://en.wikipedia.org/wiki/Google_LLC_v._Oracle_America,_Inc.) 确认了 API 声明即使在不同语言中表达仍受保护。

这个问题之所以没有简单答案，是因为传统版权法假设”复制”是一个离散事件：你要么见过原作要么没见过，要么复制了要么没复制。AI
模型把这个假设变成了一个连续谱。模型在训练中”见过”不等于”记住了”，“记住了”不等于”会在输出中复制”，但你也无法证明它没有。

这层悖论对你意味着什么：如果竞争对手用 AI
把你的闭源产品换语言重写，或者你自己在做类似的事，目前的法律框架给不出确定答案。这个灰色地带可能会持续数年，直到有判例出来。

## 第三层：Anthropic 对 AI 学习版权材料这件事需要同时持两个相反的立场

这层的直觉是最清晰的。Anthropic 在一个法庭上说”AI
从版权作品中学习并生成新东西是合理使用”，在另一个法律行动中说”AI
从我们的代码中学习并生成重写版本侵犯了我们的版权”。这两个立场之间有张力。

具体来说：2025 年的 Bartz v. Anthropic 案中，法院裁定 [Anthropic
使用版权图书训练 Claude
构成合理使用](https://www.akingump.com/en/insights/ai-law-and-regulation-tracker/district-court-rules-ai-training-can-be-fair-use-in-bartz-v-anthropic)，理由是这种使用”具有极高的转化性”。简单说，法院认为用版权书籍训练出一个通用聊天模型，和直接复制书籍内容是完全不同的事情，所以合法。这个判决对所有
AI 公司都很重要，因为它给训练数据的合法性提供了一个法律基础。

但当 Codex 从 Claude Code 源码”学习”并生成了一个功能等价的 Python
版本时，Anthropic 用 DMCA 下架了相关仓库。[Layer5
的分析](https://layer5.io/blog/engineering/the-claude-code-source-leak-512000-lines-a-missing-npmignore-and-the-fastest-growing-repo-in-github-history)捕捉到了这个矛盾的核心：如果”AI
从版权作品中学习并生成新输出”是合理使用（这是 Anthropic
在训练数据官司里的立场），那么”Codex 从 Claude Code 中学习并生成 Python
重写”在逻辑上也应该适用相同的原则。

两者之间确实存在可以区分的差异。Bartz
案涉及的是在海量书籍上训练出一个通用模型，这种使用的转化性很高：输入是书，输出是聊天机器人，两者在市场上不构成替代关系。而
claw-code
是针对一个特定代码库的定向重写，输出直接替代原作品的市场功能。[合理使用的四因素检验](https://www.reedsmith.com/articles/a-new-look-fair-use-anthropic-meta-copyright-ai-training/)中，“对原作品市场的影响”通常是最重要的考量，在这个维度上两个场景确实差距很大。

但这个区分并不能完全化解矛盾。Anthropic
的困境在于：它在训练数据案件中建立的法律论证（“AI
从版权材料中学习是转化性使用”）越成功，就越难阻止别人用同样的论证来辩护对
Anthropic 自身代码的 AI 重写。[正如
Layer5 指出](https://layer5.io/blog/engineering/the-claude-code-source-leak-512000-lines-a-missing-npmignore-and-the-fastest-growing-repo-in-github-history)，这是一个典型的 precedent
困境：你为自己建造的法律护城河，可能同时也在为对手修路。

一个值得关注的案件是 Doe v. GitHub（Copilot 集体诉讼），[已于
2026 年 2 月在第九巡回法院进行口头辩论](https://www.courtlistener.com/docket/69495342/doe-et-al-v-github-inc-et-al/)，尚未裁定。核心争点是 AI
编程工具是否移除了原始代码的版权管理信息。这个案件一旦有结果，会直接影响上述所有场景中的法律判断。

## 面对真空的实际判断

三层问题叠加之后，可以看到一个共同的模式：版权法中几个最基础的概念——作者身份、复制行为、转化性使用——都因为
AI
的介入而失去了原本清晰的边界。法律制度还没有追上来，风险被推给了实践者。

对使用 AI
写代码的开发者和公司来说，保留人类参与的证据链（设计文档、代码审查记录、架构决策讨论）会越来越重要。这些材料以后可能是证明”人类创造性控制”的关键。

对依赖闭源代码作为壁垒的 AI 产品来说，Claude Code
事件证明了一件事：即使代码没泄露，AI
工具也可能基于公开的功能描述生成功能等价的替代品。产品壁垒需要建立在更难被
AI 复制的维度上：数据飞轮、用户生态、集成深度。

对开源项目维护者来说，chardet 事件是预演。AI
辅助重写加重新许可的组合在法律上尚未被明确禁止或允许。关注 chardet
争议和 Doe v. GitHub
案的后续发展，比关注任何技术趋势预测都更有实际价值。

Anthropic 只是第一个被推到聚光灯下的。每一个用 AI
写代码的人，每天都在依赖这些尚未被验证的法律假设。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
