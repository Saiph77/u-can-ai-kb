---
title: "NVIDIA GTC\n2026：黄仁勋在卖什么，以及他没说的那些事"
date: 2026-03-17
source: https://yage.ai/share/nvidia-gtc-2026-survey-20260317.html
slug: nvidia-gtc-2026-survey-20260317
lang: zh
---
# NVIDIA GTC 2026：黄仁勋在卖什么，以及他没说的那些事

发布于 2026 年 3 月 17 日 · [查看原网页](https://yage.ai/share/nvidia-gtc-2026-survey-20260317.html)

> 黄仁勋卖的不是某个模型，而是把模型层商品化后的整套 AI 基础设施。 GTC
> 2026 的核心信号是，推理系统、沙箱执行和 agent
> 运行时开始比单纯训练更重要。 NVIDIA 想占住的是所有 Agent
> 都绕不开的生产线位置。

来源：Jensen Huang GTC 2026 Keynote（2026-03-16，San
Jose），多源交叉调研 视角：面向每天构建 Agentic AI 系统的实践者（Claude
Code / LangChain / Multi-agent 编排）

---

## 一句话

GTC 2026 的表层叙事是训练时代结束、推理时代开始。底层逻辑是 NVIDIA
通过一套开放生态设计，把模型层变成可替换的
commodity，把自己锚定为唯一的基础设施供应商。

## 黄仁勋嘴上说的 vs 实际做的

黄仁勋花了两个多小时构建一个完整论证：数据中心正在从文件仓库变成
Token 工厂，核心度量从存储和带宽变成了每瓦特产出多少 Token。他把
OpenClaw（一个第三方开源 Agent 框架）比作 Linux，预测每家 SaaS 都会变成
AaaS（Agent-as-a-Service），工程师未来的 offer 里会写明年度 Token
预算。

把这些声明放回决策空间里，战略意图就很清楚了。

Token
工厂这个比喻有明确的战略考量。工厂生产的是标准化、按量计价的工业品。在这个框架下，GPT-5
和 Claude 4
变成了流水线上的配方。配方当然重要，但垄断了生产线的人拿走最大的利润。黄仁勋通过一个看似中性的经济学比喻，把模型层定义成了供应链中的可替换环节：谁能最低成本、最高效率地生产
Token，谁就赢。这个角色只有 NVIDIA 能扮演。

把 OpenClaw 比作 Linux 是同一个逻辑的延伸。OpenAI
的路径是用封闭模型和 API 构建封闭生态。NVIDIA 拥抱 OpenClaw
这个模型无关的编排层，目标是让 Agent
框架层免费化、开源化。当应用都跑在免费的 OpenClaw
上，底层模型变成可插拔的 API，剩下唯一有定价权的就是硬件和推理栈。这和
Google 对 Android 的策略一致。

## 五个关键决策的逆向工程

理解 NVIDIA 做了什么，先要理解他们面前有哪些路可以选。GTC 2026
的公告背后至少有五个关键决策点，每个点上都存在截然不同的路径。

### 决策一：推理基础设施的抽象层级

NVIDIA 可以只卖芯片（纯硬件商），可以做完整的推理云服务（对标 AWS
Bedrock），也可以做中间层：一个开源的推理操作系统。他们选了中间层，就是
Dynamo 1.0。

约束逻辑：做云服务会和 AWS、Azure、GCP 正面竞争，而这些是 NVIDIA
最大的客户（前五大超算厂商占收入的
60%）。只卖芯片的话，软件优化的红利全归云厂商，NVIDIA
变成纯粹的零部件供应商。中间层是唯一能两头获利的位置。Dynamo
开源，理论上谁都能用，但 disaggregated serving、KV cache pinning
的最优实现深度依赖 NVLink 带宽、HBM4 内存层级和 GPU
间通信拓扑。开源的代码，绑定的硬件。和 Android 的 AOSP 开源、Google Play
Services 闭源是同一种模式。

放弃了什么：直接的软件收入。Dynamo 闭源的话可以像 VMware 一样卖
license。NVIDIA 判断推理 OS 的网络效应比软件收入更值钱：所有人用
Dynamo，优化都针对 NVIDIA 硬件，买 NVIDIA 的理由更充分。

### 决策二：模型策略

NVIDIA 拥有最多的 GPU，有能力训练顶级模型，但选择了够用就好。Nemotron
3 Super 是 120B 总参 / 12B 活跃的 MoE，SWE-Bench
60.47%。官方推荐的部署模式本身就说明了定位：简单任务 Nano，规划用
Super，难题用闭源前沿模型。

约束冲突的核心：平台方进入模型层会直接威胁客户关系。如果 NVIDIA
训练出一个超越 Claude 的模型，Anthropic 会认真评估 AMD 和 Google
TPU，因为硬件供应商变成了直接竞争对手。Nemotron 的 120B/12B MoE
设计说明优化目标是推理效率（在自家硬件上跑得快），模型能力本身是次要的。60.47%
的 SWE-Bench 分数足以证明开源模型在 NVIDIA 硬件上可用，同时和
Claude、GPT-5 保持安全距离。

真实优先级排序：保住硬件垄断 > 进入模型市场。

### 决策三：Agent 运行时的所有权

NVIDIA 可以自建 Agent 框架（对标
LangChain），可以收购现有框架，也可以拥抱社区项目后加安全层。他们选了第三条：在
OpenClaw 上盖了一层 NemoClaw（OpenShell 沙箱 + Privacy Router + Agent
Toolkit）。

Agent 框架的竞争已经很激烈，自建框架会同时得罪
LangChain、CrewAI、AutoGen
等所有玩家。拥抱社区项目再加企业安全层，政治上安全。Linux
成功的关键在于没有一家公司拥有它，Red Hat
通过在上面加企业功能来赚钱。NemoClaw 是同一种策略。

值得关注的隐藏权力位置：Privacy
Router。这个路由器决定哪些请求发给本地 Nemotron 模型，哪些发给云端
Claude 或
GPT。表面上是隐私功能，实际上是流量调度器。控制路由逻辑的人控制模型提供商的流量分配，和
Safari 默认搜索引擎的逻辑相同：Google 每年付 Apple
几百亿美元保持默认地位，因为默认路由就是定价权。NVIDIA 目前对 Privacy
Router 的默认行为、开源程度、路由策略可配置性都没有明确说明。

NemoClaw 目前是 early alpha，NVIDIA 自己的描述是 expect rough
edges。

### 决策四：CPU 的定位

Vera CPU 可以做通用服务器 CPU（正面对抗 EPYC/Xeon），也可以做 GPU
的附属协处理器，还可以做特定工作负载的专用处理器。NVIDIA
选了最窄的路：88 个 Arm Olympus 核心，专门为 Agent 沙箱优化，单机架
22,500 个并发沙箱。

这个选择隐含了一个明确的技术判断：Agentic AI 的瓶颈正在从 GPU
推理转向 CPU 侧的沙箱执行。Amdahl 定律在起作用：GPU 处理 Token
生成高效，但 Agent 的大量操作是 CPU
密集的串行任务（在沙箱里编译代码、跑浏览器、查数据库、执行 API
调用）。这和日常使用 Claude Code 的体验一致：模型回复可能 2-3 秒，等
bash 命令执行完、测试跑完、linter 返回结果经常要 10-30 秒。在
multi-agent 系统中，每个 agent
需要自己的隔离执行环境，问题指数级放大。

放弃了什么：通用服务器 CPU 的市场。AMD EPYC 在数据中心 CPU
市场份额还在增长，NVIDIA
本可以去争。选择专用化意味着可寻址市场小得多，但在 agent sandbox
这个细分上独占。

### 决策五：生态联盟的结构

Nemotron Coalition
的成员名单值得展开看：Mistral（法国）、Sarvam（印度）、Thinking Machines
Lab（Mira Murati 的新公司，前 OpenAI CTO）、Reflection
AI、Cursor、LangChain、Perplexity、Black Forest Labs。

从地缘视角看，这个名单很有策略性。成员覆盖了欧洲的数字主权诉求（Mistral），印度的本土模型需求（Sarvam），硅谷从
OpenAI 独立出来的团队（Thinking Machines、Reflection）。NVIDIA
作为全球最大的 AI
硬件供应商，利益最大化的前提是模型层保持多极竞争。如果任何一家模型公司统一了市场，NVIDIA
的议价权就会下降。支持全球各方竞争者、确保模型层持续分裂，对 NVIDIA
是最优策略。

第一个项目是 Mistral + NVIDIA 联合开发基础模型，将成为 Nemotron 4
的基础。Cursor 贡献编码场景的真实评估数据，LangChain 构建 agent harness
和可观测性，Perplexity 贡献搜索和推理的生产经验。每个成员都在为 NVIDIA
的硬件生态提供差异化的应用层价值。

## 三个反共识观点

### Dynamo 的 7 倍提升意味着什么

黄仁勋宣布，仅通过软件优化（disaggregated serving + KV cache
pinning）就能在现有 Blackwell 硬件上实现 7 倍性能提升。

这个数字的另一面：如果纯软件优化能带来 7
倍提升，过去几年行业大量采购的 GPU 真实利用率可能只有 15%
左右。过去两年的算力紧张，至少有一部分是粗放的系统架构和缺乏推理层优化导致的。GPU
确实紧缺，但紧缺的程度被放大了。

这也意味着未来的性能红利来源在变。从无脑堆硬件转向对显存带宽和路由的系统级优化。对
AI 实践者来说，理解 Dynamo 的 disaggregated serving 架构（把
encode、prefill、decode 拆到独立 worker
上）的操作价值可能比升级硬件更高。

需要注意 7 倍数字的具体语境：GB200 NVL72 上跑 DeepSeek
R1-0528（FP4），1k/1k 输入输出，目标交互速度约 50
tok/sec/user。其他基准上的提升从 1.5 倍到 4 倍不等，最大收益出现在 MoE
模型和有 KV cache 复用的场景。

### 谁受影响最大

每次平台转移都重新分配价值。如果 NVIDIA 的愿景实现，除了 AMD 和 Intel
之外，更值得关注的是两个方向。

第一是云服务商。当 Dynamo 成为推理 OS，NemoClaw 的 Privacy Router
能在本地沙箱和云端之间智能调度，云厂商的增值服务层（managed
inference、model hosting）会被压缩。CNBC 的分析也指出，NVIDIA 正在试图从
GPU 供应商扩展到整个 AI
工厂的全栈供应商：计算、网络、存储、推理软件、Agent、机器人。这个全栈野心直接挤压了云厂商的价值空间。

第二是 Meta 的 Llama。Nemotron Coalition 对 Anthropic 和 OpenAI
的影响有限，因为后者的护城河在模型能力而非推理效率。但对 Llama
的冲击是实质性的。如果 Nemotron 4 在 NVIDIA 硬件上的推理效率显著优于
Llama，选开源模型的用户会倾向于选 Nemotron，因为大多数人的推理硬件就是
NVIDIA GPU。NVIDIA
正在从「所有开源模型在我们硬件上都跑得好」转向「我们自己的开源模型在我们硬件上跑得最好」。

### 沉默比声音信息量更大

整场发布会，黄仁勋几乎没有提 AGI，也没有谈 Scaling Law
的下一个里程碑。相反，他花大量时间在 Uber 无人车、Disney
机器人和工业软件上。

这个选择反映了一个判断：单纯扩大模型参数的边际收益在递减。为了支撑
2027 年那 1
万亿美元的基础设施需求，叙事重心必须从「创造更强的模型」转向「用现有模型创造经济价值」。AaaS
的现金流比 AGI 的愿景对估值更有支撑力。

另一个信号：如果 pre-training scaling
仍然是主旋律，「训练时代结束」这个说法就站不住。黄仁勋之所以可以自信地宣布进入推理时代，背后的假设是训练的边际收益已经足够平缓，推理的优化空间成为了更大的价值来源。这个叙事对
NVIDIA 有利：推理是 always-on 的持续消费，训练是一次性投入。推理时代 =
硬件持续采购。

## 硬件事实速览

Vera Rubin 平台：7 芯片 5 机架。核心芯片 Rubin GPU（336B 晶体管，TSMC
N3，288GB HBM4，22 TB/s 带宽，50 PFLOPS FP4）。相比 Blackwell：推理 5
倍，训练 3.5 倍，能效 10 倍，Token 成本 1/10。一个 NVL72 机架装 72 颗
Rubin GPU + 36 颗 Vera CPU，内部互联 260 TB/s。2026 下半年出货。Azure
已在运行首台，Satya Nadella 确认。

Vera CPU：88 个 Olympus 核心（Arm v9.2），1.5TB LPDDR5X，1.2 TB/s
带宽。单机架 256 颗 CPU，22,500+ 并发沙箱。比 x86 方案密度高 4
倍，能效高 2 倍。

Dynamo 1.0：开源分布式推理
OS（github.com/ai-dynamo/dynamo）。核心能力：disaggregated
encode/prefill/decode，KV cache pinning，agent hints routing，NIXL 快速
GPU 间数据搬运。已集成 vLLM、SGLang、TensorRT-LLM。Kubernetes
原生部署（AWS EKS、Azure AKS、GKE、OCI）。

Nemotron 3 Super：120B 总参 / 12B 活跃（MoE），100 万 Token
上下文，Hybrid Mamba-Transformer。SWE-Bench Verified 60.47%，PinchBench
85.6%（OpenClaw Agent 场景最佳开放模型），RULER 1M 91.75%。吞吐量比
GPT-OSS-120B 高 2.2 倍。开放权重、训练数据、recipe 和评估管线。

NemoClaw：Early alpha 状态。OpenShell 沙箱 + Privacy Router + Agent
Toolkit。一条命令部署。支持 GeForce RTX、DGX、云端。与 OpenClaw 创始人
Peter Steinberger 共同开发。

## 其他公告

Nemotron 3 系列还包括
Ultra（旗舰级）、Omni（多模态）、VoiceChat（实时语音）、Nano（边缘）。

Physical AI：Uber robotaxi 2027 年湾区/洛杉矶上路，计划 2028
年覆盖四大洲 28 城。Disney 的 Olaf 机器人（用 Newton 物理引擎 + Isaac
Lab 训练）在台上与 Jensen 同行。Cosmos 3
统一了合成世界生成、视觉推理和动作仿真。GR00T N2
预览版在新任务新环境上性能比领先 VLA 模型高 2 倍以上。

工业软件：Cadence、Dassault、PTC、Siemens、Synopsys 集成 CUDA-X 和
Omniverse。Honda 气动仿真 34 倍加速，Samsung/SK hynix 用 GPU
加速光刻。NVIDIA 正在从 AI 芯片供应商扩展到物理制造的计算基底。

DLSS 5：2026 秋季发布，重心从帧率提升转向视觉保真度。AI
增强纹理、光照和环境细节。

Vera Rubin Space-1：面向近地轨道的计算平台，合作伙伴 Axiom
Space、Starcloud、Planet Labs。

Feynman 架构路线图预览：Vera Rubin 之后的下一代，包括新 GPU、LP40
LPU、Rosa CPU（以 Rosalind Franklin 命名）。

## 市场反应

93% 的分析师评级买入，平均目标价约 267 美元（45%+ 上行空间），但
keynote 当天股价先涨 4.3% 后回落，收盘跌 0.70% 至 181.93 美元。

CNBC
的分析认为根源在市场结构：期权对冲活动和做市商操作把股价钉在了当前水平。Bernstein
认为以 2027 年 EPS 10.68 美元计算，17 倍 PE 已经很便宜。Stifel
的评价更精确：1 万亿美元的数字 validated rather than raised
现有预期。所有人都已经知道 NVIDIA 会很好，GTC
提供的是确认而非增量信息。

更深层的宏观张力：伊朗石油危机推高能源价格，AI
牛市需要稳定的经济环境、低成本数据中心用电和降息预期。这两个力量方向相反，市场在等矛盾解决。

## 对构建 Agentic AI 的人意味着什么

瓶颈在移动。Vera CPU 的存在是一个硬件级信号：NVIDIA
花真金白银解决的问题是工具执行和沙箱管理的效率，而非模型推理速度。如果你在设计
agent
架构，精力分配应该更多转向高效的工具调用模式和沙箱生命周期管理。当前基于
Docker 容器的 agent sandbox 方案（包括 Claude Code 的
sandbox）可能需要根本性重设计。22,500 并发沙箱暗示的模式更接近
serverless function（几秒创建、执行、销毁），而非长期运行的容器。

推理栈在变厚。Dynamo 的 disaggregated serving
意味着推理已经变成分布式系统问题。encode、prefill、decode 在不同 worker
上执行，KV cache 跨请求复用，路由根据 agent hints 动态调整。对
multi-agent 系统的设计有直接影响：KV cache pinning 意味着多轮 agent
应该保持 session affinity，而非每次随机路由。

Super + Nano + 前沿模型的分层模式值得立即尝试。Nemotron 3 Super 的
SWE-Bench 60.47% 和 100 万 Token
上下文，足以处理大部分结构化编码和规划任务。简单请求路由到
Nano、中等复杂度走 Super、极端场景调用
Claude/GPT，理论上可以把推理成本砍半以上。前提是路由逻辑足够聪明，这本身就是一个有趣的工程问题。

NVIDIA 生态的锁定正在加深，但目前拥抱仍然是理性选择。推理栈建立在
Dynamo + NVIDIA GPU 上时，迁移成本会越来越高。但替代方案（AMD
软件栈、Google TPU 的开放度）尚未成熟。务实的做法是拥抱 NVIDIA
生态获取性能优势，同时在架构中保留推理后端的抽象层，为未来迁移留余地。

关注 OpenClaw 的真实采用曲线。Jensen 的 Linux 类比很大胆，但 OpenClaw
要成为行业标准需要的是生态优势：足够的工具、集成、教程和社区支持，让不使用
OpenClaw 变成需要理由的选择。目前 NemoClaw 还是 early alpha。比起 NVIDIA
说了什么，更值得跟踪的是 OpenClaw 的 GitHub star 增长和 PR 活跃度。

---

*本报告综合了 NVIDIA 官方新闻稿、开发者博客、SemiAnalysis
InferenceX 基准、CNBC/Sherwood News/Seeking Alpha
市场分析、Latent.Space/The Decoder 技术分析、Tom’s Hardware
硬件评测等多源信息，经交叉验证后撰写。*

## 鸭哥每日手记

日更的深度AI新闻和分析

订阅

[Built with Kit](https://kit.com/features/forms?utm_campaign=poweredby&utm_content=form&utm_medium=referral&utm_source=dynamic)

本文 100% 由 AI 生成
·
Superlinear Academy

[3,000+ AI Builder 在这里交流实战经验 · 加入社区
→](https://go.ai-builders.com/yage)
