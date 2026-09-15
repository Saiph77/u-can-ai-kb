---
title: "AI 闭着眼睛也能答对题：视觉理解评估的十年困局"
date: 2026-04-05
source: https://yage.ai/share/mirage-multimodal-benchmark-20260405.html
slug: mirage-multimodal-benchmark-20260405
lang: zh
---
# AI 闭着眼睛也能答对题：视觉理解评估的十年困局

发布于 2026 年 4 月 5 日 · [查看原网页](https://yage.ai/share/mirage-multimodal-benchmark-20260405.html)

## 一个历史悠久的问题

多模态大模型的视觉理解能力，主要通过 benchmark
来衡量。但如果把输入图片移除，模型仍然保留 70%~80% 的原始准确率，那么
benchmark 分数衡量的到底是什么？斯坦福团队的 [MIRAGE](https://arxiv.org/abs/2603.21687)
研究对一系列前沿模型做了系统性的无图测试，让这个问题有了最新的量化数据。社交媒体上流传的叙事是模型完全跳过了视觉通道，但问题的实质在
benchmark 本身：测试题的设计让纯文本推断成为一条有效的解题路径。

更关键的是，这个现象有近十年的研究积累。从 2016 年 VQA
研究者发现语言先验（language prior）可以绕过视觉输入，到 2018 年胸片 AI
被发现在识别医院标签而非肺部病变，再到 GPT-5.1 在无图条件下刷出 93.5% 的
mirage rate，这是一条清晰的演化线。VQA 的全称是 Visual Question
Answering，即视觉问答：给模型一张图加一个问题，让它基于图片内容回答。这是多模态模型评估中最常见的测试范式之一。MIRAGE
是这条线上最新的数据点，远早于它的研究已经揭示了同样的机制。

这篇文章要做的，是把这条线完整画出来，帮助读者理解三件事：为什么多模态
benchmark 反复失灵，为什么医学影像领域是重灾区，以及面对一个 benchmark
分数时，应该问哪些问题来判断它的可信度。

## 这件事的利害关系

如果一个视觉问答 benchmark
的大部分题目可以在完全不看图的情况下答对，那所有基于这个 benchmark
的模型排名、产品决策、论文结论都建立在不可靠的地基上。对于通用 AI
应用来说，这意味着产品团队可能高估了模型的视觉理解能力。对于医学 AI
来说，后果更严重：一个在 benchmark
上表现优异的胸片诊断模型，实际上可能在识别便携式 X
光机的标记而非肺部病变，而这种错误在临床环境中可能直接影响患者安全。

MIRAGE 论文的核心发现是，在所有测试的模型和 benchmark
组合中，文本信息的贡献都超过了视觉信息的贡献。如果这个发现可复现，它意味着当前主流的多模态评估体系在衡量模型是否真的在用视觉通道这个问题上，提供的信号极其有限。这对正在用
benchmark 分数做采购决策或部署决策的团队来说，是一个直接的实践问题。

MIRAGE 论文本身的 novelty
需要放在正确的位置上。这篇论文的贡献在于对最新一代前沿模型（GPT-5.1、Claude
Opus 4.5、Gemini 3 Pro）和当前活跃 benchmark
的系统量化，而观察到的现象本身，即模型可以绕过视觉通道在视觉任务上取得高分，在
VQA 和医学影像两个子领域都已经有近十年的研究积累。

## 十年脉络：从语言先验到 mirage reasoning

### 2016~2018：VQA 的语言先验问题

故事的起点是 2016 年左右 VQA 研究者的一个尴尬发现。Agrawal
等人首次系统分析了 VQA 数据集中的语言先验：当模型看到 What sport is…
这类问题时，高频答案 tennis
往往就是正确答案，完全不需要理解图片内容。2017 年，Goyal 等人在构建 [VQA v2](https://visualqa.org/)
时量化了这个问题的规模。他们报告，完全无视视觉输入的盲模型（blind
model）在二选一问题上能达到 67% 的准确率，在开放问题上也有 27%。

2018 年的 [VQA-CP v2](https://arxiv.org/abs/1712.00377)
进一步暴露了问题的深度。通过改变测试集的答案分布使其与训练集不同，当时的
SOTA 模型准确率直接下降了 24~27
个百分点。这个实验干净地证明了一件事：模型学到的很大程度上是问题表面形式和答案之间的统计关联，而非图片内容与答案之间的语义关系。

### 2018~2021：医学影像中的捷径学习

VQA 领域的语言先验问题在医学影像中有一个更危险的对应物。2018 年，[Zech
等人](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002683)在 PLoS Medicine
发表了一项研究：一个训练用来检测肺炎的深度学习模型，实际上学会了识别拍片医院的来源。他们发现，一个仅用医院来源信息做预测的简单模型就能达到
AUC 0.861，而 CNN 能以 99.95%
的准确率识别影像来自哪家医院。背后的机制很清晰：NIH 数据中肺炎患病率为
1.2%，而 Mount Sinai Hospital 为
34.2%，如此大的基线差异让模型可以完全忽略影像内容，只靠识别医院标记就能获得看起来不错的性能。该论文有超过
1400 次引用。

2021 年，[DeGrave
等人](https://www.nature.com/articles/s42256-021-00338-7)在 Nature Machine Intelligence 上报告了类似的发现：COVID-19
胸片检测模型约 50% 的准确率来自虚假的相关性（spurious
confounds），包括影像上的文字标记、患者体位和侧位标记（laterality
markers），而非肺部病变本身。所谓虚假的相关性，是指模型利用了和真正答案无关、但碰巧和标签关联的特征。论文的原文表述是模型
selects shortcuts over signal。这项工作累积了超过 430 次引用。

[Banerjee
等人](https://pmc.ncbi.nlm.nih.gov/articles/PMC11192466/)在 2023 年的 JACR 综述中系统总结了放射学 AI
中的捷径类型：肺炎检测用 ICU
便携式标记做代理，气胸检测用引流管做代理，这些捷径在模型的总体准确率中被隐藏，只有在特定亚群上分层评估时才会暴露。

这里有一个从 VQA 到医学影像的清晰映射关系。VQA
中的语言先验是模型利用问题的表面形式绕过图片。医学影像中的捷径是模型利用影像的非诊断特征绕过病变区域。底层机制相同：当存在一条比真正理解视觉内容更省力的解题路径时，模型会走那条路。

### 2024~2026：MIRAGE 和前沿模型时代

MIRAGE 论文的工作发生在这条脉络的最新节点上。研究者对 GPT-5.1、Claude
Opus 4.5、Gemini 3 Pro 等前沿多模态模型进行测试，移除图片输入后，在
MMMU-Pro、VQA-RAD、MedXpertQA-MM 等 benchmark
上测量残余准确率。论文报告，在所有模型和 benchmark
的组合中，无图准确率占有图准确率的 60%~99%，医学 benchmark
一致处于高端。

论文还引入了一个新概念：mirage
reasoning。它描述的是模型在完全没有收到图片的情况下，仍然生成详细的图片描述并基于这些描述进行推理的行为。在使用评估工作流
prompt 时，mirage rate（模型在无图时仍自信描述视觉内容的频率）可以达到
90%~100%。

同时期的其他工作从不同角度佐证了这个方向。[MMMU-Pro](https://arxiv.org/abs/2409.02813) 对原始 MMMU
进行后验过滤，去除纯文本可解的题目后，模型性能下降了 16.8~26.9
个百分点。[ViLP](https://arxiv.org/html/2501.00569v1)
设计了三图测试法（给模型三张图，只有一张对应正确答案），发现 GPT-4o
的准确率仅为 66.17%，远低于其在标准 benchmark 上的表现。[Wang 等人 2025](https://arxiv.org/abs/2509.19671)
在重新审视胸片模型性能时发现，当使用临床上下文（如疾病先验概率）对评估进行分层后，SOTA
模型的表现远低于总体准确率所暗示的水平。

[Jabbour
等人 2020](http://proceedings.mlr.press/v124/jabbour20a.html) 更早地研究了胸片 AI 中捷径的利用和预防，使用 transfer
learning
来缓解模型对虚假相关性的依赖。这些工作共同构成了一个完整的证据链：从
2018 年的 Zech 到 2026 年的
MIRAGE，在方法、数据集和模型代际上各不相同，但指向的核心问题高度一致。

## 三个驱动机制

为什么这个问题反复出现，而且随着模型进步似乎在恶化？根据现有文献和
MIRAGE 的数据，可以识别出三个相互叠加的机制。

**Benchmark 层面的信息冗余。** 多数 VQA benchmark
的问题本身就携带了大量可用于推断答案的信息。问题的措辞、选项的设置、领域的限定，这些文本线索加上模型内化的世界知识，使得图片成为冗余输入。用信息论的语言说，给定模型的先验知识
K，问题 Q 和图片 I 之间的条件互信息 I(Q; I | K) 往往很低。MMMU-Pro
通过过滤、MicroVQA 通过 RefineBot 审查 CoT
来重写题目，都在尝试提高这个互信息值，但效果有限：MicroVQA
的专家人工审查成本是每题 30~40 分钟，难以规模化；MMMU-Pro
过滤后性能下降明显，但仍无法保证剩余题目在设计上就必须依赖视觉输入。

**架构层面的捷径偏好。**
当前主流的视觉语言模型（VLM）采用浅层视觉编码器拼接深度语言模型的架构。语言模型组件在参数量、训练数据量和推理能力上远超视觉编码器。当模型面临两条路径，即仔细分析视觉输入（计算代价高、不确定性大）和从问题文本推断答案（计算代价低、经常正确），架构本身就倾向于走后者。HC-M3D
benchmark
的实验提供了直接证据：即使改变图片上的关键信息点位置（理论上应该改变答案），GPT-4o
的性能几乎没有变化，说明模型在很多情况下确实绕过了视觉通道。

**知识规模反转（Knowledge Scale Inversion）。**
这是三个机制中最值得关注的。随着模型参数量增大和预训练语料扩展，模型内化的先验知识
K 持续增长。对于任何固定的 benchmark，I(Q; I | K) 会随着 K
的增长而缩小。也就是说，对于 GPT-4V 需要看图才能回答的问题，知识更丰富的
GPT-5.1 可能纯靠文本推断就能解答。MIRAGE 的数据直接支持这个推断：GPT-4.1
的 mirage rate 为 43%，而更强大的 GPT-5.1 达到了
93.5%。这个差距反映的是更强的语言能力让绕过视觉通道变得更加容易，而非
GPT-5.1 的视觉能力退化。

这个推论指向一个不乐观的趋势：如果评估方法保持不变，模型越强，视觉评估的信号失真越严重。评估精度和模型能力之间存在动态博弈，而评估方这一边目前在落后。

## Mirage 和 Hallucination：理论区分，实践趋同

MIRAGE 论文提出了 mirage reasoning 和 hallucination
的显式区分。按论文的定义，hallucination
是在有效的认知框架内编造细节（比如看到一张猫的图片，描述成黑色，实际上是白色的），而
mirage
是构建整个虚假的认知框架（在完全没有图片的情况下描述图片内容并基于它推理）。

[Bai 等人 2024](https://arxiv.org/abs/2404.18930) 的 MLLM
Hallucination Survey 定义了一种相关的 IK（I
Know）hallucination：模型拒绝承认自己无法回答某个问题，转而给出自信的回答。IK
hallucination 和 mirage
在表现上非常接近，都涉及模型在信息不足时仍给出确定性回答。同一篇 survey
中定义的 event hallucination，即模型捏造虚构目标并围绕它构建叙事，与
mirage reasoning 在认知过程上几乎同构，区别仅在于 event hallucination
发生在图片存在但被错误描述的情境下，而 mirage
扩展到了图片完全缺失的情境。

这个理论区分在认知科学层面可能有意义，它确实指向了不同层次的认知失败（epistemic
failure）。这里的 epistemic 意为认知层面的、关于知识本身的。Epistemic
failure
指的是认知框架本身的崩塌，而非在正确框架里犯了细节错误。Hallucination
是在正确的认知框架里填错了细节，mirage
则是整个框架就是虚构的。但从实际后果来看，两者高度趋同：都导致 benchmark
分数不可信，都需要检测和缓解机制，都构成部署安全的风险。对于 AI
产品团队而言，区分 mirage 和 hallucination
的优先级低于一个更基本的问题：模型在这个任务上到底用了多少视觉信息？

## 社交媒体叙事的修正

回到社交媒体上的那个概括。模型完全跳过了视觉通道这一说法之所以流行，是因为它简洁且有冲击力。但它混淆了两个完全不同的命题。

MIRAGE 的数据表明的是：在当前主流 benchmark
上，大部分题目可以在不提供图片的情况下被正确回答。这是对 benchmark
质量的判断，而非对模型视觉能力的判断。Benchmark 上的 mirage score
高，说明这些 benchmark
未能有效区分两种行为：真正使用了视觉信息，还是依靠文本与知识推断出了答案。

模型是否具备真实的视觉理解能力，需要用不同的方法来测试。ViLP
的三图测试法是一个方向；要求模型完成只有通过观察图片才能回答的低级视觉任务（如计数、空间关系判断）是另一个方向。Rahmanzadehgervi
等人 2024 年的研究（[VLMs are
Blind](https://arxiv.org/abs/2407.06581)）发现，当前 VLM 在简单视觉任务上的准确率仅为
58.57%，这暗示视觉理解的真实水平确实有很大的提升空间，但这与模型完全忽略视觉输入是完全不同的诊断。

MIRAGE 论文自身在措辞上也比媒体报道审慎得多。论文使用的表述是 the
illusion of visual understanding，指向评估层面的幻觉，即我们以为
benchmark
分数代表了视觉理解，但实际上可能主要反映的是语言能力和知识储备。这是一个关于测量工具的判断，与模型视觉能力本身的判断分属不同层面。

## 这个问题会随模型进步改善还是恶化？

Knowledge scale inversion
机制给出了一个不乐观的预测：在评估方法保持不变的前提下，模型越强，问题越严重。每一代更强的语言模型都会使更多的
benchmark 题目变得可以通过纯文本推断解答。MIRAGE
报告的数据中，GPT-4.1（mirage rate 43%）到 GPT-5.1（mirage rate
93.5%）之间的跳变就是直接证据。

这意味着 benchmark
设计需要变成一个动态过程。每当模型能力显著跃升，现有 benchmark
的区分效度就会下降，需要重新校准。一种更根本的方向是在构建 benchmark
时就确保题目在设计上必须依赖视觉输入：改变图片内容必须改变正确答案。实现这个条件的代价很高（HC-M3D
的尝试表明，即使做到了这一点，当前模型仍然可能绕过），但它至少把问题推到了正确的层面上。

最终，这个领域面对的是一个持续的博弈：评估者努力设计出真正需要视觉理解才能通过的测试，而越来越强大的语言模型持续找到新的绕行路径。这个动态在过去十年里没有被解决，在可预见的未来也不太可能被一次性解决。它更可能成为多模态
AI 发展中的一个常驻议题，需要评估方法论的持续投入。

---

**主要来源**

- Asadi, O’Sullivan et al. (2026). MIRAGE: The Illusion of Visual
  Understanding. [arXiv:2603.21687](https://arxiv.org/abs/2603.21687)
- DeGrave et al. (2021). AI for radiographic COVID-19 detection
  selects shortcuts over signal. [Nature Machine
  Intelligence](https://www.nature.com/articles/s42256-021-00338-7)
- Zech et al. (2018). Variable generalization performance of a deep
  learning model to detect pneumonia in chest radiographs. [PLoS
  Medicine](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002683)
- Banerjee et al. (2023). Shortcuts Causing Bias in Radiology AI. [JACR/PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11192466/)
- Yue et al. (2024). MMMU-Pro: A More Robust Multi-discipline
  Multimodal Understanding Benchmark. [arXiv:2409.02813](https://arxiv.org/abs/2409.02813)
- Du et al. (2025). ViLP: Knowledge Exploration using Vision,
  Language, and Pose. [arXiv:2501.00569](https://arxiv.org/html/2501.00569v1)
- Bai et al. (2024). Hallucination of Multimodal Large Language
  Models: A Survey. [arXiv:2404.18930](https://arxiv.org/abs/2404.18930)
- Wang et al. (2025). Revisiting Performance Claims for Chest X-Ray
  Models Using Clinical Context. [arXiv:2509.19671](https://arxiv.org/abs/2509.19671)
- Jabbour et al. (2020). Exploiting and Preventing Shortcuts in Chest
  X-ray. [PMLR](http://proceedings.mlr.press/v124/jabbour20a.html)
- Rahmanzadehgervi et al. (2024). VLMs are Blind. [arXiv:2407.06581](https://arxiv.org/abs/2407.06581)
- Goyal et al. (2017). VQA v2. [visualqa.org](https://visualqa.org/)
- Agrawal et al. (2018). VQA-CP. [arXiv:1712.00377](https://arxiv.org/abs/1712.00377)

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
