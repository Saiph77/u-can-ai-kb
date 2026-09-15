---
title: "如果研究真有用，为什么不偷偷用？AI\n公司公开和开源研究的产业逻辑"
date: 2026-03-25
source: https://yage.ai/share/why-ai-companies-publish-open-source-research-20260325.html
slug: why-ai-companies-publish-open-source-research-20260325
lang: zh
---
# 如果研究真有用，为什么不偷偷用？AI 公司公开和开源研究的产业逻辑

发布于 2026 年 3 月 25 日 · [查看原网页](https://yage.ai/share/why-ai-companies-publish-open-source-research-20260325.html)

---

一个常见的直觉是：如果某项 AI
研究真的能显著降低推理成本或提升模型能力，发现它的公司应该闭口不言，独享优势。这个直觉在很多行业都成立，在
AI 行业却反复被打破。Google DeepMind 在 2025 年 NeurIPS 上发表了超过 175
篇论文。Meta 把 Llama 系列的权重直接开放下载。DeepSeek
不仅公开了模型权重，还详细披露了 Multi-head Latent Attention
等训练工程细节。NVIDIA 把推理操作系统 Dynamo 整个开源了。

这些行为看起来是在主动放弃竞争优势，但每一个做出这些选择的公司都不傻。要理解它们为什么这么做，需要把问题拆开两层来看：第一，公开的到底是什么；第二，公开之后谁得利。

## 先分清楚：公开的是哪一层

讨论 AI
公司的开放行为时，最容易犯的错误是把所有形式的公开混成一件事。实际上，从论文到产品分发，至少可以分成六个层面，每一层的开放逻辑截然不同。

**论文和方法** 是扩散最快的一层。一个基础架构创新——比如
Transformer、知识蒸馏、Mixture of
Experts——即使某家公司不发表，几周到几个月内也会被同行独立发现或逆向推导出来。保密论文的实际收益很低，但不发表的代价很高：研究者会因为缺少发表自由而离开。LeCun
2025 年底离开 Meta 的原因之一，就是他认为 FAIR
实验室的发表自由正在被收紧。他随后创立的 AMI Labs 拿到了 10.3
亿美元种子轮，说明顶级研究者的流失不只是声誉损失，是直接创造出一个新的竞争对手。

**开源代码和工具链**
比论文更进一步。论文告诉你原理，代码让你直接跑起来。一旦开源，第三方会主动帮你做硬件适配、框架移植、性能优化和二次封装，原本属于发布方的工程成本被分摊给整个社区。这是后面会重点展开的机制。

**协议、SDK 和接口标准**
是一个容易被低估的层面。Anthropic 把 Model Context Protocol（MCP）捐给了
Linux Foundation，月下载量达到 9700 万次，OpenAI 和 Google
也被迫采用。谁先定义了默认接口，谁就更容易成为后续工具生态的中心节点。开放协议不是慷慨，是在争夺架构定义权。

**模型权重**
是开放行为中最重的一步。权重一旦发布就不可撤回，任何人都可以在此基础上微调和部署。Meta（Llama）、阿里（Qwen）和
DeepSeek
选择了这条路，因为它们各自的商业模式不依赖权重本身的独占。OpenAI 和
Anthropic 的权重严格闭源，因为 API
差异化定价就是它们的核心收入来源。Google 两头下注：小模型 Gemma
开放，旗舰 Gemini 闭源。

**训练数据和对齐数据**
几乎没有公司公开。训练数据是可持续的差异化来源，积累需要时间和资金，而且涉及版权争议。OpenAI
从未公开过 Books1 和 Books2 的具体来源，Anthropic 在 2025 年和解了 15
亿美元的版权案。对齐训练数据则更加敏感，因为它同时涉及商业价值和安全考量。

**产品分发和用户行为数据**
是所有公司严格封闭的底线。ChatGPT 4 亿周活跃用户、Meta AI 5
亿用户、Google 在搜索中嵌入 Gemini
带来的使用数据，这些入口的网络效应和行为数据没有任何公司会拿出来共享。可以说，上面所有层面的开放行为，最终目的都是为了保护或扩大这个封闭的分发层。

理解了这个层级之后就会发现，说一家公司”开放”或”封闭”是过度简化。更准确的描述是：每家公司都在某些层面开放、另一些层面封闭，而这个边界精确反映了它的利润池位置。

## 为什么公开研究本身常常是理性的

回到开头的问题。公司不选择偷偷用，最根本的原因不是利他主义，而是一个经济学概念：commoditize
your complement——把你不靠它赚钱的那一层做成
commodity，从而把利润集中到你更强的互补层上。

Joel Spolsky 很早就把这个机制写清楚了。IBM 开放 PC
架构不是因为善良，而是因为它的利润在服务和大型机。Google 做 Android
开源不是情怀，而是因为智能手机越 commodity 化，搜索广告收入越高。AI
行业正在发生完全相同的事情，只是参与者更多、层级更复杂。

NVIDIA 是这个逻辑最纯粹的案例。Jensen Huang 在 GTC 2026
上明确把竞争重心从模型训练转向持续推理。他的比喻是把模型比作流水线上的配方，配方谁家的都行，但工厂得是
NVIDIA 的。NVIDIA 开源推理操作系统 Dynamo，培育多极模型生态（Nemotron
Coalition 覆盖了法国的 Mistral、印度的 Sarvam
和硅谷独立团队），用模型无关的基础设施定位确保一件事：无论哪家的模型胜出，硬件层利润都归自己。模型层越
commodity 化，推理需求越大，GPU 销售越好。Dynamo 是开源的，但
disaggregated serving 和 KV cache pinning 的最优实现深度依赖 NVLink
带宽和 HBM4 内存层级。开放的是软件接口，锁定的是硬件消费。

Meta 的开放逻辑不同于 NVIDIA，但底层推理一致。Meta 的核心利润不在模型
API，而在广告系统、社交分发和平台控制力。Llama 开源是一步典型的
commoditize your complement 操作：基础模型层越 commodity 化，OpenAI 和
Anthropic 这类按模型 API 直接收费的公司的定价权就越弱，而 Meta
自己的分发渠道（WhatsApp、Instagram、Facebook、Ray-Ban 智能眼镜）的 AI
能力供给就越充裕。Zuckerberg 2024 年的公开信 Open Source AI is the Path
Forward 的核心论点就是：开源是避免被单一模型供应商锁定的方式。Llama 4 在
HuggingFace 上有超过 85000 个衍生模型，这些衍生模型的开发者在替 Meta
完成微调、适配、教程和二次封装的工作。

不过，Meta 的开放策略在 2026 年出现了转向的迹象。LeCun 离职时批评
Meta 内部研究越来越封闭；同时 Meta 开始开发闭源的 Avocado
模型。这说明开放策略不是永久承诺，而是随竞争格局和利润池变化持续调整的动态选择。

Google 和 DeepMind
的开放边界又不一样。它们更愿意开放的是研究工具链（JAX、Flax、Optax）、小模型（Gemma）和基础科学资产（AlphaFold），这些东西的共同特征是能放大
Google Cloud 的吸引力和研究生态的影响力。开发者在研究阶段习惯了 Google
的技术栈，后续更容易把工作负载导向 Vertex AI。但旗舰能力 Gemini
的闭源是坚定的，因为这是 Google Cloud 差异化的核心。DeepMind
保持高论文产出（NeurIPS 2025
论文数量业界第一）则是人才策略的硬需求，长期研究者留存率是 AI
行业最高之一，靠的就是学术自由承诺和发表文化。

## 开源降低的是 shipping friction，而不只是研究传播摩擦

到这里可能有人会问：就算公开研究在经济上是理性的，为什么很多公司还要更进一步，把代码、工具链甚至权重都开源出来？

答案在于，开源解决的问题和论文解决的问题属于不同层面。论文解决的是知识表达：让同行知道你做了什么。开源解决的是部署和采用路径：让别人能把你的东西接住、集成、跑起来、教给更多人、部署到真实场景中。这个从知识到采用的链路，可以叫做
shipping
friction，它比研究传播摩擦大得多，而开源是降低它最有效的手段。

具体来说，开源通过至少五个机制降低 shipping friction。

第一，把适配成本外部化。只发论文的时候，所有复现和集成都要发布方自己做，或者等别人从零复现。一旦代码和推理实现开源，第三方会主动完成硬件优化、框架移植、云服务封装和企业定制。这意味着原本属于发布方的适配成本被分摊给整个生态。Qwen
在这方面的案例非常典型：它已经被 vLLM、HuggingFace
Transformers、TensorRT-LLM 和 LlamaFactory 原生支持，开发者使用 Qwen
时几乎不存在额外的技术集成成本。阿里没有为每个框架逐一做适配工作，是社区替它完成的。

第二，把协议和框架做成默认选项。开源一套接口或工具链，争夺的是架构定义权。谁定义了默认接口，谁更容易成为后续生态的中心。NVIDIA
把 Dynamo
开源，表面上是方便大家用，实际上是让所有推理优化工作都针对自己的硬件栈展开。Anthropic
开源 MCP 也是同样的逻辑：一旦 MCP 成为 Agent
与工具交互的行业标准，Claude 在工具生态中的中心位置就得到了保障。

第三，降低开发者教育成本。开发者先在开源模型和工具链上形成习惯和肌肉记忆，后续迁移到商业平台会更自然。研究阶段和生产阶段之间的路径被打通之后，市场教育成本显著下降。Google
开放 Gemma 就有这个考虑：开发者在 Gemma 上学会的 API
模式和技术栈习惯，未来可以平滑迁移到 Vertex AI 上的 Gemini。

第四，降低企业采用门槛。很多组织，银行、医疗机构、政府部门，因为数据合规要求不能把数据发给第三方
API。开源权重让它们可以本地部署，直接消除了一个关键的采用障碍。这也是为什么阿里和
Meta 在企业场景的渗透不完全依赖 API 调用量，本地部署的 Qwen 和 Llama
在很多场景中成为默认选择，但这些使用量不会反映在 API 统计里。

第五，让互补资产受益。如果你的核心利润在云、硬件、广告或分发，而不在模型本身，那让模型和工具更便宜、更容易
ship，反而放大了你的核心资产价值。这是前面讲的 commoditize your
complement 在 shipping 层面的具体展开。

把这五个机制合在一起看，开源做的事情本质上是：把一个原本要发布方自己承担的
GTM、集成、evangelism
和教育成本，外包给了整个生态。这不是慈善，是成本社会化。

## 不同公司的利润池、互补资产和开放边界

理解了上面的机制之后，不同公司之间的策略差异就容易解释了。差异的根源在于：每家公司的利润池位置不同，因此它想要
commodity 化的层面不同，想要保护的层面也不同。

**NVIDIA** 的利润池 100%
在硬件层。它的开放策略是所有玩家中最激进的：开源推理 OS、开放 Nemotron
模型权重和训练 recipe、拥抱第三方 Agent 框架。同时通过 NVLink 绑定和
Privacy Router 等控制点维持硬件层定价权。它的最优世界是模型层完全
commodity 化、推理需求无限增长、所有优化都针对自家硬件。

**Meta** 的利润池在广告和社交分发。它开放 Llama
权重是为了：抵消自身在闭源模型能力上落后 OpenAI 和 Anthropic
的劣势；让开源生态围绕自己的分发渠道构建；通过开源避免对任何单一模型供应商的依赖。但
Llama 4 的 benchmark 争议、LeCun 的出走、以及 Avocado
闭源项目的启动，显示 Meta 正在重新评估开放的成本收益。对 Meta 来说，三年
6000 亿美元的 AI
基建投入能否转化为可持续竞争优势，目前信号并不明朗。

**OpenAI 和 Anthropic** 的利润池在 API
差异化定价和订阅收入。它们选择旗舰模型权重闭源、选择性发表论文和安全研究。OpenAI
仍然选择性发表的原因是三个：维持学术声誉以招募研究者；通过技术论文引导行业方向（RLHF
范式就是 OpenAI 定义的）；以及维持 Sam Altman
长期塑造的欢迎竞争的公众形象。Anthropic
的策略更有意思：核心模型闭源，但在协议层积极开源（MCP），在安全研究上高调发表（Constitutional
AI、interpretability）。安全品牌是它 40% 企业市场份额的重要来源，而 6:1
的人才入出比（AI 行业最高）也部分得益于 interpretability
团队的学术影响力。Anthropic 的开放不在模型层，而在品牌和标准层。

**Google 和 DeepMind** 的利润池在搜索广告和云服务。Gemma
开放是为了在开发者社区保持存在感，防止生态完全被 Llama 和 Qwen
主导，同时用小模型培养开发者对 Google AI 技术栈的熟悉度。Gemini
旗舰闭源是因为它是 Google Cloud 差异化竞争的核心资产。AlphaFold
的模式又不同：开放基础科学工具和公共科学资产，闭源基于其构建的高价值商业化应用。Google
和 DeepMind
开放的不是最靠近利润池的层，而是能放大云平台、研究生态和行业标准影响力的层。

**中国开源玩家（DeepSeek、Qwen、MiniMax、Moonshot）**
的开放策略最为激进：模型权重完全开放，API 定价比美国闭源模型便宜 80% 到
95%（Kimi K2.5 的 input token 定价约 $0.60/M，Claude Opus 4.6 是
$5/M），同时积极融入全球推理框架获得原生支持。这套策略实现了三重目标：以
adoption 换取全球技术影响力（Qwen 在 HuggingFace 累计下载超 7
亿次，衍生模型占新增语言模型的 40% 以上）；以低价 API
吸引价格敏感的全球开发者（OpenRouter 2026 年 2 月 Top 5
调用量中四家来自中国，占比
85.7%）；以及通过部署层的扩散绕开训练环节的限制。这最后一点涉及中美竞争的关键不对称性，需要单独展开。

## 中美竞争：训练封锁与部署绕行的不对称博弈

2026 年 3 月，美中经济与安全审查委员会（USCC）发布了一份研究报告 Two
Loops: How China’s Open AI Strategy Reinforces Its Industrial
Dominance，提出了一个对中国 AI
从业者很值得关注的判断：美国正式把开源模型的分发能力、API
定价、框架兼容性和工业场景部署，当作一条独立的竞争维度来评估了。

这份报告的核心洞察在于一个政策盲区。美国芯片出口管制的设计逻辑建立在一个前提上：限制中国获取最先进芯片，就能限制其训练前沿模型的能力。这个逻辑在训练环节是有效的。但中国模型的全球扩散发生在部署环节，部署用的通常是蒸馏或量化后的小模型，对前沿芯片的依赖远低于预训练。出口管制对这条路径几乎没有着力点。

用更直接的话说：美国管得住训练，管不住部署。

这使得开放策略在中美竞争中有了超出商业逻辑的额外维度。中国公司通过激进开放权重、低价
API
和框架兼容性，在全球开发者生态中建立了一条与闭源前沿模型完全不同的竞争路径。Qwen
的衍生模型已经占 HuggingFace 上新增语言模型衍生的 40% 以上，超过了 Meta
Llama 的约 15%。当 Qwen 成为全球开发者的默认选择时，中国的模型架构、API
设计和推理优化方案就在事实上成为了行业标准的一部分。USCC 把这称为
alternative pathways to AI leadership：即使前沿能力上不是最强，通过
adoption 和标准渗透也能获得技术定义权。

这给美国公司制造了一个策略困境。如果继续封闭以保护前沿能力差距，全球开发者会加速转向中国开源替代品。如果选择开放以争夺开发者生态，又会加速模型商品化，压缩自身在闭源
API 上的利润空间。NVIDIA
的应对是这个困境中最清晰的一种：用模型无关的开源软件栈 +
多极模型生态，确保无论中美哪方的模型胜出，硬件层利润都归自己。

需要避免的是把这个竞争简化成单一维度的比赛。美国在 frontier training
和资本密度上仍然明显领先。中国在开源分发、低价
API、框架兼容和工业部署速度上有优势（67% 的中国工业企业已在生产中部署
AI，美国同类企业仅 34%）。但 adoption 层面的进展不等于全面领先，正如
benchmark
上的领先也不等于产业主导。真实的竞争图景是多维的，而中美各自的优势集中在不同维度上。

## 为什么这件事值得你关心

即使你不在大公司做战略决策，理解 AI
公司为什么公开和开源研究，也直接影响你作为 AI 从业者的日常判断。

首先，它影响你如何评估论文的商业含义。一篇强论文不等于发布方有了强护城河。如果发布方的利润池不在模型层，论文公开可能恰恰是在加速模型
commodity
化来利好自己的互补资产。看到一个新的训练效率突破被公开发表时，值得问一句：这家公司是在放弃优势，还是在定向压缩对手的差异化空间？

其次，它影响你如何理解公司的真实优势。很多时候，一家公司最强的资产不在模型权重里，而在算力规模、工程执行节奏、客户关系深度、分发渠道控制力、数据飞轮质量这些论文里看不到的地方。Anthropic
40% 的企业市场份额不是靠 Claude 的 benchmark 分数拿到的，是靠 safety
品牌、企业工具链和合规叙事建立的。

第三，它影响你的职业判断。当模型能力本身在快速 commodity 化（GPT-4
等效推理成本三年下降了约 50
倍）的时候，纯粹的模型研究能力在价值链中的位置在变化。系统架构设计、Agent
编排、质量评估、产品集成、企业部署、标准制定——这些能力在利润链中的权重在上升。这不是说研究不重要了，而是说从研究到
shipping 的全链路能力变得更稀缺了。

第四，它给你提供了一个判断框架。当你看到一家公司宣布开源或闭源某项技术时，可以问三个问题：这家公司的利润池在哪一层？被开放的这一层和利润池是同一层还是互补层？开放之后，shipping
friction
会降低多少，谁会因此受益？如果开放的是互补层而利润池在别处，那这个开放行为大概率是理性的竞争策略。如果开放的是利润池本身所在的层，那要么是这个层的护城河已经守不住了，要么是公司在做更大的战略赌注。

最后一个判断也是最宏观的：这些开放策略不是静态的。Meta 从开源先锋转向
Avocado 闭源，Anthropic 从闭源模型公司转向 MCP 开源，DeepSeek
从学术实验室转向全球开发者生态的争夺者。公司的开放边界随竞争格局和利润池变化持续调整。给任何一家公司贴上一个固定的开放或封闭标签，过几个月大概率就过时了。真正有用的不是记住谁开放了什么，而是理解这背后的利益机制，然后持续跟踪边界的移动。

---

## 参考来源

**一手报告与官方声明**

- USCC, *Two Loops: How China’s Open AI Strategy Reinforces Its
  Industrial Dominance*, 2026-03-23
- Mark Zuckerberg, *Open Source AI is the Path Forward*,
  2024
- NVIDIA GTC 2026 keynote, Jensen Huang 关于推理时代与 Dynamo
  的表述

**行业分析**

- Joel Spolsky, *Strategy Letter V: The Economics of Open
  Source*
- Long Yield Substack, *The AI Profit Map: Why the Biggest Winners
  Aren’t Who You Think*（利润池三阶段迁移模型）
- Jessica Leao Substack, *AI Predictions for 2026*（MCP
  标准化、Meta 闭源转向）
- MIT Technology Review, *What’s next for Chinese open-source
  AI*, 2026-02-12

**Adoption 与竞争数据**

- 新华社, Alibaba’s Qwen leads global open-source AI community with
  700M downloads, 2026-01-13
- CGTN, Chinese AI models overtake U.S. rivals in global token usage,
  2026-02-28
- 36Kr, February Sees Surge in AI Usage: China’s AI Call Volume
  Overtakes US, 2026-02
- nxcode.io, Kimi K2.5 Pricing 2026; LLM Benchmark 2026, 38 Actual
  Tasks, 15 Models

**人才流动**

- LinkedIn OC Insights, What 2025 Revealed About the Future of AI
  Talent（Anthropic 入出比 6:1, OpenAI 3.6:1）
- CNBC, LeCun 离职报道; Bloomberg, AMI Labs $1.03B seed round

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
