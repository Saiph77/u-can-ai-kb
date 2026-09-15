---
title: "当神经网络学会假装自己是一台电脑"
date: 2026-04-13
source: https://yage.ai/share/neural-computer-e2e-learning-20260413.html
slug: neural-computer-e2e-learning-20260413
lang: zh
---
# 当神经网络学会假装自己是一台电脑

发布于 2026 年 4 月 13 日 · [查看原网页](https://yage.ai/share/neural-computer-e2e-learning-20260413.html)

你每天看到的电脑屏幕，如果不是操作系统在渲染，而是一个视频模型在逐帧”编造”出来的，你能分辨吗？

2026 年 4 月，Meta 和 KAUST 的研究团队发表了一篇名为 [Neural Computers](https://arxiv.org/abs/2604.06425)
的论文，提出了一个听起来很疯狂的想法：把计算、内存、I/O
全部折叠进一个视频生成模型的内部状态里，让模型本身成为一台”计算机”。他们基于
[Wan2.1](https://github.com/Wan-Video/Wan2.1)
这个视频扩散模型搭了两个原型，一个模拟终端命令行，一个模拟桌面
GUI。输入是一帧屏幕截图加上用户操作（键盘或鼠标），输出是下一帧屏幕。换句话说，模型在”演”一台电脑。

先说结论：这个方向今天对绝大多数技术从业者的日常工作没有任何直接影响。Neural
Computer 原型连两位数加法都做不对。但它指向了一条跟 AI Agent
完全不同的技术路径。如果你关心软件这个东西在未来十年会变成什么，这篇论文提供了一个认真理解的入口。

## 它做到了什么，没做到什么

Neural Computer 的终端原型 (NCCLIGen) 用大约 1100
小时的终端录屏训练，在视觉渲染上表现出人意料。终端画面的 PSNR 达到 40.8
dB，SSIM 达到 0.989（作为参考，PSNR 40dB
以上通常意味着人眼几乎无法分辨差异）。光标闪烁、窗口滚动、文字换行、全屏
TUI 程序的进度条，这些视觉细节都能正确渲染。GUI 原型 (NCGUIWorld)
的光标位置准确率达到 98.7%。输入
`pwd`、`date`、`echo`
这样的简单命令，模型能给出看起来合理的输出 ([MarkTechPost](https://www.marktechpost.com/2026/04/12/meta-ai-and-kaust-researchers-propose-neural-computers-that-fold-computation-memory-and-i-o-into-one-learned-model/))。

但一旦涉及需要逻辑推理的操作，模型就暴露了能力边界。两个两位数相加的结果几乎都是错的。这不是训练数据不够的问题，而是一个更深层的能力边界：视频模型擅长学习视觉模式（像素层面的统计规律），但不擅长学习形式化的符号运算。

论文自己的项目页面用了一个准确的描述：模型最先学会的是 “the
appearance of runtime”，即运行时的外观，而不是运行时的逻辑 ([Neural Computer project
page](https://metauto.ai/neuralcomputer/))。屏幕看起来像是一台正在工作的计算机，但模型并没有真正”理解”计算本身。

一个有意思的数据：110 小时经过精心设计的脚本化终端数据（在 Docker
里用脚本生成的标准输入/输出序列）的训练效果，显著超过 1400
小时的随机终端录屏。数据质量对这类系统的影响远大于数据数量。这跟 world
model 领域的一般经验一致。

## 这个脑洞不是孤立的

Neural Computer
的想法看似天马行空，但把它放进过去五年的发展脉络里看，它是一条清晰的技术路线的自然延伸。这条路线的核心问题是：神经网络能在多大程度上端到端地替代传统软件？

### 阶段一：学会模拟简单游戏 (2018-2020)

起点是 2018 年 Ha 和 Schmidhuber 的 [World Models](https://worldmodels.github.io/)，他们在 latent
space 里模拟简单的赛车游戏环境用于策略规划。2020 年，NVIDIA 的 [GameGAN](https://research.nvidia.com/labs/toronto-ai/GameGAN/)
更进一步：用 50,000 局 Pac-Man 的录像和对应的手柄输入训练一个
GAN，让模型学会重建整个游戏。模型不仅学会了 Pac-Man
怎么移动，还学会了吃到大力丸之后幽灵会变紫并开始逃跑这样的游戏规则。在四张
NVIDIA GP100 上训练四天，就能生成一个人类可以玩的 Pac-Man ([Engadget](https://www.engadget.com/nvidia-pac-man-ai-gamegan-130045785.html))。

这个阶段证明了一件事：游戏规则可以从纯视觉观察中涌现出来，不需要访问游戏引擎的源代码。但复杂度仅限于
2D 街机游戏。

### 阶段二：3D 游戏和实时交互 (2024)

2024 年是这个方向的爆发年。几个项目同时把复杂度拉升了一个量级。

Google 的 [GameNGen](https://gamengen.github.io/) 用
diffusion model 实时模拟经典 FPS 游戏 DOOM，在单个 TPU 上跑到 20fps
以上，PSNR
29.4。人类评测者在区分真实游戏截图和模型生成画面时的正确率只比随机猜测略高。稳定运行时间超过五分钟
([AI
CERTs](https://www.aicerts.ai/news/googles-real-time-generative-gamengen-breakthrough/))。

Decart 和 Etched 联合发布的 [OASIS](https://oasis-model.github.io/) 更激进：一个基于
Transformer 的模型实时生成 Minecraft
风格的开放世界，20fps，没有物理引擎，没有一行游戏代码。你可以走动、跳跃、放置方块、砍树。当然，如果你转过身，刚放的方块可能已经变成了别的东西，因为模型会”幻觉”
([MIT
Technology Review](https://www.technologyreview.com/2024/10/31/1106461/this-ai-generated-minecraft-may-represent-the-future-of-real-time-video-generation/))。

Google DeepMind 的 Genie 系列则从学术走向产品。[Genie
2](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/) (2024 年 12 月) 能从一张图片生成可交互的准 3D
环境，一致性维持约一分钟。到 [Genie
3](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/project-genie/) (2025 年 8 月)，分辨率到了 720p，帧率 24fps，延迟约
150ms，环境一致性仍然是约一分钟。环境一致性是涌现出来的，不是靠显式的 3D
表示保证的。

这个阶段证明了两件事：diffusion model / transformer 可以实时模拟复杂
3D 环境；但所有系统都有一个共同的 coherence 上限，大约一分钟之后画面开始
drift。

### 阶段三：从游戏到操作系统 (2025-2026)

Neural Computer 和 [NeuralOS](https://arxiv.org/abs/2507.08800)
几乎同时出现，把模拟对象从游戏环境换成了计算机界面本身。

NeuralOS 来自 Waterloo 大学和加拿大国家研究委员会，架构稍有不同：用
RNN
维护操作系统的内部状态（哪些应用在运行、窗口层叠顺序、最近的操作），再用
diffusion renderer 生成桌面画面。训练数据是 Ubuntu XFCE
桌面的录屏，包含随机操作和 AI agent
生成的类人操作。模型能正确渲染移动光标、双击打开文件夹、关闭窗口这些操作序列。但跟
Neural Computer 一样，精确的键盘输入建模仍然困难 ([Hugging Face](https://huggingface.co/papers/2507.08800))。

Runway 的 [GWM-1](https://runwayml.com/research/introducing-runway-gwm-1)
(2025 年 12 月) 走了更商业化的路线，把 world model
拆成三个分支：环境模拟 (Worlds)、机器人训练 (Robotics)、虚拟人物
(Avatars)，全部基于 Gen-4.5 视频模型做自回归实时生成。

Google/MIT/Berkeley 的 [UniSim](https://openreview.net/forum?id=sFyTZEqmUY)
则尝试了一条不同的路径：混合多种数据源（图片中的丰富物体、机器人数据中的密集动作、导航数据中的多样运动），训练一个能同时响应高层指令（“打开抽屉”）和低层控制（“向右移动
x 像素”）的通用模拟器。

这个阶段的核心推进是把模拟范围从”特定游戏环境”扩展到了”通用计算机界面”和”物理世界”。但核心困难没有改变：模型学会了环境的外观和简单的交互规律，但没有学会环境背后的逻辑。

### 并行路径：Tesla FSD 的端到端替代

值得一提的另一条路线是 Tesla FSD v12。2024 年 3 月，Tesla 把 300,000
行手写 C++ 控制代码完全替换成了一个端到端的视频 transformer
模型。这是”神经网络替代传统软件”在工业界最大规模的实际部署。但它的成功建立在极其苛刻的条件上：超过
84 亿英里的真实驾驶数据、Dojo 专用训练集群 100 petaflops
的算力、以及自动驾驶这个任务本身可以被反复练习和自动评分。

## 外观 vs 逻辑：这条路线最深层的矛盾

从 Pac-Man 到 DOOM 到 Minecraft 到 Ubuntu
桌面到终端命令行，这条线索的模拟对象越来越复杂，但有一个模式始终没变：模型先学会的总是视觉层面的东西，逻辑层面的东西总是最难的。

GameGAN 能渲染出逼真的 Pac-Man
画面，但幽灵的追逐策略只是大致正确。OASIS 能生成 Minecraft
的地形和方块操作，但世界一致性在转身后就可能崩塌。Genie 3
的环境一致性是涌现出来的，约一分钟后开始 drift。Neural Computer
能渲染出完美的终端画面，但 23 + 45 的结果是错的。

这个模式揭示了一个根本性的问题：视频模型的训练目标是最小化像素级预测误差，这个目标天然倾向于学习视觉统计规律（颜色分布、空间布局、运动模式），而不是抽象的逻辑关系。一个终端上
`23 + 45 = 68` 和 `23 + 45 = 71`
在像素空间里的差距微乎其微，但在语义空间里一个对一个错。视频模型的损失函数不区分这两者。

Andrej Karpathy 2026
年初的一个判断提供了一个有用的评估框架：如果一个任务可以被反复练习
(practice)、有明确评分 (scored)、可以重置环境 (reset)、有清晰的奖励信号
(reward)，AI 就能学好它。用这个框架看 Neural Computer 的任务：

渲染终端画面？满足所有四个条件。所以视觉质量可以很高。

执行正确的算术运算？“评分”需要的不是像素相似度而是符号精确匹配，这跟视频模型的训练范式不兼容。“练习”需要的不是更多录屏而是算术本身的形式化结构。这些条件目前都不满足。

这意味着，如果不在架构层面解决”视觉渲染”和”逻辑推理”的分离问题，单纯增加训练数据和模型参数不太可能让
Neural Computer 跨过”能正确计算”这个门槛。有趣的是，NeuralOS
选择了一条不同的架构路线，用 RNN 专门维护逻辑状态、diffusion
专门负责视觉渲染，可能是对这个问题的一种回应。

## 更宽的视角：两条路线的分叉

理解 Neural Computer
的价值，不在于这个原型本身能做什么，而在于它让我们看到 AI
与软件之间存在两条根本不同的路线，以及这两条路线的消长对技术投资和产品设计意味着什么。

**路线 A：AI 学会使用软件。** 这是当下的主流叙事。AI
Agent 在传统软件栈之上运行，通过
API、命令行、甚至模拟鼠标键盘来调用现有工具。软件本身不变，AI
是更聪明的用户。这条路线的隐含前提是：传统软件栈是稳定的基础设施层。

**路线 B：AI 学会成为软件。** 这是 Neural Computer
代表的方向。不是让 AI 操作终端，而是让 AI 直接生成终端画面。不是让 AI
调用物理引擎，而是让 AI 直接产出符合物理规律的画面。GameNGen 模拟
DOOM，OASIS 模拟 Minecraft，Genie 3 模拟任意可交互环境，Neural Computer
尝试模拟通用计算。这条路线的隐含前提是：软件本身可以被学习出来。

这两条路线不是互斥的，但它们对几类人有不同的判断价值。

如果你在做 AI 产品，路线 B 的进展意味着”给 AI 做更好的 API”和”让 AI
直接生成交互体验”之间的选择空间正在打开。Runway GWM-1
已经在向后者推进。这不是说 API
会消失，而是某些场景下，生成整个交互体验比拼装 API 调用可能更自然。

如果你在做基础设施，路线 B
的含义是：计算的一部分正在从确定性指令执行转向神经网络推理。这已经在自动驾驶里发生了（Tesla
FSD 用端到端模型替代了 30 万行
C++），正在视频生成和机器人训练里发生。这个迁移会改变 GPU/TPU
的经济学和部署架构。

如果你关心 AI 的长期走向，这两条路线的分叉指向一个更基本的问题：AI
与世界交互的终态，是一个善于使用工具的智能体，还是一个能直接模拟世界运行方式的系统？前者的天花板取决于工具链本身的能力，后者的天花板取决于学习的效率和精度。Neural
Computer
的实验恰好展示了后者目前的天花板在哪里：视觉可以学好，逻辑学不好。

## 它作为认知框架的贡献

Neural Computer
最有价值的部分可能不是它的原型本身，而是它提供的认知框架：把”模型”和”计算机”之间的边界当作一个可以被重新定义的东西。

在这个框架下，过去五年从 Pac-Man 到 Ubuntu 桌面的演进不再是一堆独立的
demo，而是同一个问题的渐进式攻击：神经网络能在多大程度上内化一个交互系统的完整行为？GameGAN
内化了一个 2D 街机的规则，GameNGen 内化了 DOOM
的实时渲染和物理反馈，OASIS 内化了 Minecraft 的开放世界生成，Genie
内化了任意图片到可交互环境的映射，Neural Computer
尝试内化的是通用计算本身。

每一步都在扩大”可被学习替代的东西”的范围。每一步也都撞上同一堵墙：学会外观比学会逻辑容易得多。

这堵墙是否能被突破，决定了这条路线最终是产出一批有用的世界模拟器（用于游戏、机器人训练、内容生成），还是真的通向一种新的计算范式。前者在今天已经在发生，后者可能需要一些我们目前还不知道的东西。

---

**参考来源**

- Neural Computer 论文: [arXiv:2604.06425](https://arxiv.org/abs/2604.06425)
- Neural Computer 项目页: [metauto.ai/neuralcomputer](https://metauto.ai/neuralcomputer/)
- NeuralOS: [arXiv:2507.08800](https://arxiv.org/abs/2507.08800)
- GameNGen: [gamengen.github.io](https://gamengen.github.io/)
- OASIS: [oasis-model.github.io](https://oasis-model.github.io/)
- Genie 2: [DeepMind
  blog](https://deepmind.google/blog/genie-2-a-large-scale-foundation-world-model/)
- Project Genie (Genie 3): [Google
  blog](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/project-genie/)
- GWM-1: [Runway
  Research](https://runwayml.com/research/introducing-runway-gwm-1)
- GameGAN: [NVIDIA
  Research](https://research.nvidia.com/labs/toronto-ai/GameGAN/)
- UniSim: [OpenReview](https://openreview.net/forum?id=sFyTZEqmUY)
- OASIS 报道: [MIT
  Technology Review](https://www.technologyreview.com/2024/10/31/1106461/this-ai-generated-minecraft-may-represent-the-future-of-real-time-video-generation/)
- GameNGen 分析: [AI
  CERTs](https://www.aicerts.ai/news/googles-real-time-generative-gamengen-breakthrough/)
- Neural Computer 报道: [MarkTechPost](https://www.marktechpost.com/2026/04/12/meta-ai-and-kaust-researchers-propose-neural-computers-that-fold-computation-memory-and-i-o-into-one-learned-model/)

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
