---
title: "Composer 2 的底座争议，以及 AI 编程工具的模型策略"
date: 2026-03-19
source: https://yage.ai/share/cursor-composer-2-base-model-20260319.html
slug: cursor-composer-2-base-model-20260319
lang: zh
---
# Composer 2 的底座争议，以及 AI 编程工具的模型策略

发布于 2026 年 3 月 19 日 · [查看原网页](https://yage.ai/share/cursor-composer-2-base-model-20260319.html)

> Composer 2 的关键变化不是又多训了一轮 RL，而是引入了更强的 continued
> pretraining 底座。 底座质量、继续预训练、RL
> 后训练和产品集成，正在一起决定 AI 编程模型的上限。
> 模型策略已经从单点优化转向整条训练链路的组合设计。

## 从三篇博客看 Cursor 的技术路线

要理解 Composer 2 的底座争议，需要先看 Cursor
在过去五个月里发了什么。三篇博客加上一篇配套研究笔记，拼出了一条完整的技术演进线。

2025 年 10 月，[Composer
1](https://cursor.com/blog/composer) 发布。它是一个 MoE 架构的模型，Cursor
从未公开过底座来源。当时有人直接问 Sasha Rush（Cursor
的研究负责人）这个模型是否基于某个开源 base model 做的 fine-tune，Rush
的回答是回避性质的：我们的重点在 RL
post-training，我们认为这是把模型变成强交互式 agent 的最佳路径。Composer
1 的全部技术叙事都围绕 RL 展开：在一个模拟 Cursor 生产环境的 agent
harness 里，让模型访问文件编辑器、终端、语义搜索等工具，然后用 RL
训练它做出更高效的工具调用决策。模型本身没有
chain-of-thought，速度是主打卖点，大部分交互在 30 秒内完成。

2026 年 2 月，[Composer
1.5](https://cursor.com/blog/composer-1-5) 发布。底座和 1
完全相同，没有做任何继续预训练。变化全部来自后训练：RL 的计算量扩大了 20
倍，后训练消耗的算力甚至超过了底座预训练本身。这是一个很值得记住的数字。同时引入了两个新的训练行为：thinking
tokens（自适应深度推理，简单问题快速响应，复杂问题延长思考链），以及
self-summarization（上下文接近长度极限时自动压缩历史信息，压缩结果本身参与
RL 的奖励信号）。博客里的关键判断是：RL for coding can be continually
scaled with predictable intelligence improvements。Cursor
在这个阶段的核心论点是，RL scaling law
在编程领域成立，只要投入更多后训练算力，模型智能就会持续提升。

2026 年 3 月 17 日，Cassano 和 Rush 发表了一篇关于 [self-summarization](https://cursor.com/blog/self-summarization)
的研究笔记，详细解释了压缩机制的实现方式和训练集成方法。两天后，[Composer 2](https://cursor.com/blog/composer-2) 发布。

Composer 2 和之前两个版本有一个根本差异：它引入了 continued
pretraining。博客原文是 these quality improvements come from our first
continued pretraining run, which provides a far stronger base to scale
our reinforcement learning。这句话意味着两件事。第一，Cursor 承认
Composer 2
有一个预训练底座，而且这个底座经过了继续预训练。第二，这是他们第一次做继续预训练，说明
Composer 1 和 1.5 都没有走这一步。

从 benchmark 数据看，这步棋的回报很大。CursorBench 从 1 到 1.5 提升了
6.2 分（38.0 → 44.2），从 1.5 到 2 提升了 17.1 分（44.2 →
61.3），后者接近前者的三倍。考虑到 1 到 1.5 之间已经投入了 20 倍的 RL
算力，这个对比暗示了一个可能性：RL-only 路线在 1.5
阶段已经接近某种收益递减，而 continued pretraining
提供了一个新的起点，让后续 RL 重新获得了更高的边际回报。Cursor
没有发布消融实验来证明这一点，但数据的方向是一致的。

## 底座争议的证据链

技术路线讲清楚之后，底座争议才有讨论框架。

有人在 Cursor 里调 OpenAI base URL 时看到了这个内部路径：

`accounts/anysphere/models/kimi-k2p5-rl-0317-s515-fast`

`kimi-k2p5` 指向 Kimi K2.5 模型族，`rl`
对应强化学习，`0317` 和 `s515`
像日期加训练步数的内部标记。这种命名在工程系统里是中间产物标记的常见形式。

同时，Moonshot 预训练负责人 Yulun Du 公开评论了 tokenizer
相似性并质疑许可合规，虽然相关帖子后来被删除。另有两名 Moonshot 员工确认
Cursor 没有获得这种用途的授权（同样已删除）。

不过，3 月 20 日，[Kimi /
Moonshot 官方账号](https://x.com/Kimi_Moonshot/status/2035074972943831491)
又给出了目前最强的一条一手证据。原文直接写到：Kimi-k2.5 provide the
foundation，并且进一步说明 Cursor 是通过 Fireworks AI 的 hosted RL and
inference platform 访问 Kimi K2.5，双方属于 authorized commercial
partnership。这里面有三层信息。第一，Kimi K2.5 作为 Composer 2
底座不再只是社区侧推断，而是模型提供方的公开确认。第二，Cursor
的做法确实是 continued pretraining 加 high-compute RL，这和 Cursor
自己的技术叙事一致。第三，Fireworks AI
首次被点名为中间的基础设施与托管平台。

综合来看：Cursor 官方确认了 continued pretraining
的训练路径，社区发现的内部路径强烈指向 Kimi K2.5，Moonshot
内部人员的早期公开反应与后续官方账号表态也指向同一方向。Kimi K2.5
血缘关系现在已经从高可信推断，进一步升级为接近半官方确认的状态。需要保留的边界是：这条
X 帖子经过编辑，原始版本不可见，而且 authorized commercial partnership
是公关语言，不等于外界已经看到了具体法律协议。

这里有一个常见的简化需要纠正。说 Composer 2 就是 Kimi K2.5 加
RL，会丢掉 continued pretraining 这一步。从 Cursor
自己的技术叙事来看，这一步恰恰是 Composer 2 相对于 1.5
的核心变化。Continued pretraining
调整的是模型的任务分布和能力重心，它决定了后续 RL
的起点在哪里。把它省略掉，就没办法理解为什么 2 和 1.5
之间的性能跳跃如此大。

## 这条路线并非孤例

Cursor 走的这条路线，在 AI
编程工具领域已经出现了至少两个直接对照案例。

Cognition 的 [SWE-1.5](https://cognition.ai/blog/swe-1-5)（也就是 Windsurf
背后的模型）采用了几乎相同的方法。他们的博客原文是：after careful evals
and ablations, we selected a strong open-source model as the base for
our post-training。社区分析指向 Zhipu 的 GLM-4.6。和 Cursor
一样，他们没有做继续预训练，直接在底座上跑 RL，而且 RL 环境是 Windsurf
自己的 Cascade agent
harness，模型在训练时就已经在使用产品内的具体工具。Cognition
在另一篇博客里还展示了更细粒度的做法：他们单独训练了一个小模型 [SWE-grep-mini](https://cognition.ai/blog/swe-grep)（基于
Phi-3-mini），专门优化了上下文检索环节的并行工具调用能力。这说明组件级别的
RL 定向优化也在出现。

底座提供方这边的策略也在变化。Zhipu 在 GLM-5 上采用了完全开放的 MIT
许可，没有用户量限制，鼓励下游产品在上面构建。这更像是基础设施层的策略：通过开源获取生态位，通过推理
API 和企业部署获取商业价值。Moonshot 的 Kimi K2 则选择了修改版 MIT
许可，对月活超过 1 亿或月收入超过 2000
万美元的衍生产品要求界面标注。两种许可策略对应两种生态定位。

## 这条路线为什么有效

一个自然的问题是：为什么在已有底座上做 RL
能产出这么大的能力增量，而不是只学到表面模式？

ICML 2025 有一篇来自港大、UC Berkeley、NYU 和 Google DeepMind
合作的论文给出了一个有用的解释框架。论文标题是 [SFT Memorizes, RL
Generalizes](https://arxiv.org/html/2501.17161v2)。核心发现是，SFT
倾向于记忆训练样本，在分布外场景下泛化能力有限，而基于结果奖励的 RL
能促进更深层的能力泛化，在视觉任务上的分布外提升高达 61%。RL
改善的是底层感知和推理能力，而不只是任务表现。

另一个相关发现是 RL 的隐式正则化效应。在多个高奖励解中，on-policy RL
天然偏向和 base model 在 KL 散度上接近的解。这意味着 RL
会在保留底座通用能力的前提下叠加领域技能，而不是把底座能力覆盖掉。这个特性使得在开源底座上做
RL 后训练成为一种高效的能力叠加方式，而非简单的行为克隆。

Moonshot 自己在 [Kimi
K2 的技术报告](https://moonshotai.github.io/Kimi-K2/)
里对预训练和后训练的关系也有一段很清晰的表述：Pre-training is the
crucial foundation for Agentic Intelligence, establishing the priors
that makes reinforcement learning exploration tractable, efficient, and
generalizable。预训练建立先验，RL
在这组先验上做高效探索。这个框架解释了为什么 Composer 2 的 continued
pretraining 会带来那么大的收益：它改变的是 RL 探索的起点质量。

从算力分配趋势来看，这条路线也和行业方向一致。[FundaAI
的分析](https://fundaai.substack.com/p/deepllm-2026-from-the-illusion-of) 指出，到 2025 年 OpenAI 已经将 70-80% 的训练算力分配给
mid-training 和 RL，而非预训练阶段。训练的重心正在后移。

## 许可与治理问题的边界

Kimi K2.5 的修改版 MIT 许可里有一条明确的触发条件：衍生产品月活超过 1
亿或月收入超过 2000 万美元时，需要在界面上显著展示 Kimi K2.5
标识。Cursor 的 ARR 估计在 20 亿美元量级。Composer 2 的界面里没有 Kimi
相关标注。

现在看，前一个版本里“如果 Kimi K2.5
血缘关系属实”这层假设已经没有那么强了。Moonshot
官方账号已经公开把这件事描述为 authorized commercial partnership，并点名
Fireworks AI
作为托管平台。这说明问题的重心已经部分移动：外界最需要解释的，不再只是底座到底是不是
Kimi K2.5，而是这套商业与技术安排的具体边界是什么。

但几个关键信息目前仍然不在外界手里：Cursor 和 Moonshot
之间是否有独立的商业协议，Fireworks
在其中承担的是纯托管角色还是也参与授权交付，continued pretraining 加 RL
之后的产物在法律上是否仍然构成原许可定义的衍生作品，以及 Cursor
自己的官方立场。在这些信息缺失的情况下，把这件事定性为 governance risk
仍然比直接定性为 license violation 更准确。新的 X
帖子削弱了“未经授权使用”这一路径的可信度，但没有把法律结构本身讲清楚。

不过 Windsurf 的情况提供了一个有意思的对照。Cognition 据信使用的是
Zhipu GLM-4.6，而 GLM 采用的是标准 MIT
许可，没有用户量门槛。底座选择直接决定了下游产品面临的许可约束强度。这让底座选型变成了一个兼具技术和商业维度的决策。

## 回到 Composer 2

把技术演进、底座证据、行业对照和研究支撑放在一起看，Composer 2
可以比较准确地描述为：以 Kimi K2.5 级别的 MoE 底座为起点，经过定向
continued pretraining 调整任务分布，再通过 long-horizon RL 和
self-summarization 训练长任务行为，最后深度集成进 Cursor
的编辑器工具链和 agent 执行环境。

从 Composer 1 到 2 的五个月里，Cursor
的技术叙事经历了一次值得注意的转变。1 和 1.5 的阶段，主张是 RL
后训练就是全部差异化来源，RL scaling law
成立，投入更多后训练算力就能持续提升智能。到了 2 这个阶段，continued
pretraining 被引入，而且带来了近三倍于前一次迭代的 benchmark
提升。这至少暗示，RL-only
路线在编程领域遇到了收益递减，而底座质量对后训练的放大效应被重新重视了。

这个观察对整个 AI
编程工具领域有参考意义。它意味着底座选择、继续预训练、RL
后训练和产品集成四个环节的相对权重，可能随着产品成熟度在持续变化。早期可以靠
RL
快速拉开差距，但到了一定阶段，底座本身的质量和针对性改造会重新成为瓶颈。能不能持续迭代这四个环节的组合，可能比单独在某一层投入更多算力更重要。

后续值得持续观察的几件事：Cursor 是否会在未来某个版本做完整的 base
model 预训练，Windsurf 和其他竞品是否也会从 RL-only 转向 continued
pretraining，以及当越来越多的产品共享同一批开源底座时，底座归属、许可合规和来源透明度会以什么频率出现在产品竞争的讨论里。

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
