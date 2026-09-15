---
title: "TurboQuant：Google 想把 KV Cache 压到 3 bit"
date: 2026-03-25
source: https://yage.ai/share/turboquant-kv-cache-3-bit-20260325.html
slug: turboquant-kv-cache-3-bit-20260325
lang: zh
---
# TurboQuant：Google 想把 KV Cache 压到 3 bit

发布于 2026 年 3 月 25 日 · [查看原网页](https://yage.ai/share/turboquant-kv-cache-3-bit-20260325.html)

## 先说结论：这件事跟你有什么关系

如果你在做长上下文相关的 AI 产品或推理服务，KV cache
的内存占用很可能是你当前最大的资源瓶颈之一。在 128K
甚至更长上下文的场景下，KV cache
占据的显存经常超过模型权重本身，直接决定了一块 GPU
能同时处理多少请求、推理的延迟/成本平衡点、以及你是否必须上更贵的硬件。

KV cache
压缩因此是一个实打实的工程需求，但过去的方案大多有让人头疼的实际障碍：有的要先拿离线数据做
calibration，换模型就得重来；有的压缩后还要额外存一堆
metadata（缩放因子、零点之类），标称 4 bit
实际省不了那么多显存；有的质量在论文上好看，真实推理时开始漂。这些摩擦不会写在论文摘要里，但做过
serving 的人都知道它们才决定方案能不能上线。

Google Research 在 2026 年 3 月 24 日发布了 [TurboQuant
博客](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)，论文 [TurboQuant:
Online Vector Quantization with Near-optimal Distortion Rate](https://arxiv.org/abs/2504.19874) 将在
ICLR 2026 发表。这个结果值得认真看，不是因为它声称了一个更低的
bit-width，而是因为它试图同时解决上面这三类摩擦。但需要提前说清楚：这是一个研究意义明确的结果，实际生产验证还有距离。下面逐层拆解。

## KV Cache 压缩为什么是个特殊问题

一般意义上的模型量化（比如
GPTQ、AWQ）通常作用于模型权重，而权重是静态的，可以在部署前离线完成压缩和校准。KV
cache
则不同：它在每次推理时动态生成，随输入序列增长而膨胀，生命周期和分布特征在不同请求之间差异很大。

这意味着 KV cache
压缩需要满足一组更苛刻的约束。首先，压缩必须在推理过程中在线完成，不能依赖预先收集的
calibration 数据集来决定量化参数。其次，KV cache 中的 key 和 value
承担的计算角色不同：key 参与内积运算来决定 attention 分布，value
参与加权求和来生成输出。这意味着 key
的压缩需要保证内积的精度，而不仅仅是逐元素的均方误差（MSE）。第三，任何附加的
metadata（比如 per-channel 或 per-token
的缩放因子、零点）都会抵消压缩带来的内存收益，尤其在 low-bit 场景下
metadata 开销占比会急剧上升。

过去几年在这个方向上已有不少工作，包括 KIVI、KVQuant、以及 QJL
等。但这些方法通常只覆盖上述约束的一部分。TurboQuant
的定位是试图把理论保证、在线可用性和工程开销控制三件事放到同一个框架里。

## TurboQuant 到底做了什么

理解 TurboQuant
需要知道它不是一个单独的算法，而是一个由三个组件组成的
pipeline。每个组件解决 KV cache 压缩中的一个具体痛点。

**第一步：用 PolarQuant 去掉 metadata 开销。**
传统量化方案在把浮点数压成 low-bit 整数时，需要为每组数据记录一套
normalization 参数（缩放因子和零点），这样解压时才能还原。问题是，当
bit-width 很低的时候，这些参数本身占的存储空间就不小了。比如你把数据压到
3 bit，但每组还要存一个 16-bit 的缩放因子和一个 16-bit
的零点，实际压缩比远没有标称值好看。PolarQuant
的解决方式是通过极坐标变换，把向量拆成范数（长度）和方向两部分，量化只作用于方向分量。因为方向分量天然是单位长度的，不需要逐组记录缩放参数，metadata
开销就被消除了。这是让后续 low-bit
量化在工程上真正可行的前提，不是一个可有可无的优化。相关论文：[PolarQuant: Quantizing KV Caches
with Polar Transformation](https://arxiv.org/abs/2502.02617)。

**第二步：TurboQuant 量化器做 MSE-optimal 的压缩。**
PolarQuant 处理完之后，方向向量被送入 TurboQuant
的核心量化器。这个量化器的特点是在线运行（不需要 calibration
数据）、并且在理论上可以逼近信息论的 rate-distortion
下界。也就是说，在给定的 bit budget
下，它造成的均方误差（MSE）接近理论上能做到的最小值。这一步主要保证了
value 的重建精度。

**第三步：用残差 QJL 保证 key 的内积精度。**
上面说过，key 在 attention 计算中参与内积运算，所以 key 的压缩不能只看
MSE，还要保证两个 key 向量之间的内积算出来是准的。MSE-optimal
的量化不自动保证这一点。TurboQuant
的做法是：先把第二步产生的量化残差（原始向量减去量化重建值）算出来，然后对这个残差施加一个
1-bit 的 QJL 变换（Quantized Johnson-Lindenstrauss
变换），用随机投影的方式把内积误差压下去。QJL
本身是一个独立的研究工作（[论文](https://arxiv.org/abs/2406.03482)，[GitHub](https://github.com/amirzandieh/QJL)），原始 QJL
直接对完整向量做 1-bit 投影来压缩 KV cache，而 TurboQuant
把它用在了残差上，作为一个校正层嵌入更完整的 pipeline。

三个阶段组合在一起，TurboQuant 同时覆盖了两个目标：MSE 失真优化（对
value 重要）和内积失真优化（对 key 重要），而且不需要离线 calibration
数据、不需要额外的 per-group metadata 存储。

## 数字口径：3 bits、3.5 bits、5x、6x、8x

性能数字是大家最关心的部分，但需要注意 Google
博客的表述和论文本身的精确口径有差别。

博客说 TurboQuant 可以把 KV cache 量化到 3 bits 且不牺牲模型质量，KV
内存至少减少 6 倍。论文摘要的措辞更精确：在 3.5 bits per channel
下实现质量中性（quality neutrality），在 2.5 bits per channel
下仅有边际退化（marginal degradation）。论文引言部分描述的压缩倍数是超过
5 倍（more than 5x）。

这两组数字并不矛盾，但不应混为一谈。博客面向更广泛的受众，采用了四舍五入后的说法；论文的口径更精确，区分了不同
bit-width 下的质量表现。在评估这个结果时，应该以论文口径为准：3.5 bits
per channel 质量中性是有实验支持的较强 claim，3 bits
以下的表现需要更仔细地对照具体 benchmark 结果才能下判断。

博客还提到在 4-bit 设置下，H100 上相比 32-bit 未量化 key 可以获得最高
8 倍的性能提升。引用这个数字时需要注意两点：它描述的是 key
侧的计算性能提升而非整体推理吞吐量，而且依赖于特定的 kernel
优化实现。

博客中提及的评估范围覆盖了 Gemma 和 Mistral 模型家族，在
LongBench、Needle In A Haystack、ZeroSCROLLS、RULER、L-Eval
等多个长上下文 benchmark 上进行了测试。

## 什么是新的，什么是继承的

理解 TurboQuant
的贡献需要分清楚哪些想法是它提出的、哪些是它从已有工作中借来的。

QJL 用 1-bit 随机投影来压缩 KV cache 的思路不是 TurboQuant
首创的，QJL 有独立的论文和 [官方 GitHub
仓库](https://github.com/amirzandieh/QJL)。PolarQuant 用极坐标变换消除 metadata
开销也是独立发表的工作。随机旋转和 Hadamard 预处理等技巧在 SpinQuant
等先前工作中也已出现。

那 TurboQuant
的贡献到底在哪？它把这些以前分散发展的思路拉到了一起，组成了一个端到端的
KV cache 压缩
pipeline，并且在理论上为整体的失真率给出了更紧的保证。打个比方：PolarQuant
解决了 metadata 问题，QJL 解决了内积保持问题，TurboQuant
量化器本身提供了 MSE-optimal 的压缩核心——但在 TurboQuant
之前，这三件事是各做各的，没有人把它们串成一个连贯的、有统一理论支撑的
pipeline。

这个区分很重要，因为它影响对结果可推广性的判断。每个组件的可靠性已经有各自独立的验证，但组件整合后的
pipeline 效果目前主要依赖 TurboQuant
论文自身的实验结果。换句话说，单个零件是经过检验的，但这辆车作为整车的路测数据还比较有限。

## 对你的日常工作意味着什么

前面已经解释了 TurboQuant
在技术上做了什么。这一节换个角度，聊几个它背后隐含的、但还没有被充分讨论的工程判断问题。

**方案选型的评估维度可能要改。** 过去评估 KV cache
压缩方案，通常先看压缩率和质量保持，然后看 calibration
成本和模型适配工作量。TurboQuant
提出了一个新的参考系：如果存在一类方案可以同时做到在线运行、无 metadata
开销、有理论保证，那么需要离线 calibration 或引入额外 metadata
的方案在选型中的说服力就会被压低。即便 TurboQuant
本身不成为最终标准，它也可能改变后续方案的评判门槛。

**长上下文场景的容量规划逻辑会变。** 假设 KV cache
真的能可靠地压到 3-4 bit
且质量中性，对容量规划的影响不只是省显存。它会改变 batch size
上限（同一块 GPU 能并发更多请求）、影响是否需要 tensor parallelism
来容纳 KV cache、以及在什么上下文长度下需要切换到 offloading
策略。这些是二阶效应，但对成本模型的影响可能比单纯的显存节省更大。

**推理框架的集成优先级排序。** vLLM、TensorRT-LLM
等框架对新量化格式的支持通常需要专门的 kernel 开发。如果 TurboQuant 的
pipeline 足够标准化，它有可能降低 kernel 适配的碎片化程度——一套 kernel
支持一个统一的量化格式，而不是为每个方案分别做适配。但这取决于
TurboQuant 能否成为事实标准，目前还太早。

## 还有哪些问题没有解决

以下几点是目前明确的开放问题，在参考 TurboQuant
的结果时需要纳入考量。

**开源与可复现性。** TurboQuant
目前没有作为独立仓库正式开源。QJL 有官方 GitHub 仓库，但完整的
TurboQuant pipeline（包含 PolarQuant 预处理和残差 QJL
阶段）的可复现实现尚不公开。在社区能够独立复现之前，论文中的性能数字应被视为可信但单源的实验结果。

**模型覆盖范围。** 目前公开的评估主要在 Gemma 和 Mistral
家族上完成。Llama、Qwen 等其他主流模型家族的表现，以及不同模型规模下的
scaling 行为，还需要更多验证。

**Kernel 与框架集成。** 博客中的 H100
性能数字依赖于特定的 kernel 实现。要把 TurboQuant 的量化格式集成到
vLLM、TensorRT-LLM 或其他主流推理框架中，需要专门的 kernel
开发。这通常是量化方案从论文走到生产线上最费时间的一步。

**安全性和对齐影响。** 量化对模型安全性（如 safety
alignment 的保持程度）的影响在 TurboQuant
的工作中没有专门讨论。safety-critical 的部署场景需要对此做独立评估。

**随机投影的稳定性。** TurboQuant 中 QJL
阶段使用随机投影矩阵，不同随机种子的选择是否会导致显著的性能波动，论文中讨论有限。在生产环境中，这关系到结果的可预测性。

## 小结

TurboQuant 把三条以前各自发展的技术路线——PolarQuant 消除 metadata
开销、QJL 保持内积精度、在线向量量化逼近理论最优——整合成了一个连贯的 KV
cache 压缩
pipeline。它不是一个全新的压缩范式，但在部署摩擦、工程开销和理论严谨性上，比之前的单点方案都往前走了一步。

至于它能不能大规模用于生产，取决于三件事：开源实现的推进速度、主流推理框架的
kernel
适配、以及更广泛的模型和场景验证。现在它处于研究意义明确、工程相关性真实、但生产就绪性尚未证明的阶段。

---

**来源**

- Google Research Blog: [TurboQuant:
  Redefining AI efficiency with extreme compression](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/) (2026-03-24)
- arXiv: [TurboQuant: Online
  Vector Quantization with Near-optimal Distortion Rate](https://arxiv.org/abs/2504.19874) (ICLR
  2026)
- arXiv: [QJL: 1-Bit
  Quantized JL Transform for KV Cache Quantization with Zero
  Overhead](https://arxiv.org/abs/2406.03482)
- arXiv: [PolarQuant:
  Quantizing KV Caches with Polar Transformation](https://arxiv.org/abs/2502.02617)
- QJL GitHub: [github.com/amirzandieh/QJL](https://github.com/amirzandieh/QJL)

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
